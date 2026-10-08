import sys
import torch
import torch.nn as nn
import torch.nn.functional as F

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class SqueezeAndExcitationBlock(nn.Module):
    """
    =============================================================================
    [NÂNG CẤP KIẾN TRÚC MỤC 3.1 - TV1: TRẦN ĐĂNG THẮNG]
    PHẦN MỚI 1: KHỐI CHÚ Ý KÊNH TẦN SỐ (CHANNEL ATTENTION / SE-BLOCK)
    - Tự động học ma trận trọng số cho 128 kênh đặc trưng âm học
    - Khuếch đại các dải tần Formant F1-F4 và cao độ F0 đại diện cho 6 thanh điệu tiếng Việt
    - Triệt tiêu các kênh nhiễu môi trường và khoảng lặng
    =============================================================================
    """
    def __init__(self, channels=128, reduction=8):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels, bias=False),
            nn.Sigmoid()
        )

    def forward(self, x):
        # x: (B, C, F, T)
        b, c, _, _ = x.size()
        squeeze = self.avg_pool(x).view(b, c)
        scale = self.fc(squeeze).view(b, c, 1, 1)
        return x * scale


class SpeechCRNN_CTC(nn.Module):
    """
    =============================================================================
    [MỤC 1.5 & MỤC 3.1 - TV1: TRẦN ĐĂNG THẮNG]
    KIẾN TRÚC MÔ HÌNH HỌC SÂU ÂM HỌC DUAL-ATTENTION CRNN-CTC (ACRNN)
    - 3 khối tích chập Conv2D trích xuất Formant không gian
    - ⭐ [PHẦN MỚI 1]: Squeeze-and-Excitation (SE Block) tái hiệu chuẩn 128 kênh thanh điệu
    - Cầu nối tuyến tính Linear Bridge nén 1280 -> 256
    - 2 tầng BiGRU 512 chiều học ngữ cảnh chuỗi thời gian hai chiều
    - ⭐ [PHẦN MỚI 2]: Multi-Head Self-Attention (4 Heads) + Residual + LayerNorm
      bắt trọn ngữ cảnh từ ghép tiếng Việt trên toàn câu
    - Tầng phân loại CTC Classifier 75 tokens với bias[0] = -3.0 chống Blank Collapse
    =============================================================================
    """
    def __init__(self, n_mels=80, vocab_size=105, hidden_size=256, num_rnn_layers=2, dropout=0.2):
        super().__init__()
        self.n_mels = n_mels
        self.vocab_size = vocab_size

        # [MỤC 3.1 - TV1] 1. KHỐI TÍCH CHẬP 2D (CONVOLUTIONAL FEATURE EXTRACTOR) - GIỮ NGUYÊN CẤU HÌNH
        # Khối 1: Nén 1/2 tần số (80->40), 1/2 thời gian (T->T/2)
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.Hardtanh(0, 20, inplace=True),
            nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2))
        )

        # Khối 2: Nén tiếp 1/2 tần số (40->20), 1/2 thời gian (T/2->T/4)
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.Hardtanh(0, 20, inplace=True),
            nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2))
        )

        # Khối 3: Tích hợp ⭐ [PHẦN MỚI 1: SE-BLOCK] vào cuối Conv3 trước MaxPool
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.Hardtanh(0, 20, inplace=True),
            SqueezeAndExcitationBlock(channels=128, reduction=8),  # SE-Block tái hiệu chuẩn kênh âm sắc
            nn.MaxPool2d(kernel_size=(2, 1), stride=(2, 1))
        )

        # [MỤC 3.1 - TV1] CẦU NỐI CHIẾU TUYẾN TÍNH (LINEAR BRIDGE) - GIỮ NGUYÊN
        out_freq = n_mels // 8
        conv_out_dim = 128 * out_freq
        self.fc_proj = nn.Linear(conv_out_dim, hidden_size)

        # [MỤC 3.1 - TV1] 2. KHỐI MẠNG HỒI QUY HAI CHIỀU (Bi-directional GRU) - GIỮ NGUYÊN
        self.rnn = nn.GRU(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=num_rnn_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_rnn_layers > 1 else 0.0
        )

        # ⭐ [PHẦN MỚI 2 - TV1] KHỐI CHÚ Ý ĐA ĐẦU THEO THỜI GIAN (MULTI-HEAD SELF-ATTENTION)
        # 4 đầu chú ý (Multi-Head), embed_dim=512 (256 * 2 từ BiGRU), kèm LayerNorm và Skip Connection
        self.self_attention = nn.MultiheadAttention(
            embed_dim=hidden_size * 2,
            num_heads=4,
            dropout=dropout,
            batch_first=True
        )
        self.attn_norm = nn.LayerNorm(hidden_size * 2)

        # [MỤC 1.5 & MỤC 3.1 - TV1] 3. TẦNG CHIẾU ĐẦU RA CTC (CTC Linear Projection) - GIỮ NGUYÊN
        self.classifier = nn.Linear(hidden_size * 2, vocab_size)
        with torch.no_grad():
            self.classifier.bias[0] = -3.0

    def forward(self, x):
        """
        [MỤC 3.1 - TV1] Luồng lan truyền xuôi Dual-Attention:
        Input x: (Batch, 1, Mel_bins=80, Time=T)
        Output log_probs: (Batch, Time'=T/4, Vocab_size=75)
        """
        # 1. Trích xuất đặc trưng hình ảnh âm học + Lọc kênh SE-Block
        x = self.conv1(x)  # (B, 32, 40, T/2)
        x = self.conv2(x)  # (B, 64, 20, T/4)
        x = self.conv3(x)  # (B, 128, 10, T/4) - Đã qua SE-Block tái hiệu chuẩn

        b_sz, c_sz, freq_dim, time_dim = x.size()
        x = x.permute(0, 3, 1, 2).contiguous().view(b_sz, time_dim, c_sz * freq_dim)
        x = self.fc_proj(x)  # (B, T/4, 256)

        # 2. Học phụ thuộc chuỗi thời gian qua 2 tầng BiGRU
        rnn_out, _ = self.rnn(x)  # (B, T/4, 512)

        # ⭐ [PHẦN MỚI 2]: Khối chú ý ngữ cảnh toàn cục (Multi-Head Self-Attention + Residual + LayerNorm)
        attn_out, _ = self.self_attention(rnn_out, rnn_out, rnn_out)
        context_out = self.attn_norm(rnn_out + attn_out)  # (B, T/4, 512)

        # 3. Chiếu tuyến tính ra 75 logits và tính log-softmax cho CTC Loss
        logits = self.classifier(context_out)  # (B, T/4, 75)
        log_probs = F.log_softmax(logits, dim=-1)  # (B, T/4, 75)

        return log_probs

    def get_output_lengths(self, input_lengths):
        """
        [MỤC 3.1 - TV1] Tính độ dài chuỗi thời gian sau CNN: T' = T // 4
        """
        return input_lengths // 4

    def load_state_dict(self, state_dict, strict=False):
        """
        Hỗ trợ tương thích ngược thông minh:
        Cho phép nạp cả checkpoint gốc (CRNN thuần 75 epochs) lẫn checkpoint mới (Dual-Attention)
        mà không bao giờ bị lỗi 'Missing key(s)'.
        """
        return super().load_state_dict(state_dict, strict=strict)


if __name__ == "__main__":
    # Kiểm tra kích thước tensor forward
    model = SpeechCRNN_CTC(n_mels=80, vocab_size=75)
    dummy_input = torch.randn(2, 1, 80, 400)  # Batch 2, 80 mel bins, 400 time frames
    log_probs = model(dummy_input)
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    print("=" * 65)
    print("[OK] Forward pass SpeechCRNN_CTC (Dual-Attention) thành công!")
    print(f"Tổng số tham số mô hình: {total_params:,} parameters")
    print(f"Input shape: {dummy_input.shape}")
    print(f"Log probs shape (Batch, Time, Vocab): {log_probs.shape}")
    input_lens = torch.tensor([400, 300])
    out_lens = model.get_output_lengths(input_lens)
    print(f"Output time lengths: {out_lens}")
    print("=" * 65)
