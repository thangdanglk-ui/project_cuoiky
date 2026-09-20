import os
import sys
import ssl
import time
import tarfile
import urllib.request

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
VIVOS_DIR = os.path.join(DATASET_DIR, "vivos")
ARCHIVE_PATH = os.path.join(DATASET_DIR, "vivos.tar.gz")

URL = "https://huggingface.co/datasets/vivos/resolve/main/data/vivos.tar.gz"

def download_vivos():
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    # Kiểm tra xem VIVOS đã giải nén chưa
    train_prompts = os.path.join(VIVOS_DIR, "train", "prompts.txt")
    if os.path.exists(train_prompts):
        print(f"[OK] Tập dữ liệu VIVOS đã tồn tại tại: {VIVOS_DIR}")
        return True

    print("=" * 70)
    print("BẮT ĐẦU TẢI TẬP DỮ LIỆU VIVOS TIẾNG VIỆT (~1.37 GB)")
    print(f"Nguồn: {URL}")
    print(f"Đích: {ARCHIVE_PATH}")
    print("=" * 70)

    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )

    try:
        response = urllib.request.urlopen(req, context=ctx, timeout=30)
        total_size = int(response.headers.get("content-length", 0))
        print(f"Tổng dung lượng cần tải: {total_size / (1024 * 1024):.2f} MB")

        chunk_size = 1024 * 1024  # 1MB chunks
        downloaded = 0
        start_time = time.time()
        last_print_time = start_time

        with open(ARCHIVE_PATH, "wb") as f:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                current_time = time.time()
                if current_time - last_print_time >= 3.0 or downloaded == total_size:
                    elapsed = current_time - start_time
                    speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                    percent = (downloaded / total_size * 100) if total_size > 0 else 0
                    print(
                        f"Đã tải: {downloaded / (1024*1024):.1f}/{total_size / (1024*1024):.1f} MB "
                        f"({percent:.1f}%) - Tốc độ: {speed:.2f} MB/s"
                    )
                    last_print_time = current_time

        print("[OK] Tải hoàn tất file nén vivos.tar.gz!")
    except Exception as e:
        print(f"[Lỗi] Lỗi tải dữ liệu: {e}")
        return False

    print("\nĐang giải nén vivos.tar.gz vào thư mục dataset/...")
    try:
        with tarfile.open(ARCHIVE_PATH, "r:gz") as tar:
            tar.extractall(path=DATASET_DIR)
        print(f"[OK] Giải nén thành công! Dữ liệu nằm tại: {VIVOS_DIR}")

        # Xóa file tar.gz để tiết kiệm 1.37GB dung lượng đĩa
        if os.path.exists(ARCHIVE_PATH):
            os.remove(ARCHIVE_PATH)
            print("Đã dọn dẹp file nén vivos.tar.gz")
        return True
    except Exception as e:
        print(f"[Lỗi] Lỗi giải nén: {e}")
        return False

if __name__ == "__main__":
    success = download_vivos()
    if success:
        train_prompts = os.path.join(VIVOS_DIR, "train", "prompts.txt")
        test_prompts = os.path.join(VIVOS_DIR, "test", "prompts.txt")
        print("\n--- KIỂM TRA TẬP DỮ LIỆU ---")
        if os.path.exists(train_prompts):
            with open(train_prompts, "r", encoding="utf-8") as f:
                lines = f.readlines()
            print(f"- Tập Huấn luyện (Train): {len(lines)} câu có nhãn")
            print(f"   Ví dụ câu đầu tiên: {lines[0].strip()}")
        if os.path.exists(test_prompts):
            with open(test_prompts, "r", encoding="utf-8") as f:
                lines = f.readlines()
            print(f"- Tập Kiểm thử (Test): {len(lines)} câu có nhãn")
            print(f"   Ví dụ câu đầu tiên: {lines[0].strip()}")
