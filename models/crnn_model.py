import torch
import torch.nn as nn
import torch.nn.functional as F

class SpeechCRNN_CTC(nn.Module):
    """
    Mô hình Mạng Nơ-ron Tích chập Hồi quy cho Nhận dạng Tiếng nói Chuỗi dài Tiếng Việt
    (CRNN: CNN Feature Extractor + BiGRU Context Modeler + CTC Output Layer).
    
    Phù hợp chuẩn giáo trình:
    - Slide 01c: Trích xuất đặc trưng phổ họa âm thanh (Log Mel-Spectrogram)
    - Slide 2b: Kiến trúc CRNN & Hàm mất mát CTC Loss cho dữ liệu chuỗi thời gian không đồng bộ
    """
    def __init__(self, n_mels=80, vocab_size=75, hidden_size=256, num_rnn_layers=2, dropout=0.2):
        super().__init__()
        self.n_mels = n_mels
        self.vocab_size = vocab_size

        # 1. Khối tích chập 2D (Convolutional Feature Extractor)
        # Khối 1: Giảm 1/2 tần số, 1/2 thời gian
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.Hardtanh(0, 20, inplace=True),
            nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2))
        )

        # Khối 2: Giảm tiếp 1/2 tần số, 1/2 thời gian
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.Hardtanh(0, 20, inplace=True),
            nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2))
        )

        # Khối 3: Giảm 1/2 tần số, GIỮ NGUYÊN trục thời gian để đảm bảo độ phân giải âm vị CTC
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.Hardtanh(0, 20, inplace=True),
            nn.MaxPool2d(kernel_size=(2, 1), stride=(2, 1))
        )

        # Kích thước tần số sau 3 khối: n_mels (80) -> 40 -> 20 -> 10
        out_freq = n_mels // 8
        conv_out_dim = 128 * out_freq

        # Chiếu về kích thước ẩn cho RNN
        self.fc_proj = nn.Linear(conv_out_dim, hidden_size)

        # 2. Khối mạng Hồi quy Hai chiều (Bi-directional GRU)
        self.rnn = nn.GRU(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=num_rnn_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_rnn_layers > 1 else 0.0
        )

        # 3. Tầng chiếu đầu ra CTC (CTC Linear Projection)
        # BiGRU cho ra vector kích thước hidden_size * 2 = 512
        self.classifier = nn.Linear(hidden_size * 2, vocab_size)
        # Khởi tạo bias âm cho token blank (token 0) để chống hiện tượng sụp đổ cực tiểu Blank (Blank Collapse)
        with torch.no_grad():
            self.classifier.bias[0] = -3.0

    def forward(self, x):
        """
        Input x: (Batch, 1, Mel_bins, Time)
        Output log_probs: (Batch, Time', Vocab_size)
        """
        # 1. Trích xuất đặc trưng qua CNN
        x = self.conv1(x)  # (B, 32, F/2, T/2)
        x = self.conv2(x)  # (B, 64, F/4, T/4)
        x = self.conv3(x)  # (B, 128, F/8, T/4)

        b_sz, c_sz, freq_dim, time_dim = x.size()
        # Biến đổi chiều để đưa vào RNN: gộp Channel và Freq thành feature vector
        # (B, C, F, T) -> (B, T, C * F)
        x = x.permute(0, 3, 1, 2).contiguous().view(b_sz, time_dim, c_sz * freq_dim)
        x = self.fc_proj(x)  # (B, T, hidden_size)

        # 2. Xử lý chuỗi thời gian qua BiGRU
        rnn_out, _ = self.rnn(x)  # (B, T, hidden_size * 2)

        # 3. Tính logits và log-probabilities cho CTC
        logits = self.classifier(rnn_out)  # (B, T, vocab_size)
        log_probs = F.log_softmax(logits, dim=-1)  # (B, T, vocab_size)

        return log_probs

    def get_output_lengths(self, input_lengths):
        """
        Tính toán độ dài chuỗi thời gian sau khi đi qua các tầng tích chập MaxPool.
        Do khối 1 giảm 2, khối 2 giảm 2, khối 3 giữ nguyên trục thời gian -> T' = T // 4
        """
        return input_lengths // 4

if __name__ == "__main__":
    # Kiểm tra kích thước tensor forward
    model = SpeechCRNN_CTC(n_mels=80, vocab_size=75)
    dummy_input = torch.randn(2, 1, 80, 400)  # Batch 2, 80 mel bins, 400 time frames
    log_probs = model(dummy_input)
    print("[OK] Forward pass thanh cong!")
    print(f"Input shape: {dummy_input.shape}")
    print(f"Log probs shape (Batch, Time, Vocab): {log_probs.shape}")
    input_lens = torch.tensor([400, 300])
    out_lens = model.get_output_lengths(input_lens)
    print(f"Output time lengths: {out_lens}")
