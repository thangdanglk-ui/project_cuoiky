import os
import sys
import glob
import torch
import soundfile as sf
import numpy as np
import librosa
from torch.utils.data import Dataset

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

class MelFeatureExtractor:
    """
    =============================================================================
    [MỤC 2.4 - TV1: TRẦN ĐĂNG THẮNG]
    TRÍCH XUẤT ĐẶC TRƯNG 80 DẢI LOG-MEL SPECTROGRAM & CỬA SỔ HAMMING (Slide 2b)
    - Bước 1: Phân khung (25ms = 400 mẫu, hop 10ms = 160 mẫu) & Cửa sổ Hamming
    - Bước 2: STFT 512 điểm tính phổ công suất Power Spectrum |STFT|^2
    - Bước 3: Ngân hàng 80 bộ lọc tam giác Mel Filterbank & Thang đo Logarit
    - Bước 4: Chuẩn hóa phổ CMVN (Mean-Variance Normalization) khử méo micro
    =============================================================================
    """
    def __init__(self, sample_rate=16000, n_fft=512, win_length=400, hop_length=160, n_mels=80):
        # [MỤC 2.4 - TV1] Tham số DSP chuẩn đồ án:
        self.sample_rate = sample_rate  # 16.000 Hz
        self.n_fft = n_fft              # 512 điểm FFT (257 bins tần số)
        self.win_length = win_length    # 400 mẫu = 25ms (tín hiệu giả dừng)
        self.hop_length = hop_length    # 160 mẫu = 10ms (độ chồng lấn overlap 60%)
        self.n_mels = n_mels            # 80 dải lọc Mel phi tuyến tính

        # [MỤC 2.4 - TV1] Khởi tạo ma trận 80 bộ lọc Mel mô phỏng ốc tai
        mel_fb = librosa.filters.mel(sr=sample_rate, n_fft=n_fft, n_mels=n_mels)
        self.mel_basis = torch.from_numpy(mel_fb).float()
        # [MỤC 2.4 - TV1] Cửa sổ Hamming w[n] giảm búp phụ -43 dB, chống rò rỉ phổ (Spectral leakage)
        self.window = torch.hamming_window(win_length)

    def extract(self, audio_np):
        """
        [MỤC 2.4 - TV1] Trích xuất Log Mel-Spectrogram từ mảng âm thanh 16kHz
        Đầu vào: Mảng audio float32 biên độ [-1.0, 1.0]
        Đầu ra: Tensor đặc trưng (n_mels=80, Time) đã chuẩn hóa CMVN
        """
        if isinstance(audio_np, np.ndarray):
            y = torch.from_numpy(audio_np).float()
        else:
            y = audio_np.float()

        # [MỤC 2.4 - TV1] Bước 1 & 2: STFT với cửa sổ Hamming -> Phổ công suất |STFT|^2
        stft = torch.stft(
            y,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.win_length,
            window=self.window,
            return_complex=True
        )
        power_spec = stft.abs().pow(2)  # (N_fft/2 + 1 = 257, Time)

        # [MỤC 2.4 - TV1] Bước 3: Chiếu qua 80 dải lọc Mel & Nén Logarit theo luật Weber-Fechner
        mel_spec = torch.matmul(self.mel_basis, power_spec)  # (80, Time)
        log_mel = torch.log(torch.clamp(mel_spec, min=1e-5))

        # [MỤC 2.4 - TV1] Bước 4: Chuẩn hóa CMVN (Mean-Variance Normalization) khử méo kênh truyền / mic
        mean = log_mel.mean()
        std = log_mel.std() + 1e-6
        norm_mel = (log_mel - mean) / std

        return norm_mel  # (n_mels=80, Time)


class VIVOSDataset(Dataset):
    """
    =============================================================================
    [MỤC 2.2 - TV1: TRẦN ĐĂNG THẮNG]
    CẤU TRÚC DỮ LIỆU TẬP NGỮ LIỆU TIẾNG VIỆT VIVOS:
    - Tổng thời lượng: 15.4 giờ, 12.488 câu
    - Train set: 11.660 câu (46 người nói nam/nữ đa vùng miền)
    - Test set: 828 câu (19 người nói hoàn toàn độc lập - Speaker-Independent)
    - Định dạng: WAV 16kHz, 16-bit Mono Linear PCM, nhãn trong prompts.txt
    =============================================================================
    """
    def __init__(self, vivos_dir, split="train", vocab=None, max_duration=12.0, min_duration=0.5):
        self.vivos_dir = vivos_dir
        self.split = split
        self.vocab = vocab
        self.extractor = MelFeatureExtractor()

        split_dir = os.path.join(vivos_dir, split)
        prompts_file = os.path.join(split_dir, "prompts.txt")
        waves_dir = os.path.join(split_dir, "waves")

        if not os.path.exists(prompts_file):
            raise FileNotFoundError(f"Không tìm thấy file nhãn: {prompts_file}")

        # Lập chỉ mục toàn bộ file .wav theo ID
        wav_files = glob.glob(os.path.join(waves_dir, "*", "*.wav"))
        wav_map = {os.path.splitext(os.path.basename(p))[0]: p for p in wav_files}

        self.samples = []
        with open(prompts_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    utt_id, text = parts[0], parts[1]
                else:
                    utt_id, text = parts[0], ""

                if utt_id in wav_map:
                    self.samples.append((wav_map[utt_id], text.strip()))

        self.cache = {}
        print(f"[VIVOSDataset] Đã nạp tập '{split}': {len(self.samples)} mẫu câu hợp lệ.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        if idx in self.cache:
            return self.cache[idx]

        wav_path, text = self.samples[idx]
        try:
            audio, sr = sf.read(wav_path)
            if audio.ndim > 1:
                audio = np.mean(audio, axis=1)
            # Trích xuất Mel
            mel = self.extractor.extract(audio)  # (80, Time)
        except Exception as e:
            mel = torch.zeros(80, 100)

        # Chuyển nhãn văn bản sang vector chỉ số
        if self.vocab is not None:
            label_indices = self.vocab.text_to_indices(text)
        else:
            label_indices = []

        # Đảm bảo trục thời gian CTC (T // 4) đủ dài cho số lượng ký tự nhãn
        ctc_time_frames = mel.size(1) // 4
        if len(label_indices) > ctc_time_frames and ctc_time_frames > 0:
            # Cắt bớt nhãn để tránh lỗi CTC out_lens < tgt_lens
            label_indices = label_indices[:ctc_time_frames]

        item = (mel, label_indices, text)
        if len(self.cache) < 3000:
            self.cache[idx] = item

        return item


class CommonVoiceDataset(Dataset):
    """
    =============================================================================
    [MỞ RỘNG MIỀN DỮ LIỆU - TV1: TRẦN ĐĂNG THẮNG]
    BỘ DỮ LIỆU MOZILLA COMMON VOICE TIẾNG VIỆT CHUẨN 16KHZ MONO (1.000 MẪU)
    - Âm thanh thu thập từ cộng đồng đa dạng chất giọng, môi trường và micro
    - Phục vụ Huấn luyện mở rộng miền (Domain Adaptation) cho Dual-Attention ACRNN
    - Bằng chứng học thuật về năng lực tổng quát hóa đa tập dữ liệu
    =============================================================================
    """
    def __init__(self, cv_dir=None, split="train", vocab=None):
        if cv_dir is None:
            base_project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cv_dir = os.path.join(base_project, "dataset", "common_voice_vi")
        self.cv_dir = cv_dir
        self.split = split
        self.vocab = vocab
        self.extractor = MelFeatureExtractor()

        # Hỗ trợ cả cấu trúc phân tách train/test chuẩn VIVOS lẫn cấu trúc phẳng
        split_dir = os.path.join(cv_dir, split)
        if os.path.exists(split_dir):
            prompts_file = os.path.join(split_dir, "prompts.txt")
            waves_dir = os.path.join(split_dir, "waves")
        else:
            prompts_file = os.path.join(cv_dir, "prompts.txt")
            waves_dir = os.path.join(cv_dir, "waves")

        if not os.path.exists(prompts_file):
            raise FileNotFoundError(f"Không tìm thấy file nhãn Common Voice: {prompts_file}")

        self.samples = []
        with open(prompts_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    utt_id, text = parts[0], parts[1]
                else:
                    utt_id, text = parts[0], ""

                wav_path = os.path.join(waves_dir, f"{utt_id}.wav")
                if os.path.exists(wav_path):
                    self.samples.append((wav_path, text.strip()))

        self.cache = {}
        print(f"[CommonVoiceDataset] Đã nạp thành công tập '{split}': {len(self.samples)} mẫu câu Mozilla Common Voice hợp lệ.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        if idx in self.cache:
            return self.cache[idx]

        wav_path, text = self.samples[idx]
        try:
            audio, sr = sf.read(wav_path)
            if audio.ndim > 1:
                audio = np.mean(audio, axis=1)
            mel = self.extractor.extract(audio)
        except Exception as e:
            mel = torch.zeros(80, 100)

        if self.vocab is not None:
            label_indices = self.vocab.text_to_indices(text)
        else:
            label_indices = []

        ctc_time_frames = mel.size(1) // 4
        if len(label_indices) > ctc_time_frames and ctc_time_frames > 0:
            label_indices = label_indices[:ctc_time_frames]

        item = (mel, label_indices, text)
        if len(self.cache) < 2000:
            self.cache[idx] = item

        return item


def ctc_collate_fn(batch):
    """
    Hàm Collate xử lý kích thước biến thiên cho CTC:
    - Zero-padding cho Mel-Spectrogram dọc theo trục thời gian T
    - Padding cho nhãn văn bản
    - Trả về input_lengths và target_lengths cho torch.nn.CTCLoss
    """
    mels, labels, texts = zip(*batch)

    # 1. Padding âm thanh (Mel-Spectrogram)
    # mel shape: (80, T)
    mel_lengths = [m.size(1) for m in mels]
    max_mel_len = max(mel_lengths)
    n_mels = mels[0].size(0)

    batch_size = len(mels)
    # Tensor 4D: (Batch, 1, n_mels, max_mel_len)
    padded_mels = torch.zeros(batch_size, 1, n_mels, max_mel_len)
    for i, m in enumerate(mels):
        padded_mels[i, 0, :, :m.size(1)] = m

    # 2. Padding nhãn văn bản
    label_lengths = [len(l) for l in labels]
    max_label_len = max(max(label_lengths), 1)

    padded_labels = torch.zeros(batch_size, max_label_len, dtype=torch.long)
    for i, l in enumerate(labels):
        if len(l) > 0:
            padded_labels[i, :len(l)] = torch.tensor(l, dtype=torch.long)

    input_lengths = torch.tensor(mel_lengths, dtype=torch.long)
    target_lengths = torch.tensor(label_lengths, dtype=torch.long)

    return padded_mels, padded_labels, input_lengths, target_lengths, texts


if __name__ == "__main__":
    from .vocab import VietnameseVocab
    vivos_path = "project_cuoiky/dataset/vivos"
    if os.path.exists(vivos_path):
        vocab = VietnameseVocab()
        ds = VIVOSDataset(vivos_path, split="test", vocab=vocab)
        print(f"Số mẫu tập test: {len(ds)}")
        mel, lbl, txt = ds[0]
        print(f"Mẫu đầu tiên: Mel shape: {mel.shape}, Nhãn: '{txt}', Token len: {len(lbl)}")

        # Thử nghiệm collate_fn
        from torch.utils.data import DataLoader
        loader = DataLoader(ds, batch_size=4, shuffle=False, collate_fn=ctc_collate_fn)
        for b_mels, b_labels, in_lens, tgt_lens, b_texts in loader:
            print(f"Batch Mels shape: {b_mels.shape}")
            print(f"Batch Labels shape: {b_labels.shape}")
            print(f"Input lengths: {in_lens}")
            print(f"Target lengths: {tgt_lens}")
            break
