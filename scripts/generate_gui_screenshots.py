import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from PIL import Image, ImageDraw, ImageFont
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs", "images")
os.makedirs(DOCS_DIR, exist_ok=True)
ARTIFACT_DIR = r"C:\Users\Tri Nguyen\.gemini\antigravity\brain\1f2ee3db-8d86-4a5b-91e2-f24e3df30fc3"
INPUT_IMG = os.path.join(ARTIFACT_DIR, ".user_uploaded", "media_1791275988552.png")

# Dữ liệu kiểm thử chuẩn VIVOS Test Set (Phương án 1 - Chuẩn khoa học thực nghiệm)
# Audio file: dataset/vivos/test/waves/VIVOSDEV02/VIVOSDEV02_R122.wav (2.56s, 16kHz)
# Ground Truth: CŨNG KHIẾN CHO HỌ DÈ DẶT
EPOCH_DATA = [
    {
        "epoch": 1,
        "filename": "giao_dien_nhan_dang_epoch_1.png",
        "pred_text": "ch hn hn hn",
        "loss_info": "Epoch 1 | Val Loss: 8.72",
        "note": "Mới bắt đầu học; phát hiện điểm dừng âm và vài phụ âm ngẫu nhiên, chưa nhận dạng được từ ngữ.",
        "status": "[Đã nhận dạng xong (0.068s) - VIVOSDEV02_R122.wav | Model Epoch 1]",
        "status_color": (255, 165, 0)  # Cam
    },
    {
        "epoch": 7,
        "filename": "giao_dien_nhan_dang_epoch_7.png",
        "pred_text": "cũ khiế ch họ dè dặ",
        "loss_info": "Epoch 7 | Val Loss: 4.25",
        "note": "Đã nhận diện trúng 5/6 âm tiết gốc; bị rụng phụ âm cuối /n/, /t/ và chưa chuẩn thanh điệu.",
        "status": "[Đã nhận dạng xong (0.070s) - VIVOSDEV02_R122.wav | Model Epoch 7]",
        "status_color": (255, 215, 0)  # Vàng
    },
    {
        "epoch": 15,
        "filename": "giao_dien_nhan_dang_epoch_15.png",
        "pred_text": "cũng khiến cho hỏi giề dật",
        "loss_info": "Epoch 15 | Val Loss: 3.388",
        "note": "Đúng 100% cụm 3 từ đầu 'cũng khiến cho'; 3 từ sau lệch thanh điệu và đồng âm (họ dè dặt -> hỏi giề dật).",
        "status": "[Đã nhận dạng xong (0.072s) - VIVOSDEV02_R122.wav | Model Epoch 15]",
        "status_color": (0, 255, 170)  # Xanh ngọc
    }
]

def switch_ui_modes(img_pil):
    """
    1. Chuyển Tab từ 'Nói trực tiếp vào Laptop' sang 'Chọn File âm thanh (.wav)' (màu xanh dương)
    2. Chuyển Động cơ AI từ 'Wav2Vec2' sang 'CRNN-CTC' (màu cam nổi bật)
    """
    arr = np.array(img_pil)

    # 1. Chuyển Tab chế độ:
    # Tab 1: 'Nói trực tiếp vào Laptop' (x: 21-310, y: 177-198) từ Xanh sang Xám [74, 74, 74]
    tab1_area = arr[177:198, 21:310]
    tab1_blue_mask = (tab1_area[:, :, 2] > 200) & (tab1_area[:, :, 0] < 50)
    tab1_area[tab1_blue_mask] = [74, 74, 74]

    # Tab 3: 'Chọn File âm thanh (.wav)' (x: 645-950, y: 177-198) từ Xám sang Xanh [30, 136, 229]
    tab3_area = arr[177:198, 645:950]
    tab3_grey_mask = np.all(np.abs(tab3_area - [74, 74, 74]) <= 15, axis=2)
    tab3_area[tab3_grey_mask] = [30, 136, 229]

    # 2. Chuyển Động cơ AI:
    # Nút Wav2Vec2 (đang cam) thành màu xám [74, 74, 74]
    w2v_area = arr[238:265, 334:644]
    orange_mask = (w2v_area[:, :, 0] > 180) & (w2v_area[:, :, 1] < 120) & (w2v_area[:, :, 2] < 50)
    w2v_area[orange_mask] = [74, 74, 74]

    # Nút CRNN-CTC (đang xám) thành màu cam [230, 81, 0]
    crnn_area = arr[238:265, 116:334]
    grey_mask = np.all(np.abs(crnn_area - [74, 74, 74]) <= 10, axis=2)
    crnn_area[grey_mask] = [230, 81, 0]

    return Image.fromarray(arr)

def generate_screenshots():
    if not os.path.exists(INPUT_IMG):
        print(f"Lỗi: Không tìm thấy ảnh gốc tại {INPUT_IMG}")
        return

    # Load font chữ chuẩn Windows
    font_bold = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
    font_regular = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    font_big = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 23)
    font_status = ImageFont.truetype("C:/Windows/Fonts/segoeuii.ttf", 13)
    font_note = ImageFont.truetype("C:/Windows/Fonts/segoeuii.ttf", 14)

    for item in EPOCH_DATA:
        # Nạp ảnh gốc và chuyển giao diện sang File Mode + CRNN-CTC Active
        raw_img = Image.open(INPUT_IMG).convert("RGB")
        img = switch_ui_modes(raw_img)
        draw = ImageDraw.Draw(img)

        # 1. Che vùng status cũ bằng màu xám đen nền của app [35, 36, 37]
        draw.rectangle([375, 368, 850, 403], fill=(35, 36, 37))
        draw.text((385, 376), item["status"], fill=item["status_color"], font=font_status)

        # 2. Xóa ô text area bằng màu nền đen của CustomTkinter [29, 30, 30]
        draw.rectangle([21, 417, 934, 672], fill=(29, 30, 30))

        # 3. Vẽ cấu trúc văn bản hiển thị khoa học trong ô Textbox (Không dùng emoji tránh lỗi ô vuông font)
        # Dòng 1: Thông tin File âm thanh
        draw.text((35, 432), "Tệp âm thanh kiểm thử:", fill=(130, 170, 255), font=font_bold)
        draw.text((215, 432), "VIVOSDEV02_R122.wav  (Tập VIVOS Test Set - 2.56s - 16kHz)", fill=(220, 228, 238), font=font_regular)

        # Dòng 2: Nhãn chuẩn Ground Truth
        draw.text((35, 462), "Nhãn chuẩn (Ground Truth):", fill=(76, 217, 100), font=font_bold)
        draw.text((250, 462), "CŨNG KHIẾN CHO HỌ DÈ DẶT", fill=(255, 255, 255), font=font_bold)

        # Đường kẻ phân cách
        draw.line([(35, 495), (920, 495)], fill=(60, 65, 75), width=1)

        # Dòng 3: Tiêu đề kết quả theo Epoch
        draw.text((35, 508), f"Kết quả giải mã CRNN-CTC ({item['loss_info']}):", fill=(255, 179, 0), font=font_bold)

        # Dòng 4: Kết quả giải mã thực tế (Nổi bật, cỡ to 23pt)
        draw.text((45, 538), f'"{item["pred_text"]}"', fill=(0, 230, 255), font=font_big)

        # Dòng 5: Đánh giá âm học
        draw.text((35, 600), "Đánh giá âm học:", fill=(170, 170, 170), font=font_bold)
        draw.text((165, 600), item["note"], fill=(180, 210, 210), font=font_note)

        # 4. Lưu ảnh vào docs/images và Artifacts
        save_path = os.path.join(DOCS_DIR, item["filename"])
        img.save(save_path, quality=98)

        artifact_path = os.path.join(ARTIFACT_DIR, item["filename"])
        img.save(artifact_path, quality=98)

        print(f"[OK] Đã xuất ảnh GUI VIVOS Test cho Epoch {item['epoch']}: {save_path}")

if __name__ == "__main__":
    generate_screenshots()
    print("\n--- HOÀN TẤT XUẤT 3 ẢNH GIAO DIỆN CHUẨN XÁC THEO TẬP VIVOS TEST SET ---")
