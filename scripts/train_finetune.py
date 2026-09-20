import os
import sys
import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import soundfile as sf

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

def fine_tune_ctc_on_vivos(epochs=3, batch_size=4, lr=1e-4, max_samples=50):
    """
    Huấn luyện chuyển giao (Transfer Learning & Fine-tuning) mô hình CTC trên tập VIVOS.
    Chuẩn ngành ASR hiện đại: Tối ưu trọng số Acoustic Model + CTC Loss trên dữ liệu đích.
    """
    print("=" * 70)
    print("BẮT ĐẦU FINE-TUNING MÔ HÌNH CTC TRÊN TẬP DỮ LIỆU VIVOS TIẾNG VIỆT")
    print(f"Tham số: Epochs={epochs}, BatchSize={batch_size}, LR={lr}, Samples={max_samples}")
    print("=" * 70)

    model_id = "nguyenvulebinh/wav2vec2-base-vietnamese-250h"
    processor = Wav2Vec2Processor.from_pretrained(model_id)
    model = Wav2Vec2ForCTC.from_pretrained(model_id)
    model.train()

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    print(f"[OK] Đã khởi tạo mô hình CTC ({sum(p.numel() for p in model.parameters()):,} tham số)")
    print("[OK] Đã sẵn sàng huấn luyện tinh chỉnh (Fine-tuning)!")

if __name__ == "__main__":
    fine_tune_ctc_on_vivos()
