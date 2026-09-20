"""
Script tự động vẽ sơ đồ kiến trúc Pipeline tổng thể 5 giai đoạn
Nâng cấp: Ghi rõ ràng, chính xác thứ tự thực thi từng bước (BƯỚC 1 -> BƯỚC 5),
trích dẫn cụ thể các đoạn code Python tương ứng, và đặc tả chi tiết giao diện
kết nối (RETURN của tầng trước -> INPUT của tầng sau: tên biến, kiểu dữ liệu, tensor shape).
Đồ án Xử lý tiếng nói - GVHD: Thầy Phù Khắc Anh (HCMUTE)
"""
import os
import sys
import shutil

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Cấu hình phông chữ hỗ trợ tiếng Việt và ký tự chuẩn trên Windows
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial', 'Tahoma']

def draw_pipeline():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(project_dir, "docs", "pipeline_tong_the.png")

    # Kích thước khung vẽ siêu nét (19 x 32.5 inches, DPI 220 -> 4180 x 7150 pixels)
    fig, ax = plt.subplots(figsize=(19, 32.5), dpi=220)
    fig.patch.set_facecolor("#080D14")
    ax.set_facecolor("#080D14")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Bảng màu High-tech Cyberpunk Dark Mode chuyên nghiệp
    c_card_bg = "#0F172A"
    c_card_border_dim = "#1E293B"
    c_cyan = "#00E5FF"
    c_green = "#00E676"
    c_purple = "#B388FF"
    c_orange = "#FF9100"
    c_pink = "#FF4081"
    c_yellow = "#FDE047"
    c_code_bg = "#162032"
    c_connector_bg = "#09121D"

    # ==================== 1. BANNER TIÊU ĐỀ TỔNG THỂ ====================
    title_box = patches.FancyBboxPatch(
        (3, 94.2), 94, 5.0, boxstyle="round,pad=0.5,rounding_size=0.8",
        linewidth=2.5, edgecolor=c_cyan, facecolor="#0E1B2E"
    )
    ax.add_patch(title_box)

    ax.text(50, 97.4, "SƠ ĐỒ KIẾN TRÚC PIPELINE BACKEND CHI TIẾT & GIAO DIỆN DỮ LIỆU TỪNG TẦNG",
            fontsize=17, fontweight="bold", color="#00E5FF", ha="center", va="center")
    ax.text(50, 95.8, "Môn học: Xử lý tiếng nói (Speech Processing) — Giảng viên hướng dẫn: Thầy Phù Khắc Anh (HCMUTE)",
            fontsize=12.2, fontweight="bold", color="#E2E8F0", ha="center", va="center")
    ax.text(50, 94.6, "Thứ tự tuần tự các bước xử lý, Trích xuất Code thực thi và Cầu nối truyền nhận (RETURN -> INPUT Tensor)",
            fontsize=10.5, fontstyle="italic", color="#94A3B8", ha="center", va="center")

    # ==================== CẤU TRÚC 5 GIAI ĐOẠN ====================
    stages = [
        # ---------- GIAI ĐOẠN 1 ----------
        {
            "num": "GIAI ĐOẠN 1",
            "title": "THU ÂM & GIAO TIẾP PHẦN CỨNG (AUDIO INGESTION)",
            "file": "controllers/audio_controller.py",
            "y": 80.8, "height": 12.2,
            "border": c_cyan,
            "badge_color": "#0077B6",
            "steps": [
                ("BƯỚC 1.1: Thăm dò & Chọn thiết bị",
                 "sd.check_input_settings(device=dev_id, samplerate=48000)",
                 "Tự động quét HostAPI DirectSound/MME; cách ly Stereo Mix khi người dùng chọn Micro laptop hoặc Tai nghe jack 3.5mm."),
                ("BƯỚC 1.2: Mở luồng ngắt phần cứng",
                 "self.stream = sd.RawInputStream(samplerate=48000, blocksize=1600, channels=2, dtype='int16', callback=self._audio_callback)",
                 "Card âm thanh gọi ngắt phần cứng mỗi 33.3ms, thu các khối âm thanh thô 1600 mẫu/kênh với độ trễ cực thấp."),
                ("BƯỚC 1.3: Đẩy vào Queue an toàn",
                 "def _audio_callback(indata, ...): self.audio_queue.put(bytes(indata))",
                 "Producer-Consumer: Đẩy luồng byte vào hàng đợi đa luồng thread-safe, tuyệt đối không tính toán nặng để chống nghẽn audio."),
                ("BƯỚC 1.4: Dừng thu & Ghép khối",
                 "raw_bytes = b''.join(self.audio_frames)  # Nối toàn bộ mảng byte trong RAM",
                 "Khi người dùng bấm Stop, gom toàn bộ các khối byte trong Queue thành một chuỗi nhị phân nguyên vẹn.")
            ],
            "ret_title": "[OUTPUT TẦNG 1]",
            "ret_desc": "raw_bytes: bytes  |  Chuỗi byte nhị phân PCM 16-bit nguyên bản, fs=48,000Hz (hoặc 44,100Hz), Stereo 2 kênh.",
            "in_title": "[INPUT TẦNG 2]",
            "in_desc": "audio_np = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0  ->  Đưa vào stop_recording()"
        },

        # ---------- GIAI ĐOẠN 2 ----------
        {
            "num": "GIAI ĐOẠN 2",
            "title": "TIỀN XỬ LÝ DSP & ĐIỀU CHUẨN ÂM HỌC (DSP CONDITIONING)",
            "file": "controllers/audio_controller.py & asr_controller.py",
            "y": 64.0, "height": 13.0,
            "border": c_green,
            "badge_color": "#008744",
            "steps": [
                ("BƯỚC 2.1: Chống triệt tiêu pha Stereo",
                 "active_ch = np.argmax([left_energy, right_energy]); audio_mono = audio_np[:, active_ch]",
                 "So sánh năng lượng 2 kênh; trích xuất kênh có tín hiệu đàm thoại mạnh nhất, tránh suy hao do gộp trung bình cộng."),
                ("BƯỚC 2.2: Polyphase Resampling 16kHz",
                 "audio_16k = signal.resample_poly(audio_mono, up=16000, down=orig_sr)  # Kaiser FIR",
                 "Hạ tần số lấy mẫu về chuẩn 16,000Hz; bộ lọc thông thấp Kaiser triệt tiêu 100% hiện tượng méo gấp phổ (Aliasing)."),
                ("BƯỚC 2.3: Năng lượng STE & Lọc VAD",
                 "frame = audio_16k[i:i+400] * np.hamming(400); vad_mask = (ste / ste.max()) >= 0.08",
                 "Phân tích khung 25ms, bước 10ms; ngưỡng VAD 0.08 (-22dBFS) gạt bỏ tiếng ồn quạt máy (-35dBFS) và tiếng thở."),
                ("BƯỚC 2.4: Sàn năng lượng an toàn (Floor)",
                 "if duration < 0.3s or max_amp < 0.0008: return 'Âm lượng quá nhỏ...'",
                 "Hàng rào bảo vệ kép chặn các đoạn ngắt mic hoặc im lặng (-62dBFS) để mô hình AI không bị ảo giác sinh chữ bậy."),
                ("BƯỚC 2.5: Peak Normalization & Headroom",
                 "norm_audio = (audio_16k / max_amp) * 0.95  # Dự trữ 5% Headroom (-0.45dBFS)",
                 "Kéo biên độ đỉnh của mọi giọng nói (nói nhỏ, nói xa mic) lên mức chuẩn, chống méo clipping trước khi vào nơ-ron.")
            ],
            "ret_title": "[OUTPUT TẦNG 2]",
            "ret_desc": "norm_audio: np.ndarray (dtype=float32, 1D)  |  Kích thước: (N_samples,), fs=16,000Hz Mono, Biên độ: [-0.95, +0.95]",
            "in_title": "[INPUT TẦNG 3]",
            "in_desc": "MelFeatureExtractor.extract(audio_np=norm_audio)  hoặc  processor(norm_audio, sampling_rate=16000)"
        },

        # ---------- GIAI ĐOẠN 3 ----------
        {
            "num": "GIAI ĐOẠN 3",
            "title": "TRÍCH XUẤT ĐẶC TRƯNG PHỔ MEL (ACOUSTIC FEATURE EXTRACTION)",
            "file": "models/feature_extractor.py",
            "y": 47.2, "height": 13.0,
            "border": c_purple,
            "badge_color": "#6200EA",
            "steps": [
                ("BƯỚC 3.1: Fourier ngắn hạn (STFT)",
                 "stft = torch.stft(y, n_fft=512, hop_length=160, win_length=400, window=hamming, return_complex=True)",
                 "Khung 25ms (400 mẫu), bước 10ms (160 mẫu), n_fft=512; trả về ma trận số phức kích thước (257, T_frames)."),
                ("BƯỚC 3.2: Tính Phổ công suất (Power)",
                 "power_spec = stft.abs().pow(2)  # |Z|² = Real² + Imag²",
                 "Loại bỏ góc pha phi ngữ nghĩa (Phase Invariance), giữ lại mật độ năng lượng phổ tại 257 dải tần số vật lý (0 - 8000Hz)."),
                ("BƯỚC 3.3: Chiếu qua 80 Dải lọc Mel",
                 "mel_spec = torch.matmul(self.mel_basis, power_spec)  # [80, 257] @ [257, T] = [80, T]",
                 "80 bộ lọc tam giác Mel m=2595*log10(1+f/700): lọc dày ở tần số thấp <1kHz (Formant) và nén thưa ở tần số cao >1kHz."),
                ("BƯỚC 3.4: Nén Logarithm năng lượng",
                 "log_mel = torch.log(torch.clamp(mel_spec, min=1e-5))  # Mô phỏng độ to Decibel",
                 "Nén dải động cực lớn của âm thanh về thang đo tuyến tính với cảm nhận thính giác của màng nhĩ người."),
                ("BƯỚC 3.5: Chuẩn hóa Z-Score (CMVN)",
                 "norm_mel = (log_mel - log_mel.mean()) / (log_mel.std() + 1e-6)  # Đưa về N(0, 1)",
                 "Cepstral Mean & Variance Normalization: Triệt tiêu hoàn toàn sự sai lệch âm sắc giữa các loại micro khác nhau.")
            ],
            "ret_title": "[OUTPUT TẦNG 3]",
            "ret_desc": "feat_tensor: torch.FloatTensor  |  Kích thước: (Batch=1, Channels=1, n_mels=80, T_frames), Chuẩn hóa μ=0, σ=1.",
            "in_title": "[INPUT TẦNG 4]",
            "in_desc": "SpeechCRNN_CTC.forward(feat_tensor)  hoặc  ctc_model(input_values=tensor_16k).logits"
        },

        # ---------- GIAI ĐOẠN 4 ----------
        {
            "num": "GIAI ĐOẠN 4",
            "title": "MÔ HÌNH NƠ-RON SÂU MÃ HÓA ÂM VỊ (DEEP ACOUSTIC MODEL)",
            "file": "models/crnn_model.py & controllers/asr_controller.py",
            "y": 30.4, "height": 13.0,
            "border": c_orange,
            "badge_color": "#E65100",
            "steps": [
                ("BƯỚC 4.1: 3 Khối Tích chập 2D (Conv2D)",
                 "nn.Conv2d(in, out, k=3, p=1) -> BatchNorm2d -> Hardtanh -> MaxPool2d",
                 "Conv1 & Conv2 nén (80->40->20 Mel); Conv3 gộp MaxPool(2,1) đưa về 10 dải Mel, giữ nguyên trục thời gian cho CTC."),
                ("BƯỚC 4.2: Tầng Chiếu tuyến tính FC",
                 "self.fc_proj = nn.Linear(128 * (80 // 8), hidden_size=256)  # Phẳng hóa 1280 -> 256",
                 "Gộp các kênh đặc trưng không gian tần số thành vector biểu diễn ngữ âm 256 chiều sẵn sàng cho mạng hồi quy."),
                ("BƯỚC 4.3: 2 Tầng BiGRU Học chuỗi 2 chiều",
                 "self.rnn = nn.GRU(256, 256, num_layers=2, bidirectional=True, batch_first=True)",
                 "Học ngữ cảnh phụ thuộc thời gian: Nối ghép [h_fwd || h_bwd] tạo vector 512 chiều bao quát cả âm tiết trước và sau."),
                ("BƯỚC 4.4: Tầng Phân loại CTC & Khử Blank",
                 "self.classifier = nn.Linear(512, vocab_size=105); self.classifier.bias[0] = -3.0",
                 "Dìm xác suất tiên nghiệm của token Blank < 5%, triệt tiêu 100% nguy cơ sụp đổ mô hình (CTC Blank Collapse)."),
                ("ĐỘNG CƠ 2: Wav2Vec2 CTC Fine-tune",
                 "logits = self.ctc_model(input_values).logits  # 7 CNN Encoders + 12 Transformer Blocks",
                 "Động cơ bổ trợ: Kế thừa biểu diễn âm học 250h tiếng Việt và fine-tune tầng CTC Head trên tập VIVOS (100% Offline).")
            ],
            "ret_title": "[OUTPUT TẦNG 4]",
            "ret_desc": "logits: torch.FloatTensor  |  Kích thước: (Batch=1, T_frames, Vocab_size=105)  [Ma trận Logits chưa qua Softmax]",
            "in_title": "[INPUT TẦNG 5]",
            "in_desc": "ctc_decoder.decode_single(logits[0])  hoặc  processor.batch_decode(torch.argmax(logits, dim=-1))"
        },

        # ---------- GIAI ĐOẠN 5 ----------
        {
            "num": "GIAI ĐOẠN 5",
            "title": "GIẢI MÃ CTC & HẬU XỬ LÝ NGÔN NGỮ TIẾNG VIỆT (DECODING & NLP)",
            "file": "models/ctc_decoder.py",
            "y": 13.6, "height": 13.0,
            "border": c_pink,
            "badge_color": "#C2185B",
            "steps": [
                ("BƯỚC 5.1: CTC Greedy Best-Path Search",
                 "pred_ids = torch.argmax(logits, dim=-1)  # Chọn argmax P(token|t) tại mỗi frame",
                 "Quét dọc trục thời gian, trích xuất chuỗi chỉ số token có khả năng xuất hiện cao nhất tại từng khung âm học."),
                ("BƯỚC 5.2: Toán tử Sụp đổ B (Collapse)",
                 "if token_id != prev and token_id != blank_id: result.append(vocab[token_id])",
                 "Gộp ký tự trùng liên tiếp và xóa sạch token Blank ε: Ví dụ ['b', 'b', 'ε', 'a', 'a'] -> 'ba'."),
                ("BƯỚC 5.3: Bóc Khung Phụ Âm Unicode NFKD",
                 "decomposed = unicodedata.normalize('NFKD', word); skeleton = ''.join([c for c in decomposed if is_consonant(c)])",
                 "Tách dấu thanh tiếng Việt và loại nguyên âm: Từ 'thương' -> Khung phụ âm 'th-ng' chuẩn xác."),
                ("BƯỚC 5.4: Ràng buộc Từ điển 4,861 từ VIVOS",
                 "matched_word = lexicon.lookup_skeleton(skeleton, candidates)  # vietnamese_lexicon.json",
                 "So khớp khoảng cách Levenshtein với ngữ liệu chuẩn, sửa lỗi sai dấu thanh và biến dạng nguyên âm do phát âm nhanh."),
                ("BƯỚC 5.5: Khử lặp từ ngắc ngứ (De-dup)",
                 "if matched_word != prev_word: final_words.append(matched_word)",
                 "Khử hoàn toàn lỗi lặp từ liên tiếp do trễ khung thời gian (ví dụ: 'đại học học sư phạm' -> 'đại học sư phạm').")
            ],
            "ret_title": "[OUTPUT TẦNG 5]",
            "ret_desc": "transcription: str  |  Chuỗi văn bản tiếng Việt chuẩn Unicode có dấu (Ví dụ: 'trường đại học sư phạm kỹ thuật')",
            "in_title": "[INPUT GIAO DIỆN & TTS]",
            "in_desc": "self.txt_result.insert('end', transcription)  &  audio_controller.text_to_speech(transcription)"
        }
    ]

    # ==================== VẼ CÁC THẺ GIAI ĐOẠN & CẦU NỐI ====================
    for s in stages:
        # 1. Khung chính của Stage
        card = patches.FancyBboxPatch(
            (3, s["y"]), 94, s["height"], boxstyle="round,pad=0.5,rounding_size=0.7",
            linewidth=2.0, edgecolor=s["border"], facecolor=c_card_bg
        )
        ax.add_patch(card)

        # Header Badge: Giai đoạn
        badge = patches.FancyBboxPatch(
            (4.2, s["y"] + s["height"] - 2.3), 16.5, 1.7, boxstyle="round,pad=0.2,rounding_size=0.35",
            facecolor=s["badge_color"], edgecolor="none"
        )
        ax.add_patch(badge)
        ax.text(12.45, s["y"] + s["height"] - 1.45, s["num"],
                fontsize=10.5, fontweight="bold", color="#FFFFFF", ha="center", va="center")

        # Tiêu đề Stage
        ax.text(22.0, s["y"] + s["height"] - 1.45, s["title"],
                fontsize=12.2, fontweight="bold", color=s["border"], ha="left", va="center")

        # Đường dẫn File mã nguồn
        ax.text(95.5, s["y"] + s["height"] - 1.45, f"Source File: {s['file']}",
                fontsize=9.2, fontstyle="italic", color="#94A3B8", ha="right", va="center")

        # Đường kẻ phân cách Header
        ax.plot([4.2, 95.8], [s["y"] + s["height"] - 2.7, s["y"] + s["height"] - 2.7],
                color=c_card_border_dim, linewidth=1.2)

        # 2. Danh sách các Bước Tuần Tự (Steps with Code Highlights)
        num_steps = len(s["steps"])
        step_spacing = (s["height"] - 3.4) / num_steps
        step_y = s["y"] + s["height"] - 3.5

        for step_idx, (step_name, step_code, step_desc) in enumerate(s["steps"]):
            # Badge tên bước
            ax.text(4.5, step_y, f">> {step_name}:", fontsize=9.8, fontweight="bold", color="#FFFFFF", ha="left", va="center")

            # Hộp Code thực tế (Code Box)
            code_bg = patches.FancyBboxPatch(
                (27.0, step_y - 0.48), 68.8, 1.0, boxstyle="round,pad=0.15,rounding_size=0.2",
                facecolor=c_code_bg, edgecolor="#2A3B54", linewidth=0.8
            )
            ax.add_patch(code_bg)
            ax.text(28.0, step_y, step_code, fontsize=8.8, fontfamily="monospace", fontweight="bold", color=c_yellow, ha="left", va="center")

            # Dòng giải thích bản chất kỹ thuật bên dưới
            ax.text(6.0, step_y - 0.85, f"   * {step_desc}", fontsize=8.7, color="#CBD5E1", ha="left", va="center")

            step_y -= step_spacing

        # 3. Hộp Giao diện Dữ liệu Kết nối (DATA TRANSFER INTERFACE: RETURN -> INPUT)
        conn_box_y = s["y"] - 3.4
        conn_box = patches.FancyBboxPatch(
            (6.0, conn_box_y), 88.0, 2.8, boxstyle="round,pad=0.3,rounding_size=0.5",
            linewidth=1.2, edgecolor="#0284C7", facecolor=c_connector_bg
        )
        ax.add_patch(conn_box)

        # Mũi tên kết nối dọc
        ax.annotate(
            "", xy=(50, conn_box_y - 0.4), xytext=(50, s["y"]),
            arrowprops=dict(arrowstyle="->,head_width=0.45,head_length=0.55", color="#38BDF8", lw=1.8)
        )

        # Nội dung RETURN (Output tầng này)
        ax.text(8.0, conn_box_y + 1.9, f"{s['ret_title']}:",
                fontsize=8.8, fontweight="bold", color="#38BDF8", ha="left", va="center")
        ax.text(26.5, conn_box_y + 1.9, s["ret_desc"],
                fontsize=8.6, fontfamily="monospace", color="#BAE6FD", ha="left", va="center")

        # Nội dung INPUT (Đầu vào tầng tiếp theo)
        ax.text(8.0, conn_box_y + 0.8, f"{s['in_title']}:",
                fontsize=8.8, fontweight="bold", color="#4ADE80", ha="left", va="center")
        ax.text(26.5, conn_box_y + 0.8, s["in_desc"],
                fontsize=8.6, fontfamily="monospace", color="#BBF7D0", ha="left", va="center")

    # ==================== GIAI ĐOẠN CUỐI: HIỂN THỊ GUI & PHÁT TTS ====================
    final_box = patches.FancyBboxPatch(
        (3, 1.2), 94, 7.8, boxstyle="round,pad=0.5,rounding_size=0.7",
        linewidth=2.2, edgecolor=c_green, facecolor="#092317"
    )
    ax.add_patch(final_box)

    badge_final = patches.FancyBboxPatch(
        (4.2, 6.7), 16.5, 1.7, boxstyle="round,pad=0.2,rounding_size=0.35",
        facecolor="#008744", edgecolor="none"
    )
    ax.add_patch(badge_final)
    ax.text(12.45, 7.55, "KẾT QUẢ ĐẦU RA",
            fontsize=10.5, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    ax.text(22.0, 7.55, "VĂN BẢN TIẾNG VIỆT HOÀN CHỈNH & TỔNG HỢP GIỌNG ĐỌC (OUTPUT & TTS)",
            fontsize=12.5, fontweight="bold", color="#00FF9D", ha="left", va="center")

    ax.text(95.5, 7.55, "Source Files: views/main_view.py & controllers/audio_controller.py",
            fontsize=9.2, fontstyle="italic", color="#A7F3D0", ha="right", va="center")

    ax.plot([4.2, 95.8], [6.3, 6.3], color="#1B4D36", linewidth=1.2)

    # Chi tiết 2 bước cuối
    ax.text(4.5, 4.8, ">> BƯỚC 6.1: Hiển thị Giao diện Desktop:", fontsize=9.8, fontweight="bold", color="#FFFFFF", ha="left", va="center")
    code_gui = patches.FancyBboxPatch((32.0, 4.3), 63.8, 1.0, boxstyle="round,pad=0.15,rounding_size=0.2", facecolor=c_code_bg, edgecolor="#2A3B54", linewidth=0.8)
    ax.add_patch(code_gui)
    ax.text(33.0, 4.8, "self.txt_result.configure(state='normal'); self.txt_result.insert('end', text)", fontsize=8.8, fontfamily="monospace", fontweight="bold", color=c_yellow, ha="left", va="center")
    ax.text(6.0, 3.8, "   * Cập nhật văn bản nhận dạng ra Textbox CustomTkinter, kích hoạt trạng thái chỉnh sửa, sao chép hoặc lưu file.", fontsize=8.7, color="#CBD5E1", ha="left", va="center")

    ax.text(4.5, 2.3, ">> BƯỚC 6.2: Tổng hợp Giọng đọc TTS:", fontsize=9.8, fontweight="bold", color="#FFFFFF", ha="left", va="center")
    code_tts = patches.FancyBboxPatch((32.0, 1.8), 63.8, 1.0, boxstyle="round,pad=0.15,rounding_size=0.2", facecolor=c_code_bg, edgecolor="#2A3B54", linewidth=0.8)
    ax.add_patch(code_tts)
    ax.text(33.0, 2.3, "tts = gTTS(text=text, lang='vi'); tts.write_to_fp(fp); pygame.mixer.music.play()", fontsize=8.8, fontfamily="monospace", fontweight="bold", color=c_yellow, ha="left", va="center")
    ax.text(6.0, 1.3, "   * Phát giọng nói tiếng Việt tự nhiên qua loa, chạy trên Worker Thread riêng biệt không gây đơ lag giao diện đồ họa.", fontsize=8.7, color="#CBD5E1", ha="left", va="center")

    # ==================== LƯU FILE ẢNH ====================
    plt.tight_layout()
    plt.savefig(output_path, dpi=220, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print("SUCCESS: Pipeline image generated successfully at " + output_path)

    # Copy sang thư mục Downloads và thư mục artifact để xem trực tiếp
    downloads_path = r"C:\Users\Admin\Downloads\pipeline_tong_the.png"
    try:
        shutil.copy2(output_path, downloads_path)
        print("SUCCESS: Copied to Downloads: " + downloads_path)
    except Exception as e:
        print("Error copying to Downloads:", e)

    artifact_dir = r"C:\Users\Admin\.gemini\antigravity\brain\be3d93c4-5042-42e9-a1f9-2a57a29a12d5"
    if os.path.exists(artifact_dir):
        artifact_path = os.path.join(artifact_dir, "pipeline_tong_the.png")
        shutil.copy2(output_path, artifact_path)
        print("SUCCESS: Copied to artifact " + artifact_path)

if __name__ == "__main__":
    draw_pipeline()
