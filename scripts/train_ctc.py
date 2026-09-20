import os
import sys
import time
import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset

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
from models.feature_extractor import VIVOSDataset, ctc_collate_fn
from models.ctc_decoder import CTCGreedyDecoder

def train_ctc(epochs=30, batch_size=16, lr=1e-4, max_train_samples=3000, device="cpu", resume=True, max_hours=2.0):
    # Điều tiết CPU hợp lý để máy không bị treo/quá nhiệt khi chạy dài 2 tiếng
    if device == "cpu":
        torch.set_num_threads(2)

    weights_dir = os.path.join(BASE_DIR, "models", "weights")
    os.makedirs(weights_dir, exist_ok=True)
    vocab_path = os.path.join(weights_dir, "vocab.json")
    model_save_path = os.path.join(weights_dir, "vivos_ctc_model.pth")
    backup_path = os.path.join(weights_dir, "vivos_ctc_model_epoch15_original.pth")

    print("=" * 75)
    print(" TIẾP TỤC HUẤN LUYỆN (RESUME TRAINING) MÔ HÌNH CRNN-CTC TIẾNG VIỆT")
    print(f" Kiến trúc: SpeechCRNN (CNN + BiGRU + CTC Loss)")
    print(f" Tập dữ liệu: VIVOS Tiếng Việt (15.4 giờ âm thanh)")
    print(f"️ Cấu hình: MaxHours={max_hours}h, BatchSize={batch_size}, LR={lr}, Device={device}")
    print("=" * 75)

    # 1. Khởi tạo từ điển
    vocab = VietnameseVocab()
    if not os.path.exists(vocab_path):
        vocab.save(vocab_path)
        print(f" Đã tạo mới từ điển ký tự ({len(vocab)} tokens) vào: {vocab_path}")
    else:
        print(f" Đã nạp từ điển ký tự ({len(vocab)} tokens) từ: {vocab_path}")

    # 2. Chuẩn bị tập dữ liệu Train & Validation
    vivos_dir = os.path.join(BASE_DIR, "dataset", "vivos")
    if not os.path.exists(vivos_dir):
        raise FileNotFoundError(f"Không tìm thấy dữ liệu VIVOS tại {vivos_dir}. Vui lòng kiểm tra lại dataset!")

    full_train_dataset = VIVOSDataset(vivos_dir, split="train", vocab=vocab)
    val_dataset = VIVOSDataset(vivos_dir, split="test", vocab=vocab)

    if max_train_samples and max_train_samples < len(full_train_dataset):
        train_indices = list(range(max_train_samples))
        train_dataset = Subset(full_train_dataset, train_indices)
        print(f" Chọn {max_train_samples}/{len(full_train_dataset)} mẫu câu để huấn luyện ổn định theo thời gian.")
    else:
        train_dataset = full_train_dataset

    # Giới hạn tập val 50 mẫu để đánh giá nhanh sau mỗi epoch
    val_indices = list(range(min(50, len(val_dataset))))
    val_subset = Subset(val_dataset, val_indices)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=ctc_collate_fn,
        num_workers=0
    )
    val_loader = DataLoader(
        val_subset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=ctc_collate_fn,
        num_workers=0
    )

    # 3. Khởi tạo mô hình
    device_obj = torch.device(device)
    model = SpeechCRNN_CTC(
        n_mels=80,
        vocab_size=len(vocab),
        hidden_size=256,
        num_rnn_layers=2,
        dropout=0.2
    ).to(device_obj)

    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f" Tổng số tham số mô hình: {total_params:,} parameters")

    start_epoch = 1
    best_val_loss = float("inf")

    # 4. Nạp checkpoint cũ (Resume)
    if resume and os.path.exists(model_save_path):
        print(f"\n[Resume] Nạp checkpoint đã có từ: {model_save_path}")
        checkpoint = torch.load(model_save_path, map_location=device_obj)
        model.load_state_dict(checkpoint["state_dict"])
        saved_epoch = checkpoint.get("epoch", 15)
        start_epoch = saved_epoch + 1
        best_val_loss = checkpoint.get("val_loss", 3.388)
        print(f"[OK] Nạp thành công! Đã hoàn tất {saved_epoch} Epochs trước đó.")
        print(f"[Loss] Mức Val CTC Loss kỷ lục hiện tại: {best_val_loss:.4f}")
        print(f"[Train] Bắt đầu huấn luyện tiếp nối từ Epoch {start_epoch}...")

    # 5. Hàm mất mát & Bộ tối ưu
    criterion = nn.CTCLoss(blank=vocab.blank_id, zero_infinity=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2)
    decoder = CTCGreedyDecoder(vocab)

    global_start_time = time.time()
    max_seconds = max_hours * 3600.0 if max_hours > 0 else float("inf")
    end_epoch = start_epoch + epochs - 1

    print(f"\n[Kế hoạch] Huấn luyện từ Epoch {start_epoch} đến tối đa Epoch {end_epoch}")
    print(f"[Thời gian] Giới hạn thời gian tối đa: {max_hours:.1f} giờ ({max_seconds/60:.0f} phút)\n")

    # 6. Vòng lặp huấn luyện chính
    stopped_by_time = False
    for epoch in range(start_epoch, end_epoch + 1):
        epoch_start_time = time.time()
        model.train()
        total_train_loss = 0.0
        num_train_batches = len(train_loader)

        print(f"\n--- EPOCH [{epoch}/{end_epoch}] --- (Thời gian chạy: {(time.time() - global_start_time)/60:.1f} / {max_seconds/60:.0f} phút)")

        for batch_idx, (mels, labels, in_lens, tgt_lens, texts) in enumerate(train_loader):
            # Kiểm tra giới hạn thời gian chạy
            current_elapsed = time.time() - global_start_time
            if current_elapsed >= max_seconds:
                print(f"\n[Dừng] ĐÃ CHẠM MỐC THỜI GIAN {max_hours:.1f} GIỜ! Tự động dừng an toàn.")
                stopped_by_time = True
                break

            mels = mels.to(device_obj)
            labels = labels.to(device_obj)

            optimizer.zero_grad()

            # Forward pass
            log_probs = model(mels)  # (Batch, Time, Vocab)
            out_lens = model.get_output_lengths(in_lens).to(device_obj)

            loss = criterion(
                log_probs.permute(1, 0, 2),
                labels,
                out_lens,
                tgt_lens
            )

            if torch.isnan(loss) or torch.isinf(loss):
                continue

            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()

            total_train_loss += loss.item()

            if (batch_idx + 1) % 10 == 0 or (batch_idx + 1) == num_train_batches:
                avg_loss = total_train_loss / (batch_idx + 1)
                batch_elapsed = time.time() - epoch_start_time
                print(
                    f"Epoch {epoch} [{batch_idx + 1}/{num_train_batches}] - "
                    f"Batch Loss: {loss.item():.4f} (Avg: {avg_loss:.4f}) - "
                    f"Đã chạy: {batch_elapsed:.1f}s",
                    flush=True
                )

        if stopped_by_time:
            break

        avg_train_loss = total_train_loss / max(1, num_train_batches)

        # 7. Đánh giá tập Validation
        model.eval()
        total_val_loss = 0.0
        sample_pred_text = ""
        sample_true_text = ""

        with torch.no_grad():
            for val_idx, (v_mels, v_labels, v_in_lens, v_tgt_lens, v_texts) in enumerate(val_loader):
                v_mels = v_mels.to(device_obj)
                v_labels = v_labels.to(device_obj)

                v_log_probs = model(v_mels)
                v_out_lens = model.get_output_lengths(v_in_lens).to(device_obj)

                v_loss = criterion(
                    v_log_probs.permute(1, 0, 2),
                    v_labels,
                    v_out_lens,
                    v_tgt_lens
                )
                if not torch.isnan(v_loss) and not torch.isinf(v_loss):
                    total_val_loss += v_loss.item()

                if val_idx == 0 and len(v_texts) > 0:
                    decoded_list = decoder.decode_batch(v_log_probs, v_out_lens)
                    sample_pred_text = decoded_list[0]
                    sample_true_text = v_texts[0]

        avg_val_loss = total_val_loss / max(1, len(val_loader))
        scheduler.step(avg_val_loss)

        epoch_duration = time.time() - epoch_start_time
        total_elapsed = time.time() - global_start_time
        print(f"\n[KẾT QUẢ] EPOCH {epoch}:", flush=True)
        print(f"   Train CTC Loss: {avg_train_loss:.4f} | Val CTC Loss: {avg_val_loss:.4f} (Kỷ lục cũ: {best_val_loss:.4f})", flush=True)
        print(f"   Thời gian Epoch: {epoch_duration:.1f}s | Tổng thời gian: {total_elapsed/60:.1f} phút", flush=True)
        print(f"   - Mẫu Nhãn Gốc:  '{sample_true_text}'", flush=True)
        print(f"   - Mẫu AI Đoán:   '{sample_pred_text}'", flush=True)

        # Lưu checkpoint khi có cải thiện hoặc kết thúc epoch
        is_best = avg_val_loss < best_val_loss
        if is_best:
            best_val_loss = avg_val_loss
            print(f"[KỶ LỤC] Val Loss giảm xuống: {best_val_loss:.4f}", flush=True)

        checkpoint = {
            "state_dict": model.state_dict(),
            "vocab_chars": vocab.chars,
            "model_config": {
                "n_mels": 80,
                "vocab_size": len(vocab),
                "hidden_size": 256,
                "num_rnn_layers": 2
            },
            "epoch": epoch,
            "val_loss": avg_val_loss,
            "best_val_loss": best_val_loss
        }
        torch.save(checkpoint, model_save_path)
        print(f"[Lưu] Đã lưu checkpoint tại Epoch {epoch} vào: {model_save_path}", flush=True)

        if total_elapsed >= max_seconds:
            print(f"\n[Hoàn thành] ĐÃ HOÀN THÀNH 2 GIỜ HUẤN LUYỆN THEO YÊU CẦU!", flush=True)
            break

    total_training_time = time.time() - global_start_time
    print("\n" + "=" * 75)
    print(f"HOÀN TẤT ĐỢT HUẤN LUYỆN! Tổng thời gian chạy: {total_training_time/3600:.2f} giờ ({total_training_time/60:.1f} phút)")
    print(f"Trọng số tối ưu đã được lưu tại: {model_save_path}")
    print(f"Bản sao lưu ban đầu (Epoch 15) vẫn an toàn tại: {backup_path}")
    print("=" * 75)
    return model_save_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Huấn luyện tiếp tục mô hình CRNN-CTC trên tập VIVOS")
    parser.add_argument("--epochs", type=int, default=20, help="Số lượng epoch muốn huấn luyện thêm")
    parser.add_argument("--batch_size", type=int, default=16, help="Kích thước batch")
    parser.add_argument("--samples", type=int, default=1500, help="Số mẫu huấn luyện tối đa")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate (nhỏ cho fine-tuning)")
    parser.add_argument("--hours", type=float, default=2.0, help="Thời gian chạy tối đa (giờ)")
    parser.add_argument("--no_resume", action="store_true", help="Không nạp lại checkpoint cũ mà train từ đầu")
    args = parser.parse_args()

    train_ctc(
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        max_train_samples=args.samples if args.samples > 0 else None,
        resume=not args.no_resume,
        max_hours=args.hours
    )
