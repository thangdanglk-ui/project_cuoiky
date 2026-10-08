import os
import sys
import re
import io
import unicodedata
import requests
import urllib3
import soundfile as sf
import librosa
import pyarrow.parquet as pq

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

urllib3.disable_warnings()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models.vocab import VietnameseVocab

def clean_transcript(text):
    text = unicodedata.normalize('NFC', text)
    # Loại bỏ dấu câu đặc biệt, giữ lại chữ cái và khoảng trắng
    text = re.sub(r'[^\w\s]', ' ', text)
    # Gộp các khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

def download_and_prepare_common_voice(target_samples=1000):
    output_dir = os.path.join(BASE_DIR, "dataset", "common_voice_vi")
    waves_dir = os.path.join(output_dir, "waves")
    os.makedirs(waves_dir, exist_ok=True)
    prompts_path = os.path.join(output_dir, "prompts.txt")
    readme_path = os.path.join(output_dir, "README.md")
    
    vocab = VietnameseVocab()
    print("=" * 70)
    print("TẢI VÀ TIỀN XỬ LÝ TẬP DỮ LIỆU MOZILLA COMMON VOICE TIẾNG VIỆT")
    print(f"Thư mục lưu trữ bằng chứng: {output_dir}")
    print(f"Mục tiêu số lượng mẫu: {target_samples} câu âm thanh chuẩn 16kHz")
    print("=" * 70)

    urls = [
        ("validation", "https://huggingface.co/datasets/tsdocode/common_voice_13_0_vi_pseudo_labelled/resolve/main/vi/validation-00000-of-00001.parquet"),
        ("train", "https://huggingface.co/datasets/tsdocode/common_voice_13_0_vi_pseudo_labelled/resolve/main/vi/train-00000-of-00001.parquet")
    ]

    saved_samples = []
    sample_idx = 1

    for split_name, url in urls:
        if len(saved_samples) >= target_samples:
            break
        print(f"\n[1/3] Đang tải phân đoạn '{split_name}' từ Hugging Face...")
        r = requests.get(url, verify=False, stream=True)
        if r.status_code != 200:
            print(f"[Cảnh báo] Không thể tải {url} (Status: {r.status_code})")
            continue
        
        content_bytes = io.BytesIO(r.content)
        table = pq.read_table(content_bytes)
        pydict = table.to_pydict()
        total_rows = len(pydict['sentence'])
        print(f"[2/3] Đã nạp bảng dữ liệu '{split_name}': {total_rows} mẫu. Bắt đầu chuẩn hóa âm thanh...")

        for i in range(total_rows):
            if len(saved_samples) >= target_samples:
                break
            
            raw_text = pydict['sentence'][i]
            clean_text = clean_transcript(raw_text)

            # Kiểm tra xem văn bản có hợp lệ với từ điển 105 tokens không
            if not clean_text or not all(c in vocab.char2idx for c in clean_text):
                continue

            audio_info = pydict['audio'][i]
            audio_bytes = audio_info.get('bytes') if isinstance(audio_info, dict) else None
            if not audio_bytes:
                continue

            try:
                # Đọc giải mã âm thanh
                data, sr = sf.read(io.BytesIO(audio_bytes))
                # Chuyển stereo -> mono nếu cần
                if data.ndim > 1:
                    data = data.mean(axis=1)
                # Resample về 16kHz
                if sr != 16000:
                    data = librosa.resample(data, orig_sr=sr, target_sr=16000)
                
                # Bỏ qua các file quá ngắn (< 0.5s) hoặc quá dài (> 15s)
                duration = len(data) / 16000.0
                if duration < 0.5 or duration > 15.0:
                    continue

                file_id = f"cv_vi_{sample_idx:05d}"
                wav_filename = f"{file_id}.wav"
                wav_path = os.path.join(waves_dir, wav_filename)

                # Lưu file WAV chuẩn 16-bit PCM 16kHz Mono
                sf.write(wav_path, data, 16000, subtype='PCM_16')
                saved_samples.append((file_id, clean_text, duration))
                sample_idx += 1

                if len(saved_samples) % 100 == 0 or len(saved_samples) == target_samples:
                    print(f"   -> Đã xử lý và lưu thành công {len(saved_samples)}/{target_samples} mẫu...")

            except Exception as e:
                continue

    # [3/3] Ghi tệp prompts.txt
    print(f"\n[3/3] Đang tạo tệp nhãn prompts.txt tại: {prompts_path}")
    with open(prompts_path, "w", encoding="utf-8") as f:
        for fid, text, _ in saved_samples:
            f.write(f"{fid} {text}\n")

    # Tạo tệp README.md làm chứng từ học thuật
    total_duration_sec = sum(d for _, _, d in saved_samples)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# BỘ DỮ LIỆU MOZILLA COMMON VOICE TIẾNG VIỆT (EVIDENCE CORPUS)\n\n")
        f.write("## 1. Thông tin nguồn gốc dữ liệu\n")
        f.write("- **Tên tập dữ liệu:** Mozilla Common Voice Vietnamese (Corpus v13.0)\n")
        f.write("- **Nguồn thu thập:** Cộng đồng Mozilla Common Voice & Hugging Face Repository (`tsdocode/common_voice_13_0_vi_pseudo_labelled`)\n")
        f.write(f"- **Tổng số mẫu âm thanh đã chuẩn hóa:** {len(saved_samples):,} câu\n")
        f.write(f"- **Tổng thời lượng âm thanh:** {total_duration_sec/3600:.2f} giờ ({total_duration_sec/60:.1f} phút)\n")
        f.write("- **Định dạng âm thanh:** 16,000 Hz, Mono (1 kênh), 16-bit Linear PCM WAV\n")
        f.write("- **Chuẩn hóa nhãn văn bản:** Unicode dựng sẵn (NFC), chữ thường, loại bỏ ký tự lạ, tương thích 100% với `VietnameseVocab` (105 tokens)\n\n")
        f.write("## 2. Cấu trúc thư mục\n")
        f.write("- `waves/`: Chứa các tệp âm thanh `.wav` đã được resample chuẩn 16kHz\n")
        f.write("- `prompts.txt`: Danh sách cặp `file_id transcript` phục vụ huấn luyện và đánh giá\n\n")
        f.write("## 3. Mục đích sử dụng trong đồ án\n")
        f.write("Bộ dữ liệu này được nhóm nghiên cứu tải về và lưu trữ trực tiếp trong dự án để phục vụ:\n")
        f.write("1. **Huấn luyện mở rộng miền (Domain Adaptation):** Giúp mô hình Dual-Attention ACRNN học thêm đa dạng giọng nói cộng đồng.\n")
        f.write("2. **Bằng chứng học thuật:** Minh chứng với Hội đồng chấm thi về năng lực mở rộng đa tập dữ liệu (Multi-corpus generalization) của nhóm.\n")

    print("=" * 70)
    print("HOÀN TẤT TẢI VÀ CHUẨN HÓA BỘ DỮ LIỆU COMMON VOICE!")
    print(f"Tổng số mẫu âm thanh thu thập được: {len(saved_samples)} mẫu")
    print(f"Tổng thời lượng: {total_duration_sec/60:.1f} phút")
    print(f"File nhãn: {prompts_path}")
    print(f"Chứng từ: {readme_path}")
    print("=" * 70)
    return len(saved_samples)

if __name__ == "__main__":
    download_and_prepare_common_voice(target_samples=1000)
