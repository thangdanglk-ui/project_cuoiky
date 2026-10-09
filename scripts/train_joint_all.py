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

def train_joint_all(epochs=10, batch_size=32, lr=1e-4, max_vivos_samples=None, device=None, resume=True, max_hours=3.0):
    """
    Huấn luyện liên kết đa ngữ liệu (Multi-corpus Joint Training):
    Hợp nhất toàn bộ tập VIVOS và Mozilla Common Voice vào một pipeline thống nhất.
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        torch.set_num_threads(2)
    device_obj = torch.device(device)

    weights_dir = os.path.join(BASE_DIR, "models", "weights")
    os.makedirs(weights_dir, exist_ok=True)
    vocab_path = os.path.join(weights_dir, "vocab.json")
    model_save_path = os.path.join(weights_dir, "vivos_ctc_model.pth")

    vocab = VietnameseVocab()
    if not os.path.exists(vocab_path):
        vocab.save(vocab_path)

    print("=" * 80)
    print(" HUẤN LUYỆN LIÊN KẾT ĐA NGỮ LIỆU TOÀN PHẦN (JOINT MULTI-CORPUS TRAINING)")
    print(" Mô hình kiến trúc: Dual-Attention ACRNN (SE-Block + Multi-Head Self-Attention)")
    print(" Tập dữ liệu 1: VIVOS Tiếng Việt (15.4 giờ)")
    print(" Tập dữ liệu 2: Mozilla Common Voice Tiếng Việt 16kHz")
    print(f" Cấu hình: Device={device.upper()}, Epochs={epochs}, BatchSize={batch_size}, LR={lr}")
    print("=" * 80)

    # 1. Nạp tập Common Voice
    cv_dir = os.path.join(BASE_DIR, "dataset", "common_voice_vi")
    if not os.path.exists(cv_dir):
        raise FileNotFoundError(f"Không tìm thấy thư mục {cv_dir}!")
    
    cv_train = CommonVoiceDataset(cv_dir=cv_dir, split="train", vocab=vocab)
    cv_test = CommonVoiceDataset(cv_dir=cv_dir, split="test", vocab=vocab)
    print(f"[1/4] Đã nạp Common Voice: {len(cv_train)} câu Train | {len(cv_test)} câu Validation")

    # 2. Nạp tập VIVOS
    vivos_dir = os.path.join(BASE_DIR, "dataset", "vivos")
    vivos_train_prompts = os.path.join(vivos_dir, "train", "prompts.txt")
    if not os.path.exists(vivos_train_prompts):
        print("\n[CẢNH BÁO] Không tìm thấy VIVOS tại dataset/vivos!")
        print("Vui lòng chạy: python scripts/prepare_vivos.py để tải và giải nén VIVOS trước!")
        return

    vivos_train_full = VIVOSDataset(vivos_dir, split="train", vocab=vocab)
    vivos_test_full = VIVOSDataset(vivos_dir, split="test", vocab=vocab)

    if max_vivos_samples and max_vivos_samples < len(vivos_train_full):
        vivos_train = Subset(vivos_train_full, list(range(max_vivos_samples)))
        print(f"[2/4] Đã chọn lọc {max_vivos_samples}/{len(vivos_train_full)} câu VIVOS Train.")
    else:
        vivos_train = vivos_train_full
        print(f"[2/4] Đã nạp toàn bộ {len(vivos_train)} câu VIVOS Train!")

    # 3. Hợp nhất hai tập Train & Test
    joint_train_dataset = ConcatDataset([vivos_train, cv_train])
    # Val set: 100 câu Common Voice + 100 câu VIVOS
    vivos_val_sub = Subset(vivos_test_full, list(range(min(100, len(vivos_test_full)))))
    joint_val_dataset = ConcatDataset([vivos_val_sub, cv_test])

    print(f"\n[HỢP NHẤT THÀNH CÔNG]:")
    print(f"   Tổng số mẫu Huấn luyện: {len(joint_train_dataset):,} câu (VIVOS: {len(vivos_train):,} + Common Voice: {len(cv_train):,})")
    print(f"   Tổng số mẫu Kiểm thử:   {len(joint_val_dataset):,} câu")

    train_loader = DataLoader(
        joint_train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=ctc_collate_fn,
        num_workers=2 if device == "cuda" else 0,
        pin_memory=True if device == "cuda" else False
    )
    val_loader = DataLoader(
        joint_val_dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=ctc_collate_fn,
        num_workers=0
    )

    # 4. Khởi tạo mô hình
    model = SpeechCRNN_CTC(n_mels=80, vocab_size=len(vocab)).to(device_obj)
    start_epoch = 1
    best_val_loss = float("inf")

    # Nạp checkpoint nếu có
    if resume and (os.path.exists(model_save_path) or os.path.exists(base_model_path)):
        ckpt_path = model_save_path if os.path.exists(model_save_path) else base_model_path
        try:
            ckpt = torch.load(ckpt_path, map_location=device_obj)
            model.load_state_dict(ckpt["state_dict"])
            saved_loss = ckpt.get("val_loss", None)
            if saved_loss is not None:
                best_val_loss = float(saved_loss)
            print(f"\n[Kế thừa] Nạp trọng số ACRNN từ {ckpt_path} (Val Loss kỷ lục: {best_val_loss:.4f})")
        except Exception as e:
            print(f"[Ghi chú] Khởi tạo trọng số ngẫu nhiên: {e}")

    criterion = nn.CTCLoss(blank=vocab.blank_id, zero_infinity=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2)
    decoder = CTCGreedyDecoder(vocab)

    num_batches = len(train_loader)
    global_start = time.time()
    max_seconds = max_hours * 3600.0
    history = {"epochs": [], "train_loss": [], "val_loss": []}

    print(f"\n[Bắt đầu] Chạy {epochs} Epochs liên kết ({num_batches} batches/epoch)...")
    for epoch in range(start_epoch, start_epoch + epochs):
        if time.time() - global_start >= max_seconds:
            print(f"[Dừng] Đạt giới hạn thời gian tối đa {max_hours} giờ!")
            break

        model.train()
        total_train_loss = 0.0
        ep_start = time.time()

        for b_idx, (mels, labels, in_lens, tgt_lens, texts) in enumerate(train_loader):
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

            total_train_loss += loss.item()

            if (b_idx + 1) % 50 == 0 or (b_idx + 1) == num_batches:
                cur_avg = total_train_loss / (b_idx + 1)
                elapsed = time.time() - ep_start
                print(f"Epoch [{epoch}/{start_epoch + epochs - 1}] Batch [{b_idx+1}/{num_batches}] - Loss: {loss.item():.4f} (Avg: {cur_avg:.4f}) - Thời gian: {elapsed:.1f}s", flush=True)

        avg_train_loss = total_train_loss / max(1, num_batches)

        # Validation
        model.eval()
        total_val_loss = 0.0
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
                    total_val_loss += vl.item()

                if v_idx == 0 and len(v_texts) > 0:
                    decoded = decoder.decode_batch(v_log_probs, v_out_lens)
                    sample_pred = decoded[0]
                    sample_true = v_texts[0]

        avg_val_loss = total_val_loss / max(1, len(val_loader))
        scheduler.step(avg_val_loss)

        ep_duration = time.time() - ep_start
        print(f"\n--- [KẾT QUẢ EPOCH {epoch}] ---", flush=True)
        print(f"   Train Loss: {avg_train_loss:.4f} | Joint Val Loss: {avg_val_loss:.4f} (Kỷ lục: {best_val_loss:.4f})", flush=True)
        print(f"   Thời gian Epoch: {ep_duration:.1f}s | Đã chạy: {(time.time() - global_start)/60:.1f} phút", flush=True)
        print(f"   - Mẫu Ground Truth: '{sample_true}'", flush=True)
        print(f"   - Mẫu AI Dự đoán:   '{sample_pred}'", flush=True)

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            print(f"⭐ [KỶ LỤC MỚI] Val Loss giảm xuống: {best_val_loss:.4f}!", flush=True)

        # Lưu checkpoint
        ckpt = {
            "state_dict": model.state_dict(),
            "vocab_chars": vocab.chars,
            "model_config": {
                "n_mels": 80,
                "vocab_size": len(vocab),
                "hidden_size": 256,
                "num_rnn_layers": 2
            },
            "dataset": "Joint VIVOS + Mozilla Common Voice 13.0 Vietnamese",
            "val_loss": avg_val_loss,
            "best_val_loss": best_val_loss,
            "base_model": "Dual-Attention ACRNN"
        }
        torch.save(ckpt, model_save_path)
        print(f"[LƯU TRỮ] Đã lưu trọng số vào {model_save_path}\n", flush=True)

        history["epochs"].append(epoch)
        history["train_loss"].append(round(avg_train_loss, 4))
        history["val_loss"].append(round(avg_val_loss, 4))

    # Lưu lịch sử Loss vào JSON
    import json
    history_file = os.path.join(weights_dir, "train_joint_history.json")
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"[LỊCH SỬ] Đã lưu bảng số liệu Loss vào: {history_file}")

    # Tự động vẽ biểu đồ Train Loss vs Val Loss để đưa vào báo cáo
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 6), dpi=150)
        eps = history["epochs"]
        t_losses = history["train_loss"]
        v_losses = history["val_loss"]

        plt.plot(eps, t_losses, "o-", color="#1E88E5", linewidth=2.2, label="Train CTC Loss (Tập huấn luyện)")
        plt.plot(eps, v_losses, "s--", color="#E53935", linewidth=2.2, label="Validation CTC Loss (Tập kiểm chứng)")

        best_idx = v_losses.index(min(v_losses))
        plt.plot(eps[best_idx], v_losses[best_idx], "r*", markersize=14, label=f"Điểm tối ưu (Epoch {eps[best_idx]}, Val Loss={v_losses[best_idx]})")
        plt.annotate(
            f"Điểm tối ưu: {v_losses[best_idx]}\n(Tránh Overfitting)",
            xy=(eps[best_idx], v_losses[best_idx]),
            xytext=(eps[best_idx], v_losses[best_idx] + 0.3),
            arrowprops=dict(facecolor="#D32F2F", shrink=0.08, width=1.5, headwidth=6),
            fontweight="bold", color="#B71C1C", fontsize=9.5, ha="center"
        )

        plt.title("ĐỒ THỊ THEO DÕI HỘI TỤ VÀ KIỂM SOÁT OVERFITTING QUA CÁC EPOCH\n(Mô hình Dual-Attention ACRNN trên tập VIVOS + Mozilla Common Voice)", fontsize=11.5, fontweight="bold", pad=12)
        plt.xlabel("Số lượng Epochs", fontsize=10, fontweight="bold")
        plt.ylabel("Hàm mất mát CTC Loss", fontsize=10, fontweight="bold")
        plt.grid(True, linestyle=":", alpha=0.7)
        plt.legend(fontsize=10, loc="upper right")
        plt.tight_layout()

        chart_path = os.path.join(weights_dir, "loss_overfitting_chart.png")
        plt.savefig(chart_path)
        plt.close()
        print(f"⭐ [BIỂU ĐỒ BÁO CÁO] Đã tạo thành công biểu đồ kiểm soát Overfitting tại: {chart_path}")
    except Exception as e:
        print(f"[Ghi chú vẽ đồ thị]: {e}")

    print("=" * 80)
    print(f"HOÀN TẤT HUẤN LUYỆN LIÊN KẾT ĐA NGỮ LIỆU! Tổng thời gian: {(time.time() - global_start)/60:.1f} phút")
    print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Huấn luyện liên kết toàn phần VIVOS + Common Voice")
    parser.add_argument("--epochs", type=int, default=10, help="Số epochs huấn luyện")
    parser.add_argument("--batch_size", type=int, default=32, help="Kích thước batch (khuyên dùng 32 trên GPU)")
    parser.add_argument("--lr", type=float, default=1e-4, help="Tốc độ học")
    parser.add_argument("--max_vivos", type=int, default=None, help="Giới hạn câu VIVOS (None = Toàn bộ 11.660 câu)")
    parser.add_argument("--hours", type=float, default=3.0, help="Thời gian tối đa (giờ)")
    parser.add_argument("--device", type=str, default=None, help="cuda hoặc cpu")
    parser.add_argument("--no_resume", action="store_true", help="Không nạp checkpoint cũ mà train từ đầu")
    args = parser.parse_args()

    train_joint_all(
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        max_vivos_samples=args.max_vivos,
        device=args.device,
        resume=not args.no_resume,
        max_hours=args.hours
    )
