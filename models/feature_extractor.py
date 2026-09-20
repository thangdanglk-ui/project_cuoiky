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
    Bộ trích xuất đặc trưng Log Mel-Spectrogram thuần PyTorch & Cửa sổ Hamming (Slide 01c)
    Tốc độ xử lý cực nhanh trực tiếp trên Tensor.
    """
    def __init__(self, sample_rate=16000, n_fft=512, win_length=400, hop_length=160, n_mels=80):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.win_length = win_length
        self.hop_length = hop_length
        self.n_mels = n_mels

        # Khởi tạo ma trận bộ lọc Mel (Mel Filter Bank - Slide 01c)
        mel_fb = librosa.filters.mel(sr=sample_rate, n_fft=n_fft, n_mels=n_mels)
        self.mel_basis = torch.from_numpy(mel_fb).float()
        # Cửa sổ Hamming (Hamming Window - Slide 01c)
        self.window = torch.hamming_window(win_length)

    def extract(self, audio_np):
        """Trích xuất Log Mel-Spectrogram từ mảng numpy âm thanh 16kHz."""
        if isinstance(audio_np, np.ndarray):
            y = torch.from_numpy(audio_np).float()
        else:
            y = audio_np.float()

        # STFT với cửa sổ Hamming
        stft = torch.stft(
            y,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.win_length,
            window=self.window,
            return_complex=True
        )
        # Năng lượng phổ (Power Spectrum = |STFT|^2)
        power_spec = stft.abs().pow(2)
        # Chiếu qua dải lọc Mel
        mel_spec = torch.matmul(self.mel_basis, power_spec)
        # Thang đo Logarit (Log Mel-Spectrogram)
        log_mel = torch.log(torch.clamp(mel_spec, min=1e-5))

        # Chuẩn hóa Mean-Variance Normalization (CMVN)
        mean = log_mel.mean()
        std = log_mel.std() + 1e-6
        norm_mel = (log_mel - mean) / std

        return norm_mel  # (n_mels, Time)


class VIVOSDataset(Dataset):
    """
    PyTorch Dataset cho tập dữ liệu VIVOS Tiếng Việt.
    Đọc các file âm thanh .wav và các câu nhãn văn bản từ prompts.txt.
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
