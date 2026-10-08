import os
import sys
import time
import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, ConcatDataset, Subset

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models.vocab import VietnameseVocab
from models.crnn_model import SpeechCRNN_CTC
from models.feature_extractor import CommonVoiceDataset, VIVOSDataset, ctc_collate_fn
from models.ctc_decoder import CTCGreedyDecoder

def train_common_voice(epochs=1, batch_size=16, lr=5e-5, mix_vivos=True, max_hours=0.5, device=None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        torch.set_num_threads(2)
    device_obj = torch.device(device)

    weights_dir = os.path.join(BASE_DIR, "models", "weights")
    os.makedirs(weights_dir, exist_ok=True)
    vocab_path = os.path.join(weights_dir, "vocab.json")
    base_model_path = os.path.join(weights_dir, "vivos_ctc_model.pth")
    adapted_model_path = os.path.join(weights_dir, "vivos_commonvoice_acrnn.pth")

    vocab = VietnameseVocab()
    print("=" * 75)
    print(" HUẤN LUYỆN MỞ RỘNG MIỀN (DOMAIN ADAPTATION) TRÊN MOZILLA COMMON VOICE")
    print(" Mô hình: Dual-Attention ACRNN (SE-Block + Multi-Head Self-Attention)")
    print(f" Dữ liệu: Mozilla Common Voice Tiếng Việt chuẩn 16kHz (1.000 mẫu)")
    print(f" Chế độ: {'Trộn Common Voice + VIVOS (Chống quên)' if mix_vivos else 'Chỉ Common Voice'}")
    print(f" Cấu hình: Epochs={epochs}, BatchSize={batch_size}, LR={lr}, MaxHours={max_hours}h")
    print("=" * 75)

    # 1. Nạp tập dữ liệu Common Voice đã được phân tách chuẩn mực
    cv_train = CommonVoiceDataset(split="train", vocab=vocab)
    cv_test = CommonVoiceDataset(split="test", vocab=vocab)

    if mix_vivos:
        vivos_dir = os.path.join(BASE_DIR, "dataset", "vivos")
        if os.path.exists(vivos_dir):
            vivos_raw = VIVOSDataset(vivos_dir, split="train", vocab=vocab)
            # Trộn 500 mẫu VIVOS vào cùng để chống catastrophic forgetting
            vivos_sub = Subset(vivos_raw, list(range(min(500, len(vivos_raw)))))
            train_dataset = ConcatDataset([cv_train, vivos_sub])
            print(f"[Đa miền] Đã trộn {len(cv_train)} mẫu Common Voice + {len(vivos_sub)} mẫu VIVOS = {len(train_dataset)} mẫu!")
        else:
            train_dataset = cv_train
    else:
        train_dataset = cv_train

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=ctc_collate_fn,
        num_workers=0
    )
    val_loader = DataLoader(
        cv_test,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=ctc_collate_fn,
        num_workers=0
    )

    # 3. Khởi tạo mô hình & Nạp checkpoint kỷ lục hiện tại
    model = SpeechCRNN_CTC(n_mels=80, vocab_size=len(vocab)).to(device_obj)
    if os.path.exists(base_model_path):
        print(f"\n[Kế thừa] Nạp trọng số Dual-Attention tối ưu từ: {base_model_path}")
        ckpt = torch.load(base_model_path, map_location=device_obj)
        model.load_state_dict(ckpt["state_dict"])
        print(f"[OK] Nạp thành công! Val Loss kỷ lục VIVOS: {ckpt.get('val_loss', 'N/A')}")
    else:
        print("[Cảnh báo] Không tìm thấy vivos_ctc_model.pth, khởi tạo trọng số ngẫu nhiên!")

    criterion = nn.CTCLoss(blank=vocab.blank_id, zero_infinity=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    decoder = CTCGreedyDecoder(vocab)

    start_time = time.time()
    max_seconds = max_hours * 3600.0
    num_batches = len(train_loader)

    print(f"\n[Bắt đầu] Huấn luyện {epochs} Epoch ({num_batches} batches/epoch)...")
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        ep_start = time.time()

        for b_idx, (mels, labels, in_lens, tgt_lens, texts) in enumerate(train_loader):
            if time.time() - start_time >= max_seconds:
                print("\n[Dừng] Đã đạt giới hạn thời gian an toàn!")
                break

            mels = mels.to(device_obj)
            labels = labels.to(device_obj)

            optimizer.zero_grad()
            log_probs = model(mels)
            out_lens = model.get_output_lengths(in_lens).to(device_obj)

            loss = criterion(log_probs.permute(1, 0, 2), labels, out_lens, tgt_lens)
            if torch.isnan(loss) or torch.isinf(loss):
                continue

            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()

            total_loss += loss.item()

            if (b_idx + 1) % 10 == 0 or (b_idx + 1) == num_batches:
                avg = total_loss / (b_idx + 1)
                elapsed = time.time() - ep_start
                print(f"Epoch {epoch} [{b_idx+1}/{num_batches}] - Batch Loss: {loss.item():.4f} (Avg: {avg:.4f}) - Đã chạy: {elapsed:.1f}s", flush=True)

        # Đánh giá trên tập Common Voice Test
        model.eval()
        val_loss = 0.0
        sample_pred = ""
        sample_true = ""
        with torch.no_grad():
            for v_idx, (v_mels, v_labels, v_in_lens, v_tgt_lens, v_texts) in enumerate(val_loader):
                v_mels = v_mels.to(device_obj)
                v_labels = v_labels.to(device_obj)
                v_log_probs = model(v_mels)
                v_out_lens = model.get_output_lengths(v_in_lens).to(device_obj)

                vl = criterion(v_log_probs.permute(1, 0, 2), v_labels, v_out_lens, v_tgt_lens)
                if not torch.isnan(vl) and not torch.isinf(vl):
                    val_loss += vl.item()

                if v_idx == 0 and len(v_texts) > 0:
                    decoded = decoder.decode_batch(v_log_probs, v_out_lens)
                    sample_pred = decoded[0]
                    sample_true = v_texts[0]

        avg_val_loss = val_loss / max(1, len(val_loader))
        print(f"\n[KẾT QUẢ ADAPTATION] Epoch {epoch}:", flush=True)
        print(f"   Train Loss: {total_loss / max(1, num_batches):.4f} | Common Voice Val Loss: {avg_val_loss:.4f}", flush=True)
        print(f"   - Nhãn chuẩn Common Voice: '{sample_true}'", flush=True)
        print(f"   - AI nhận diện:             '{sample_pred}'", flush=True)

    # Lưu checkpoint mô hình mở rộng
    ckpt_save = {
        "state_dict": model.state_dict(),
        "vocab_chars": vocab.chars,
        "model_config": {
            "n_mels": 80,
            "vocab_size": len(vocab),
            "hidden_size": 256,
            "num_rnn_layers": 2
        },
        "adaptation_dataset": "Mozilla Common Voice 13.0 Vietnamese",
        "val_loss": avg_val_loss,
        "base_model": "Dual-Attention ACRNN"
    }
    torch.save(ckpt_save, adapted_model_path)
    # Đồng thời cập nhật checkpoint chính vivos_ctc_model.pth để ứng dụng web và controller dùng ngay
    torch.save(ckpt_save, base_model_path)
    print(f"\n[LƯU TRỮ] Đã lưu mô hình thích ứng đa miền vào: {adapted_model_path}", flush=True)
    print(f"[ĐỒNG BỘ] Đã đồng bộ vào checkpoint chính: {base_model_path}", flush=True)
    print("=" * 75)
    print("HOÀN TẤT HUẤN LUYỆN MỞ RỘNG TRÊN MOZILLA COMMON VOICE!")
    print("=" * 75)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Huấn luyện thích ứng trên Mozilla Common Voice")
    parser.add_argument("--epochs", type=int, default=1, help="Số epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Kích thước batch")
    parser.add_argument("--lr", type=float, default=5e-5, help="Learning rate nhỏ cho fine-tuning")
    parser.add_argument("--hours", type=float, default=0.5, help="Thời gian tối đa (giờ)")
    parser.add_argument("--device", type=str, default=None, help="Thiết bị huấn luyện: cuda hoặc cpu")
    parser.add_argument("--no_mix", action="store_true", help="Không trộn VIVOS")
    args = parser.parse_args()

    train_common_voice(
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        mix_vivos=not args.no_mix,
        max_hours=args.hours,
        device=args.device
    )
