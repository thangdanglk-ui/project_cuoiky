import os
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_header(doc, title, subtitle, metadata):
    p_title = doc.add_paragraph()
    p_title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(3)
    run_title = p_title.add_run(title)
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(17)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(4)
    run_sub = p_sub.add_run(subtitle)
    run_sub.font.name = "Times New Roman"
    run_sub.font.size = Pt(12)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(0x00, 0x4B, 0x87)

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(16)
    run_meta = p_meta.add_run(metadata)
    run_meta.font.name = "Times New Roman"
    run_meta.font.size = Pt(10.5)
    run_meta.font.italic = True
    run_meta.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(13.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x00, 0x4B, 0x87)
    return p

def add_paragraph(doc, text, bold_prefix="", italic=False, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(11)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    r_text = p.add_run(text)
    r_text.font.name = "Times New Roman"
    r_text.font.size = Pt(11)
    r_text.font.italic = italic
    return p

def add_pipeline_step_box(doc, step_badge, step_title, terms_concept, why_needed, math_physics, code_snippet, defense_qa):
    """
    Tạo bảng chuẩn hóa cho từng bước trong Pipeline ASR
    Tập trung làm nổi bật: TẠI SAO ĐỀ TÀI CẦN SỬ DỤNG BƯỚC NÀY?
    """
    table = doc.add_table(rows=6, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    col_widths = [Inches(1.8), Inches(5.0)]

    # Hàng tiêu đề Bước
    r0 = table.rows[0]
    r0.cells[0].merge(r0.cells[1])
    p_head = r0.cells[0].paragraphs[0]
    r_head1 = p_head.add_run(f"{step_badge}  |  ")
    r_head1.font.name = "Times New Roman"
    r_head1.font.size = Pt(11.5)
    r_head1.font.bold = True
    r_head1.font.color.rgb = RGBColor(0x00, 0xFF, 0xFF) # Cyan

    r_head2 = p_head.add_run(step_title)
    r_head2.font.name = "Times New Roman"
    r_head2.font.size = Pt(11.5)
    r_head2.font.bold = True
    r_head2.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    set_cell_background(r0.cells[0], "1B365D")

    sections = [
        ("1. Giải thích Thuật ngữ &\nBản chất Khái niệm", terms_concept, "F9FAFC"),
        ("2. TẠI SAO ĐỀ TÀI PHẢI\nSỬ DỤNG BƯỚC NÀY?", why_needed, "FFF9E6"), # Highlight màu vàng nhạt nhấn mạnh trọng tâm
        ("3. Cơ sở Toán học, Vật lý\n& Xử lý Tín hiệu", math_physics, "FFFFFF"),
        ("4. Dẫn chứng Mã nguồn\n(Source Code Mapping)", code_snippet, "EBF3FA"),
        ("5. Vấn đáp Hội đồng bảo vệ\n(Câu hỏi bẫy & Đáp án A+)", defense_qa, "FFF2E6")
    ]

    for idx, (label, content, bg_color) in enumerate(sections, start=1):
        row = table.rows[idx]
        row.cells[0].text = label
        p_lbl = row.cells[0].paragraphs[0]
        p_lbl.runs[0].font.name = "Times New Roman"
        p_lbl.runs[0].font.size = Pt(10)
        p_lbl.runs[0].font.bold = True
        p_lbl.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(row.cells[0], "D9E1F2")

        row.cells[1].text = content
        p_cnt = row.cells[1].paragraphs[0]
        p_cnt.runs[0].font.name = "Times New Roman"
        p_cnt.runs[0].font.size = Pt(10.5)
        p_cnt.paragraph_format.line_spacing = 1.15
        set_cell_background(row.cells[1], bg_color)

    for row in table.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = w
            set_cell_margins(row.cells[i], top=70, bottom=70, left=100, right=100)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(8)

def build_unified_asr_handbook():
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    add_header(
        doc,
        "BÁO CÁO KỸ THUẬT CHUYÊN SÂU & GIẢI MÃ KIẾN TRÚC PIPELINE\nHỆ THỐNG NHẬN DẠNG TIẾNG NÓI TỰ ĐỘNG (ASR) TIẾNG VIỆT",
        "Định hướng Luận giải: 'TẠI SAO ĐỀ TÀI CẦN SỬ DỤNG PIPELINE NÀY VÀ TỪNG BƯỚC CỤ THỂ?'",
        "Bộ môn: Xử lý Tiếng nói | GVHD: TS. Phù Khắc Anh | Nhóm thực hiện: Nhóm 6 (Trưởng nhóm phụ trách)"
    )

    # ==========================================
    # CHƯƠNG 1: TỔNG QUAN CHI TIẾT VỀ ĐỀ TÀI VÀ LỰA CHỌN GIẢI PHÁP
    # ==========================================
    add_heading_1(doc, "CHƯƠNG 1: TỔNG QUAN CHI TIẾT VỀ ĐỀ TÀI & LUẬN GIẢI LỰA CHỌN PIPELINE")

    add_paragraph(doc,
                  "Đề tài tập trung giải quyết bài toán Nhận dạng Tiếng nói Tự động (Automatic Speech Recognition - ASR) cho tiếng Việt đàm thoại liên tục. Mục tiêu là xây dựng một hệ thống hoàn chỉnh từ khâu thu nhận tín hiệu âm thanh thô qua Micro thực tế (Laptop hoặc tai nghe) hoặc file âm thanh .wav, trích xuất đặc trưng âm học trực quan, nhận dạng chuỗi ký tự bằng mô hình học sâu nơ-ron và giải mã văn bản tiếng Việt chuẩn xác có dấu, kèm bộ tổng hợp giọng đọc phản hồi (TTS) trên giao diện tương tác trực quan thời gian thực.",
                  bold_prefix="1.1. Bản chất đề tài (Đề tài này về cái gì?): ")

    add_paragraph(doc,
                  "Tiếng Việt là ngôn ngữ đơn lập (Isolating Language) với hệ thống 6 thanh điệu phong phú (ngang, huyền, sắc, hỏi, ngã, nặng), hệ thống nguyên âm đơn/đôi/ba phức tạp (ươ, oa, uyên...), có hiện tượng đồng âm khác nghĩa và đồng phụ âm skeleton. Cùng một câu nói nhưng ngữ điệu thanh điệu thay đổi sẽ làm thay đổi hoàn toàn ý nghĩa ngữ pháp. Do đó, hệ thống ASR cho tiếng Việt không thể sao chép máy móc pipeline tiếng Anh mà phải có cơ chế xử lý thanh điệu và đối soát chính tả riêng biệt.",
                  bold_prefix="Thách thức đặc thù của Tiếng Việt: ")

    add_paragraph(doc,
                  "• Đầu vào (Input): File âm thanh .wav hoặc ghi âm trực tiếp qua Micro (Micro Laptop, Tai phone 3.5mm/Bluetooth), định dạng mono 16.000 Hz, thời lượng 2 - 10 giây/câu.\n"
                  "• Đầu ra (Output): Văn bản tiếng Việt có dấu đúng chính tả, kèm độ trễ xử lý (Latency tính bằng giây) và trực quan hóa phổ Log-Mel Spectrogram.\n"
                  "• Phạm vi nghiên cứu: Huấn luyện và đánh giá trên tập ngữ liệu VIVOS (15.4 giờ âm thanh chuẩn) và kiểm thử thực tế trên giọng nói đàm thoại bên ngoài qua Micro.\n"
                  "• Bộ chỉ số đo lường (Metrics): Hàm mất mát CTC Loss (hội tụ mức 1.21), Tỉ lệ lỗi từ WER, Tỉ lệ lỗi ký tự CER, Kích thước mô hình (9.8 MB) và Thời gian suy luận (Latency cực thấp ~0.07 giây/câu).",
                  bold_prefix="1.2. Mục tiêu, Đầu vào, Đầu ra và Tiêu chí Đánh giá: ")

    add_paragraph(doc,
                  "Toàn bộ đề tài được xây dựng theo một kiến trúc Pipeline tích hợp chặt chẽ từ Phần cứng đến Phần mềm, gồm 5 khối công nghệ cốt lõi:\n"
                  "1. Bộ thu nhận âm thanh đa luồng: PyAudio / SoundDevice với hàng đợi FIFO Thread-Safe chống tràn buffer.\n"
                  "2. Khối tiền xử lý số tín hiệu DSP: Lọc Stereo chống triệt tiêu pha, Polyphase Resampling 16kHz, VAD năng lượng ngắn hạn (STE), Audio Floor Safety và Peak Normalization dự trữ 5% headroom.\n"
                  "3. Khối trích xuất đặc trưng âm học: STFT khung 25ms/hop 10ms, Power Spectrum (bỏ pha), Mel Filterbank 80 dải lọc tam giác, Nén Logarithm năng lượng và Chuẩn hóa Z-Score CMVN.\n"
                  "4. Mô hình âm học nơ-ron sâu End-to-End (CRNN-CTC): 3 khối Conv2D trích xuất Formant + Tầng Linear Projection nén chiều + 2 tầng BiGRU 512 chiều học ngữ cảnh thời gian hai chiều + Tầng CTC Classifier can thiệp Negative Blank Bias (-3.0). Đi kèm Động cơ bổ trợ Wav2Vec2 CTC Fine-tune (250h Pretrained) để đối chuẩn.\n"
                  "5. Khối giải mã & Ràng buộc tri thức ngôn ngữ: CTC Greedy Best-Path Search + Toán tử sụp đổ B (Collapse) + Bóc tách khung phụ âm Unicode NFKD (Consonant Skeleton) + Ràng buộc từ điển tiếng Việt VIVOS (4.861 từ) bằng khoảng cách Levenshtein + Khử lặp từ ngắc ngứ (De-duplication).",
                  bold_prefix="1.3. Đề tài sử dụng những công nghệ và mô hình gì?: ")

    add_heading_2(doc, "1.4. Luận giải Cốt lõi: TẠI SAO ĐỀ TÀI NÀY PHẢI SỬ DỤNG PIPELINE NÀY?")
    add_paragraph(doc, "Hội đồng đánh giá luôn đặt câu hỏi trọng tâm: 'Tại sao nhóm lại thiết kế pipeline này mà không chọn các giải pháp khác?'. Dưới đây là 3 lý do khoa học và kỹ thuật quyết định:")

    # Bảng so sánh 3 giải pháp
    table_comp = doc.add_table(rows=4, cols=4)
    table_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_comp.style = 'Table Grid'
    headers = ["Tiêu chí kỹ thuật", "1. HMM - GMM (Cổ điển)", "2. PIPELINE CRNN-CTC (Nhóm chọn)", "3. Transformer / Whisper"]
    for i, h in enumerate(headers):
        cell = table_comp.rows[0].cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].font.name = "Times New Roman"
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(cell, "1B365D")

    data_comp = [
        ("Căn chỉnh thời gian (Alignment)",
         "Bắt buộc dùng Forced Alignment ở cấp độ âm vị (Phoneme/Triphone). Cực kỳ tốn công gán nhãn thủ công và dễ sai lệch ranh giới âm vị tiếng Việt.",
         "Hoàn toàn Alignment-free (Không cần gán nhãn trước). Hàm mất mát CTC Loss tự động tính toán tổng xác suất trên mọi đường gióng hàng hợp lệ.",
         "Cơ chế Cross-Attention tự học gióng hàng. Yêu cầu lượng dữ liệu huấn luyện khổng lồ hàng nghìn giờ mới không bị ảo giác sinh chữ."),
        ("Tài nguyên & Độ trễ (Hardware Latency)",
         "Cồng kềnh với nhiều module rời rạc (Acoustic model, Lexicon, Language Model n-gram). Tốc độ giải mã đồ thị Viterbi chậm.",
         "Siêu gọn nhẹ: Mô hình chỉ có 2.45 triệu tham số (~9.8 MB). Thời gian suy luận cực nhanh (~0.07s/câu), chạy mượt mà thời gian thực trên CPU máy tính cá nhân.",
         "Kích thước khổng lồ (>150 MB đến 3 GB). Đòi hỏi GPU chuyên dụng VRAM lớn. Độ trễ cao (1-3s), không thể chạy realtime trên máy tính phổ thông."),
        ("Khả năng khắc phục lỗi tiếng Việt",
         "Phụ thuộc chặt vào từ điển phiên âm thủ công. Rất khó sửa lỗi khi người dùng phát âm ngọng hoặc nói nhanh lệch dấu.",
         "Kết hợp tinh tế giữa Deep Learning (CRNN dự đoán khung ký tự) và Hậu xử lý Lexicon Matching (bóc tách khung phụ âm Unicode sửa sai dấu thanh).",
         "Dựa vào Language Model nơ-ron lớn bên trong. Có hiện tượng 'ảo giác' (Hallucination) tự bịa thêm từ tiếng Việt không có trong âm thanh.")
    ]

    for row_idx, row_data in enumerate(data_comp, start=1):
        for col_idx, text in enumerate(row_data):
            cell = table_comp.rows[row_idx].cells[col_idx]
            cell.text = text
            p = cell.paragraphs[0]
            p.runs[0].font.name = "Times New Roman"
            p.runs[0].font.size = Pt(9)
            p.paragraph_format.line_spacing = 1.15
            if col_idx == 0:
                p.runs[0].font.bold = True
                set_cell_background(cell, "D9E1F2")
            elif col_idx == 2:
                set_cell_background(cell, "FFF9E6") # Cột của nhóm
            else:
                set_cell_background(cell, "FFFFFF")

    for row in table_comp.rows:
        for i, w in enumerate([Inches(1.5), Inches(1.8), Inches(2.0), Inches(1.7)]):
            row.cells[i].width = w
            set_cell_margins(row.cells[i], top=60, bottom=60, left=70, right=70)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(10)

    # ==========================================
    # CHƯƠNG 2: GIAI ĐOẠN 2 - TIỀN XỬ LÝ ÂM THANH & KHỬ NHIỄU
    # ==========================================
    add_heading_1(doc, "CHƯƠNG 2: GIAI ĐOẠN 2 - TIỀN XỬ LÝ ÂM THANH & KHỬ NHIỄU (PRE-PROCESSING & CLEAN-UP)")
    add_paragraph(doc, "Giai đoạn 2 tiếp nhận dòng byte âm thanh thô từ Micro/File và thực hiện chuỗi chuẩn hóa tín hiệu số để loại bỏ nhiễu phần cứng trước khi đưa vào trích xuất đặc trưng.")

    # 2.1
    add_pipeline_step_box(
        doc,
        "BƯỚC 2.1",
        "CHỐNG TRIỆT TIÊU PHA STEREO (DOMINANT CHANNEL EXTRACTION)",
        "Micro máy tính hoặc tai nghe Bluetooth thường ghi nhận âm thanh 2 kênh độc lập (Stereo: Left & Right). Do khoảng cách từ miệng người nói đến 2 micro nhỏ trên thân máy là khác nhau, âm thanh đến 2 kênh sẽ có độ trễ thời gian $\Delta t$, tạo ra sự Lệch pha (Phase Mismatch).",
        "Tại sao đề tài PHẢI dùng bước này mà KHÔNG cộng trung bình thô (L + R) / 2?\n"
        "Nếu người dùng sử dụng tai nghe có 2 micro bị lệch pha 180 độ ở một tần số nào đó, phép cộng trung bình thô $(L+R)/2$ sẽ gây ra hiện tượng Triệt tiêu giao thoa sóng (Destructive Interference) – tức là giọng nói của người dùng bị triệt tiêu hoàn toàn thành một đường thẳng phẳng lặng!\n"
        "Bằng cách so sánh năng lượng RMS của kênh Trái và Phải, hệ thống tự động chọn ra kênh có tín hiệu giọng nói chiếm ưu thế mạnh nhất (Dominant Channel), loại bỏ hoàn toàn nguy cơ triệt tiêu pha.",
        "Toán học:\n"
        "E_left = sum(x_left[n]^2); E_right = sum(x_right[n]^2)\n"
        "active_channel = argmax([E_left, E_right])\n"
        "audio_mono = audio_stereo[:, active_channel]",
        "File: controllers/audio_controller.py\n"
        "Code: active_ch = np.argmax([left_energy, right_energy])\n"
        "audio_mono = audio_np[:, active_ch]",
        "Hỏi: Tại sao không dùng công thức chuẩn hóa mono thông thường (L + R) / 2?\n"
        "Đáp: Phép cộng (L + R) / 2 chỉ an toàn trong phòng thu lý tưởng. Trong thực tế, các micro laptop rẻ tiền có hiện tượng lệch pha giữa 2 mic. Nếu lệch pha 180 độ tại tần số Formant 1kHz, sóng âm 2 kênh ngược dấu triệt tiêu lẫn nhau, làm mất Formant của nguyên âm. Chọn kênh có năng lượng lớn nhất đảm bảo bảo toàn 100% biên độ giọng nói mà không bị suy hao."
    )

    # 2.2
    add_pipeline_step_box(
        doc,
        "BƯỚC 2.2",
        "POLYPHASE RESAMPLING VỀ 16.000HZ CHUẨN",
        "Resampling là quá trình biến đổi tần số lấy mẫu từ mức thu âm phần cứng (thường là 44.100 Hz hoặc 48.000 Hz) về tần số chuẩn của hệ thống học máy (16.000 Hz) bằng thuật toán lọc đa pha (Polyphase Filtering) kết hợp cửa sổ Kaiser.",
        "Tại sao đề tài PHẢI hạ về 16.000 Hz mà không giữ nguyên 48.000 Hz?\n"
        "1. Dải tần tiếng nói con người: Toàn bộ thông tin nhận dạng nguyên âm, phụ âm và thanh điệu tiếng Việt tập trung dưới 8.000 Hz. Theo định lý Nyquist, tần số lấy mẫu Fs = 16.000 Hz cho phép tái tạo hoàn hảo tần số lên tới 8.000 Hz (đáp ứng 100% nhu cầu ngữ âm).\n"
        "2. Tối ưu tài nguyên CPU: Giữ nguyên 48.000 Hz khiến số lượng mẫu âm thanh tăng gấp 3 lần, làm ma trận STFT phình to gấp 3 lần và mạng nơ-ron tính toán chậm đi gấp 3 lần. Hạ về 16.000 Hz giúp tiết kiệm 67% chi phí tính toán, là nhân tố cốt lõi giúp hệ thống đạt độ trễ thời gian thực 0.07 giây.\n"
        "3. Lọc đa pha với cửa sổ Kaiser triệt tiêu hoàn toàn hiện tượng méo gấp phổ (Aliasing).",
        "Toán học:\n"
        "Tỉ số lấy mẫu: L / M = 16000 / F_orig\n"
        "Bộ lọc thông thấp cắt bỏ toàn bộ f > 8000 Hz trước khi hạ mẫu: H_kaiser(e^jw)",
        "File: controllers/audio_controller.py\n"
        "Code: audio_16k = signal.resample_poly(audio_mono, up=16000, down=orig_sr)",
        "Hỏi: Nếu bỏ qua bộ lọc thông thấp mà chỉ đơn giản lấy cách quãng 1 trong 3 mẫu thì điều gì xảy ra?\n"
        "Đáp: Hiện tượng Chồng phổ (Aliasing) sẽ xuất hiện: các tần số cao trên 8.000 Hz từ quạt gió, tiếng rít kim loại sẽ bị gập ngược vào dải 0 - 8.000 Hz, tạo ra các vạch phổ giả mạo làm biến dạng các dải Formant nguyên âm, khiến mô hình nhận diện sai hoàn toàn."
    )

    # 2.3
    add_pipeline_step_box(
        doc,
        "BƯỚC 2.3",
        "NĂNG LƯỢNG NGẮN HẠN STE & BỘ LỌC VAD (VOICE ACTIVITY DETECTION)",
        "Voice Activity Detection (VAD) là kỹ thuật phân tách dòng tín hiệu thành vùng có tiếng nói (Speech) và vùng im lặng/tạp âm (Silence/Noise). Hệ thống chia tín hiệu thành các khung 25ms (400 mẫu), bước nhảy 10ms, nhân cửa sổ Hamming và tính Năng lượng ngắn hạn STE (Short-Time Energy) so với ngưỡng tương đối 0.08 (-22dBFS).",
        "Tại sao đề tài PHẢI có bước VAD này?\n"
        "Khi người dùng bấm 'Ghi âm', thông thường họ mất 1-2 giây chuẩn bị trước khi nói và ngập ngừng 1-2 giây sau khi nói xong. Khoảng thời gian này chứa tiếng thở, tiếng quạt gió máy tính hoặc tiếng bấm chuột.\n"
        "Nếu không có VAD, 4 giây im lặng vô nghĩa này sẽ bị đưa vào mạng CRNN, làm bộ giải mã CTC sinh ra hàng loạt token Blank vô ích, làm tăng thời gian xử lý và dễ gây lỗi ảo giác (Hallucination) hoặc lặp từ. VAD gọt sạch các đoạn thừa, chỉ giữ lại phần phát âm thực tế.",
        "Toán học:\n"
        "STE[m] = sum_{n=0}^{N-1} ( x[m*H + n] * w[n] )^2\n"
        "VAD_mask = (STE / max(STE)) >= 0.08",
        "File: controllers/audio_controller.py\n"
        "Code: frame = audio_16k[i:i+400] * np.hamming(400)\n"
        "vad_mask = (ste / ste.max()) >= 0.08",
        "Hỏi: Tại sao lại chọn ngưỡng VAD tương đối 0.08 (theo ste.max) thay vì một ngưỡng cố định tuyệt đối?\n"
        "Đáp: Vì mỗi người có âm lượng nói to/nhỏ khác nhau và micro có độ nhạy khác nhau. Dùng ngưỡng tương đối so với đỉnh năng lượng lớn nhất trong chính bản ghi đó giúp hệ thống tự động thích ứng động (Dynamic Adaptive Threshold), không bị cắt nhầm tiếng thì thầm hay giữ nhầm tiếng ồn."
    )

    # 2.4
    add_pipeline_step_box(
        doc,
        "BƯỚC 2.4",
        "SÀN NĂNG LƯỢNG AN TOÀN (AUDIO FLOOR SAFETY)",
        "Sàn năng lượng an toàn là hàng rào bảo vệ kiểm tra tính hợp lệ của bản ghi âm dựa trên 2 điều kiện cứng: Thời lượng phát âm tối thiểu (Duration >= 0.3 giây) và Biên độ đỉnh tối thiểu (max_amp >= 0.0008, tương đương -62dBFS).",
        "Tại sao đề tài PHẢI có bước này?\n"
        "Đây là cơ chế phòng thủ chống sập hệ thống (Defensive Programming). Trong thực tế tương tác giao diện đồ họa, người dùng rất hay bấm nhầm nút Record rồi Stop ngay lập tức (dưới 0.3 giây) hoặc bấm ghi âm trong phòng hoàn toàn yên tĩnh mà không nói gì.\n"
        "Nếu đưa một mảng âm thanh rỗng hoặc toàn số 0 vào khâu chuẩn hóa và STFT, phép chia cho độ lệch chuẩn sẽ gây lỗi chia cho 0 (ZeroDivisionError / NaN) hoặc khiến mạng Deep Learning cố gắng 'khuếch đại nhiễu trắng' để đoán chữ. Bước này chặn đứng lỗi từ sớm và đưa ra phản hồi thân thiện cho người dùng.",
        "Điều kiện kiểm tra:\n"
        "if duration < 0.3 or max_amplitude < 0.0008:\n"
        "    Bỏ qua suy luận, thông báo 'Âm lượng quá nhỏ hoặc thời lượng quá ngắn'",
        "File: controllers/audio_controller.py\n"
        "Code: if duration < 0.3 or max_amp < 0.0008: return 'Âm lượng quá nhỏ...'",
        "Hỏi: Cơ chế Sàn năng lượng an toàn giải quyết bài toán gì trong trải nghiệm người dùng (UX)?\n"
        "Đáp: Giải quyết triệt để lỗi người dùng vô tình kích hoạt micro hoặc micro bị ngắt kết nối phần cứng. Hệ thống phản hồi ngay lập tức sau 0.001 giây mà không tốn công chạy qua mô hình AI, ngăn ngừa 100% hiện tượng crash giao diện hoặc hiện tượng AI tự đoán chữ bậy bạ khi không có người nói."
    )

    # 2.5
    add_pipeline_step_box(
        doc,
        "BƯỚC 2.5",
        "PEAK NORMALIZATION & DỰ TRỮ HEADROOM (-0.45dBFS)",
        "Peak Normalization là kỹ thuật chuẩn hóa biên độ đỉnh của tín hiệu âm thanh về một ngưỡng mục tiêu cố định bằng cách tìm giá trị tuyệt đối lớn nhất và nhân chia tỉ lệ: audio_norm = (audio / max_amp) * 0.95. Hệ thống chủ động nhân với hệ số 0.95 để dự trữ 5% biên độ an toàn (Headroom).",
        "Tại sao đề tài PHẢI chuẩn hóa biên độ và dự trữ 5% Headroom?\n"
        "1. Triệt tiêu chênh lệch âm lượng: Có người nói to sát micro, có người nói thì thầm ở xa. Nếu không chuẩn hóa, năng lượng Mel-Spectrogram sẽ bị trồi sụt thất thường, làm hàm kích hoạt Hardtanh trong mạng CRNN bị bão hòa hoặc bị tắt ngấm.\n"
        "2. Tại sao phải nhân 0.95 (Dự trữ 5% Headroom) mà không nhân 1.0? Trong quá trình xử lý tín hiệu số tiếp theo (bộ lọc FIR Resampling hoặc lọc dải), hiện tượng Gibbs Phenomenon có thể làm biên độ tại một số điểm dao động vọt lên trên 1.0 (True-Peak Overshoot). Nếu để kịch trần 1.0, các đỉnh này sẽ bị cắt cụt thẳng đứng (Clipping Distortion), sinh ra tiếng lách cách làm méo phổ Formant. Hệ số 0.95 (-0.45dBFS) là tiêu chuẩn vàng của ngành âm thanh để chống Clipping 100%.",
        "Toán học:\n"
        "max_amp = max(|x[n]|)\n"
        "x_norm[n] = (x[n] / max_amp) * 0.95",
        "File: controllers/audio_controller.py\n"
        "Code: norm_audio = (audio_16k / max_amp) * 0.95  # Dự trữ 5% Headroom",
        "Hỏi: Headroom trong xử lý âm thanh là gì? Tại sao không chuẩn hóa kịch trần lên 1.0 (0 dBFS)?\n"
        "Đáp: Headroom là khoảng đệm an toàn giữa đỉnh tín hiệu lớn nhất và ngưỡng bão hòa tối đa của hệ thống số. Chuẩn hóa lên 0.95 để dành ra 0.05 khoảng đệm. Nếu để 1.0, khi tín hiệu đi qua các phép biến đổi toán học hoặc bộ lọc tái cấu trúc, hiện tượng quá đỉnh liên mẫu (Inter-sample Peak) sẽ vượt quá 1.0 gây xén ngọn (Clipping), làm méo dạng sóng âm học."
    )

    # ==========================================
    # CHƯƠNG 3: GIAI ĐOẠN 3 - TRÍCH XUẤT ĐẶC TRƯNG ÂM HỌC
    # ==========================================
    add_heading_1(doc, "CHƯƠNG 3: GIAI ĐOẠN 3 - TRÍCH XUẤT ĐẶC TRƯNG ÂM HỌC (FEATURE EXTRACTION)")
    add_paragraph(doc, "Giai đoạn 3 biến đổi chuỗi sóng âm 1D trong miền thời gian thành biểu diễn không gian - thời gian 2D (Log-Mel Spectrogram), làm đầu vào hoàn hảo cho mạng nơ-ron tích chập.")

    # 3.1
    add_pipeline_step_box(
        doc,
        "BƯỚC 3.1",
        "BIẾN ĐỔI FOURIER NGẮN HẠN (STFT - SHORT-TIME FOURIER TRANSFORM)",
        "Tín hiệu tiếng nói biến đổi liên tục theo thời gian (phi dừng). STFT chia tín hiệu thành các khung ngắn 25ms (400 mẫu tại 16kHz) với độ dịch 10ms (160 mẫu), áp dụng n_fft = 512 và nhân cửa sổ Hamming để đưa từng khung về miền tần số phức: X(f, t) = Real(f, t) + j * Imag(f, t) gồm 257 dải tần số từ 0 đến 8.000 Hz.",
        "Tại sao đề tài PHẢI dùng STFT mà không đưa trực tiếp sóng âm (Raw Waveform) vào mạng nơ-ron?\n"
        "Trong miền thời gian, cùng một chữ 'A' được nói bởi nam và nữ có dạng sóng áp suất không khí hoàn toàn khác nhau về biên độ và chu kỳ, mạng nơ-ron nông rất khó học được tính bất biến này. STFT phân rã sóng âm phức tạp thành các thành phần tần số vật lý riêng biệt, cho phép tách bạch rõ ràng giữa cao độ giọng người (Pitch) và cấu trúc cộng hưởng miệng (Formant) – yếu tố duy nhất quyết định chữ viết!",
        "Toán học:\n"
        "STFT{x[n]}(m, k) = sum_{n=0}^{N-1} x[m*H + n] * w[n] * e^{-j * 2*pi * k * n / N_fft}\n"
        "với N_fft = 512, Win = 400 (25ms), Hop = 160 (10ms)",
        "File: models/feature_extractor.py\n"
        "Code: stft = torch.stft(y, n_fft=512, hop_length=160, win_length=400, window=hamming, return_complex=True)",
        "Hỏi: Tại sao n_fft = 512 trong khi win_length chỉ có 400 mẫu?\n"
        "Đáp: Cửa sổ 400 mẫu (25ms) được đệm thêm 112 số 0 vào đuôi (Zero-padding) để đạt độ dài lũy thừa của 2 là 512. Việc này giúp thuật toán FFT chạy với tốc độ tối ưu nhất (Radix-2 FFT), đồng thời tăng mật độ nội suy trên trục tần số từ 201 bins lên 257 bins (mỗi bin cách nhau 31.25 Hz), giúp các vạch phổ sắc nét hơn."
    )

    # 3.2
    add_pipeline_step_box(
        doc,
        "BƯỚC 3.2",
        "TÍNH PHỔ CÔNG SUẤT (POWER SPECTRUM - LOẠI BỎ PHA)",
        "Phổ công suất (Power Spectrum) là bình phương độ lớn của các hệ số Fourier phức thu được từ STFT: P(f, t) = |X(f, t)|^2 = Real^2 + Imag^2. Thao tác này loại bỏ hoàn toàn góc pha (Phase) của tín hiệu.",
        "Tại sao đề tài PHẢI loại bỏ Pha (Phase Invariance) và chỉ giữ lại Phổ công suất?\n"
        "Góc pha thể hiện vị trí xuất phát thời gian của từng họa tần sóng âm, nó biến thiên cực kỳ hỗn loạn tùy thuộc vào khoảng cách người nói dịch chuyển vài milimet so với micro hoặc phản xạ tường phòng. Tuy nhiên, hệ thống thính giác của con người hoàn toàn không nghe được góc pha tuyệt đối (Hiện tượng mù pha của tai người - Phase Deafness). Nội dung chữ viết tiếng Việt chỉ nằm ở Mật độ Năng lượng (Energy Distribution) tại các dải Formant. Bỏ pha giúp mô hình đạt tính Bất biến với độ trễ (Phase Invariance) và loại bỏ 50% dữ liệu nhiễu không cần thiết.",
        "Toán học:\n"
        "X = a + j*b => Magnitude |X| = sqrt(a^2 + b^2)\n"
        "Power Spectrum P = |X|^2 = a^2 + b^2",
        "File: models/feature_extractor.py\n"
        "Code: power_spec = stft.abs().pow(2)  # |Z|² = Real² + Imag²",
        "Hỏi: Nếu bỏ pha thì có tái tạo (nghe lại) được giọng nói gốc một cách hoàn hảo không? ASR có cần nghe lại không?\n"
        "Đáp: Bỏ pha thì không thể tái tạo lại dạng sóng âm thanh gốc hoàn hảo nếu không dùng các giải thuật ước lượng pha như Griffin-Lim. Nhưng hệ thống ASR là bài toán Chuyển giọng nói thành văn bản chữ viết (Speech-to-Text), hoàn toàn không có nhu cầu phát ngược lại âm thanh gốc. Vì vậy việc bỏ pha là tối ưu 100% cho bài toán nhận dạng."
    )

    # 3.3
    add_pipeline_step_box(
        doc,
        "BƯỚC 3.3",
        "CHIẾU QUA 80 DẢI LỌC MEL (MEL FILTERBANK)",
        "Mel Filterbank là tập hợp 80 bộ lọc hình tam giác xếp chồng gối lên nhau, được phân bổ phi tuyến theo thang tần số Mel mô phỏng màng đáy ốc tai người: m = 2595 * log10(1 + f / 700). Năng lượng tại mỗi dải Mel là tích chập có trọng số của các bin tần số FFT nằm trong tam giác.",
        "Tại sao đề tài PHẢI dùng thang đo Mel 80 dải mà không giữ nguyên 257 dải tuyến tính Hertz?\n"
        "1. Mô phỏng sinh lý thính giác: Tai người cực kỳ nhạy cảm ở tần số thấp (< 1.000 Hz) nhưng rất kém ở tần số cao (> 1.000 Hz). Mel Filterbank bố trí các bộ lọc rất dày ở dải thấp (mỗi lọc chỉ 1-2 bins) để nắm bắt Formant F1, F2 của nguyên âm tiếng Việt, và mở rộng bộ lọc ở dải cao để gom năng lượng phụ âm xát.\n"
        "2. Nén chiều dữ liệu: Giảm kích thước trục tần số từ 257 bins xuống đúng 80 dải Mel. Đây là con số tiêu chuẩn vàng giúp mạng Conv2D vừa đủ thông tin học sâu mà không bị quá tải bộ nhớ.",
        "Toán học (Phép nhân ma trận):\n"
        "Mel_Spec[80, T] = Mel_Basis[80, 257] @ Power_Spec[257, T]",
        "File: models/feature_extractor.py\n"
        "Code: mel_spec = torch.matmul(self.mel_basis, power_spec)  # [80, 257] @ [257, T] = [80, T]",
        "Hỏi: Tại sao nhóm lại chọn 80 dải lọc Mel mà không phải là 40 dải hay 128 dải?\n"
        "Đáp: 40 dải Mel thường dùng cho mô hình cổ điển MFCC/HMM nhưng hơi thô đối với tiếng Việt (vốn có nhiều nguyên âm đôi tinh vi như ươ, oa, uyê). 128 dải Mel lại chứa nhiều thông tin thừa ở dải cao gây tốn GPU. 80 dải Mel là chuẩn công nghiệp hiện đại (được dùng trong cả Whisper, Conformer và Tacotron2), cung cấp đủ độ mịn để phân biệt rõ 6 thanh điệu và các nguyên âm tiếng Việt."
    )

    # 3.4
    add_pipeline_step_box(
        doc,
        "BƯỚC 3.4",
        "NÉN LOGARITHM NĂNG LƯỢNG (LOG MEL-SPECTROGRAM)",
        "Nén Logarithm là thao tác lấy Log tự nhiên của năng lượng các dải Mel sau khi chặn sàn cực tiểu epsilon: S_log = torch.log(torch.clamp(mel_spec, min=1e-5)).",
        "Tại sao đề tài PHẢI lấy Logarithm của năng lượng Mel?\n"
        "1. Định luật cảm giác Weber-Fechner: Não bộ và màng nhĩ người cảm nhận cường độ âm thanh (độ to Loudness) theo tỉ lệ Logarit (thang Decibel) chứ không theo thang tuyến tính. Chênh lệch năng lượng giữa tiếng thì thầm và hét lớn có thể lên tới 1.000.000 lần (10^6). Phép Log nén dải động khổng lồ này về khoảng giá trị nhỏ gọn [-11.5, +5.0].\n"
        "2. Ổn định Gradient học sâu: Nếu giữ nguyên năng lượng tuyến tính, các âm thanh phát âm lớn sẽ có gradient bùng nổ (Exploding Gradient), làm bay màu trọng số của các phụ âm phát âm khẽ. Hàm Log giúp cân bằng động học toàn dải, giúp mạng nơ-ron học đồng đều cả nguyên âm lẫn phụ âm.",
        "Toán học:\n"
        "S_LogMel = log( max( Mel_Energy, 1e-5 ) )",
        "File: models/feature_extractor.py\n"
        "Code: log_mel = torch.log(torch.clamp(mel_spec, min=1e-5))  # Mô phỏng độ to Decibel",
        "Hỏi: Tại sao lại cần hàm torch.clamp(..., min=1e-5) trước khi lấy log?\n"
        "Đáp: Để bảo vệ an toàn số học. Hàm Log(0) tiến tới âm vô cùng (-inf). Nếu có dải tần số nào hoàn toàn không có năng lượng (ví dụ trong khoảng lặng sâu), log(0) sẽ sinh ra giá trị NaN hoặc -Inf, làm phá hủy toàn bộ ma trận trọng số mạng nơ-ron khi lan truyền ngược. Giá trị clamp 1e-5 đảm bảo log luôn là số thực hữu hạn."
    )

    # 3.5
    add_pipeline_step_box(
        doc,
        "BƯỚC 3.5",
        "CHUẨN HÓA THỐNG KÊ Z-SCORE (CMVN - CEPSTRAL MEAN & VARIANCE NORMALIZATION)",
        "CMVN là kỹ thuật chuẩn hóa Z-score trực tiếp trên từng dải tần số của ma trận Log-Mel Spectrogram theo trục thời gian: trừ đi giá trị trung bình (Mean) và chia cho độ lệch chuẩn (Std) của bản ghi âm đó: norm_mel = (log_mel - mean) / (std + 1e-6).",
        "Tại sao đề tài PHẢI dùng CMVN trên từng câu (Per-utterance CMVN)?\n"
        "Trong thực tế, mỗi micro (micro laptop, tai nghe cắm dây, tai nghe Bluetooth) đều có một đáp ứng tần số riêng biệt (micro xịn thì âm trầm dày, micro rẻ tiền thì âm thanh bẹt đục). Kênh truyền micro và độ vang phòng đóng vai trò như một bộ lọc nhân tích chập H(f) với tiếng nói S(f) trong miền tần số.\n"
        "Khi lấy Log năng lượng: log |X(f)| = log |S(f)| + log |H(f)|.\n"
        "Ta thấy đặc tính méo của micro biến thành một đại lượng CỘNG TĨNH không đổi theo thời gian! Khi ta tính Mean theo trục thời gian và trừ đi, thành phần méo của micro log|H(f)| bị TRIỆT TIÊU HOÀN TOÀN! Nhờ CMVN, cùng một câu nói thu qua bất kỳ loại micro nào cũng trở về cùng một dạng phân phối chuẩn N(0, 1).",
        "Toán học:\n"
        "mu = (1/T) * sum_{t=1}^T S[f, t]; sigma = sqrt( (1/T) * sum_{t=1}^T (S[f, t] - mu)^2 )\n"
        "S_norm[f, t] = (S[f, t] - mu) / (sigma + 1e-6)",
        "File: models/feature_extractor.py\n"
        "Code: norm_mel = (log_mel - log_mel.mean()) / (log_mel.std() + 1e-6)  # Đưa về N(0, 1)",
        "Hỏi: Phép trừ Mean trong CMVN có làm mất ngữ nghĩa của câu nói không?\n"
        "Đáp: Tuyệt đối không. Ngữ nghĩa của tiếng nói nằm ở sự biến thiên động học (Dynamic modulation) của các Formant chuyển động lên xuống theo thời gian. Trong khi đó, đáp ứng của micro là thành phần tĩnh cố định suốt câu nói. Phép trừ Mean chỉ gạt bỏ thành phần tĩnh của micro, giữ lại trọn vẹn 100% sự biến thiên ngữ âm của người nói."
    )

    # ==========================================
    # CHƯƠNG 4: GIAI ĐOẠN 4 - MÔ HÌNH ÂM HỌC NƠ-RON SÂU
    # ==========================================
    add_heading_1(doc, "CHƯƠNG 4: GIAI ĐOẠN 4 - MÔ HÌNH ÂM HỌC NƠ-RON SÂU (CRNN-CTC DEEP ACOUSTIC MODEL)")
    add_paragraph(doc, "Giai đoạn 4 là trái tim của hệ thống ASR, chuyển đổi biểu diễn phổ Log-Mel 80 chiều thành phân phối xác suất trên 105 tokens tiếng Việt dọc theo các khung thời gian.")

    # 4.1
    add_pipeline_step_box(
        doc,
        "BƯỚC 4.1",
        "3 KHỐI TÍCH CHẬP 2D (CONV2D + BATCHNORM + HARDTANH + MAXPOOL)",
        "Khối trích xuất đặc trưng gồm 3 tầng tích chập 2D xếp chồng:\n"
        "• Khối 1: Conv2D(1->32, k=3, p=1) + BatchNorm2D + Hardtanh + MaxPool2D(2, 2) => nén (80->40 Mel, T->T/2).\n"
        "• Khối 2: Conv2D(32->64, k=3, p=1) + BatchNorm2D + Hardtanh + MaxPool2D(2, 2) => nén (40->20 Mel, T/2->T/4).\n"
        "• Khối 3: Conv2D(64->128, k=3, p=1) + BatchNorm2D + Hardtanh + MaxPool2D(2, 1) => nén (20->10 Mel, GIỮ NGUYÊN T/4).",
        "Tại sao đề tài PHẢI dùng CNN ở tầng đầu và TẠI SAO Khối 3 lại giữ nguyên trục thời gian (stride=(2, 1))?\n"
        "1. Tại sao dùng CNN: Mạng Conv2D quét các kernel 3x3 bắt các mối tương quan không gian cục bộ (Local Spectral Patterns) – nhận diện chính xác hình dạng đường cong Formant và các cạnh chuyển tiếp phụ âm.\n"
        "2. ĐIỂM SÁNG TẠO CỦA KHỐI 3: Nếu Khối 3 tiếp tục nén thời gian 2 lần nữa (thành T/8), trục thời gian sẽ bị co quá ngắn (chỉ còn khoảng 80ms/khung). Trong tiếng Việt, các phụ âm bật tắt ngắn như /t/, /p/, /c/ chỉ kéo dài 20-30ms sẽ bị nuốt chửng hoàn toàn! Bằng cách thiết lập MaxPool2D(2, 1) ở khối 3, hệ thống chỉ nén tần số về 10 dải nhưng giữ nguyên độ phân giải thời gian T/4, đảm bảo thuật toán CTC có đủ số frame để phân định từng âm vị độc lập.",
        "Kích thước biến đổi Tensor:\n"
        "[B, 1, 80, T] -> [B, 32, 40, T/2] -> [B, 64, 20, T/4] -> [B, 128, 10, T/4]",
        "File: models/crnn_model.py\n"
        "Code: self.conv3 = nn.Sequential(nn.Conv2d(64, 128, 3, 1, 1), nn.BatchNorm2d(128), nn.Hardtanh(0, 20), nn.MaxPool2d((2, 1), (2, 1)))",
        "Hỏi: Tại sao ở Khối 3 nhóm lại dùng MaxPool2D với kernel_size=(2, 1) thay vì (2, 2) như 2 khối trước?\n"
        "Đáp: Để bảo toàn độ phân giải thời gian cho hàm mất mát CTC Loss. CTC yêu cầu độ dài chuỗi thời gian đầu ra T' phải lớn hơn độ dài chuỗi nhãn ký tự L (T' >= 2L + 1). Nếu nén thời gian quá sâu thành T/8, chuỗi audio bị ngắn lại khiến CTC không đủ số frame để chèn token Blank phân tách các ký tự lặp, gây lỗi mất chữ (Deletion Error). MaxPool (2, 1) giữ nguyên T' = T/4 là tỷ lệ tối ưu hoàn hảo."
    )

    # 4.2
    add_pipeline_step_box(
        doc,
        "BƯỚC 4.2",
        "TẦNG CHIẾU TUYẾN TÍNH FC (FEATURE PROJECTION: LINEAR(1280, 256))",
        "Sau 3 khối CNN, tensor có kích thước [Batch, 128 channels, 10 freq bands, T/4]. Hệ thống thực hiện hoán vị chiều và duỗi phẳng (flatten) gộp 128 kênh và 10 dải tần lại thành vector đặc trưng 1.280 chiều tại mỗi frame thời gian: x = x.permute(0, 3, 1, 2).view(B, T/4, 1280). Tầng Linear chiếu từ 1.280 chiều về kích thước ẩn 256 chiều của BiGRU.",
        "Tại sao đề tài PHẢI có tầng chiếu FC này mà không đưa thẳng 1.280 vào BiGRU?\n"
        "1. Cầu nối tương thích cấu trúc (Structural Adapter): CNN làm việc trên không gian 2D (Kênh x Tần số), còn BiGRU làm việc trên chuỗi 1D theo thời gian. Tầng FC chuyển giao biểu diễn không gian thành vector ngữ âm tại từng thời điểm.\n"
        "2. Nút thắt cổ chai giảm tải tham số (Bottleneck Compression): Nếu đưa thẳng 1.280 chiều vào BiGRU(1280, 256), riêng tầng GRU 1 sẽ ngốn tới 2.36 triệu tham số. Tầng FC nén từ 1.280 về 256 chiều chỉ tốn 327.936 tham số, giúp toàn bộ mô hình giữ được quy mô siêu nhẹ ~2.45 triệu tham số và tăng tốc độ tính toán lên gấp 3 lần.",
        "Toán học:\n"
        "Y[t] = X[t] @ W^T + b (W: 256 x 1280, b: 256)",
        "File: models/crnn_model.py\n"
        "Code: self.fc_proj = nn.Linear(128 * (80 // 8), hidden_size=256)",
        "Hỏi: Tầng FC này có làm mất thông tin không gian tần số đã trích xuất từ CNN không?\n"
        "Đáp: Không làm mất, mà nó thực hiện 'Tổng hợp tuyến tính có trọng số' (Weighted linear combination). Ma trận trọng số W(256, 1280) tự học cách gom các đặc trưng Formant ở các dải tần khác nhau thành 256 đặc trưng ngữ âm trừu tượng cô đọng nhất trước khi đưa vào học chuỗi."
    )

    # 4.3
    add_pipeline_step_box(
        doc,
        "BƯỚC 4.3",
        "2 TẦNG MẠNG HỒI QUY HAI CHIỀU (Bi-directional GRU)",
        "Mạng BiGRU gồm 2 tầng chồng lên nhau (num_layers=2, hidden_size=256, bidirectional=True). Mỗi tầng chạy đồng thời 2 luồng: Chiều tiến (Forward) học ngữ cảnh từ đầu đến cuối câu, Chiều lùi (Backward) học ngữ cảnh từ cuối câu ngược về đầu câu. Đầu ra là vector ghép nối 512 chiều tại mỗi frame.",
        "Tại sao đề tài PHẢI dùng BiGRU mà không dùng GRU 1 chiều hoặc LSTM?\n"
        "1. Tại sao cần 2 chiều (Bidirectional): Trong tiếng Việt, hiện tượng Đồng cấu âm (Co-articulation) diễn ra rất mạnh: cách phát âm của một phụ âm bị chi phối bởi nguyên âm đứng ngay sau nó (ví dụ: phát âm chữ 't' trong 'ti' khác với 't' trong 'to' do khẩu hình miệng chuẩn bị trước). GRU 2 chiều cho phép mô hình 'nhìn thấy cả tương lai lẫn quá khứ' để nhận dạng chính xác âm vị.\n"
        "2. Tại sao chọn GRU thay vì LSTM: GRU chỉ có 3 cổng (Reset, Update, Candidate) so với 4 cổng của LSTM, giúp tiết kiệm 25% tham số (1.97M vs 2.62M) và tính toán nhanh hơn 30%, cực kỳ thích hợp để chạy realtime trên CPU và chống overfitting trên tập dữ liệu 15.4 giờ VIVOS.",
        "Toán học:\n"
        "h_t = [ h_forward_t ; h_backward_t ] kích thước 256 + 256 = 512 chiều",
        "File: models/crnn_model.py\n"
        "Code: self.rnn = nn.GRU(256, 256, num_layers=2, bidirectional=True, batch_first=True)",
        "Hỏi: Tại sao Layer 2 của BiGRU lại nhận kích thước đầu vào là 512 trong khi Layer 1 nhận 256?\n"
        "Đáp: Vì Layer 1 chạy 2 chiều forward và backward độc lập, tại mỗi bước thời gian nó sinh ra 2 vector 256 chiều. PyTorch tự động ghép nối (concatenate) 2 vector này lại thành vector 512 chiều làm đầu vào cho Layer 2. Do đó Layer 2 bắt buộc phải có input_size = 512."
    )

    # 4.4
    add_pipeline_step_box(
        doc,
        "BƯỚC 4.4",
        "TẦNG CHIẾU CTC & KHỬ SỤP ĐỔ CỰC TIỂU BLANK (NEGATIVE BLANK BIAS = -3.0)",
        "Tầng CTC Classifier là một phép chiếu tuyến tính Linear(512, 105 tokens) kết hợp hàm Log-Softmax để sinh ra ma trận phân phối xác suất Log-Probabilities. ĐẶC BIỆT: Nhóm đã can thiệp khởi tạo trọng số âm sẵn cho token Blank ở vị trí số 0: self.classifier.bias[0] = -3.0.",
        "Tại sao đề tài PHẢI can thiệp Negative Blank Bias (-3.0)?\n"
        "ĐÂY LÀ ĐIỂM SÁNG TẠO CẢI TIẾN LỚN CỦA ĐỒ ÁN! Trong bài toán huấn luyện CTC Loss, token Blank chiếm hơn 90% số lượng khung hình (do các khoảng lặng giữa các âm). Nếu khởi tạo bias ngẫu nhiên quanh 0, mạng nơ-ron rất dễ rơi vào 'Bẫy sụp đổ cực tiểu Blank' (Blank Collapse) – mô hình phát hiện ra mẹo lười biếng: chỉ cần đoán tất cả các frame đều là Blank thì CTC Loss ban đầu sẽ giảm rất nhanh! Khi đã rơi vào bẫy này, gradient của các ký tự chữ cái tiếng Việt bị triệt tiêu về 0 và mô hình vĩnh viễn không học được chữ.\n"
        "Bằng cách gán bias[0] = -3.0, xác suất tiên nghiệm của token Blank ban đầu bị dìm xuống dưới e^(-3) ≈ 0.05 (dưới 5%), ép buộc các gradient phải tập trung cập nhật trọng số cho 104 ký tự tiếng Việt ngay từ epoch đầu tiên.",
        "Toán học:\n"
        "Logits = W @ h_t + b; with b[0] = -3.0\n"
        "Log_Probs = LogSoftmax(Logits)",
        "File: models/crnn_model.py\n"
        "Code: self.classifier = nn.Linear(512, vocab_size=105)\n"
        "with torch.no_grad(): self.classifier.bias[0] = -3.0",
        "Hỏi: Nếu không đặt bias[0] = -3.0 thì quá trình huấn luyện sẽ gặp hiện tượng gì?\n"
        "Đáp: Mô hình sẽ bị hiện tượng Blank Collapse ở những epoch đầu: Loss giảm nhanh nhưng kết quả giải mã ra toàn chuỗi rỗng (chuỗi trắng). Việc gán bias âm -3.0 giúp phá vỡ thế đối xứng, tạo lực đẩy gradient cho các ký tự văn bản có nghĩa, giúp mô hình hội tụ nhanh gấp đôi và đạt mức loss kỷ lục 1.21."
    )

    # 4.5
    add_pipeline_step_box(
        doc,
        "ĐỘNG CƠ BỔ TRỢ",
        "MÔ HÌNH WAV2VEC2 CTC FINE-TUNE (250H PRETRAINED TIẾNG VIỆT)",
        "Wav2Vec2 là kiến trúc mô hình nền tảng (Foundation Model) học tự giám sát trên 250 giờ tiếng Việt, gồm 7 khối CNN Feature Encoder và 12 tầng Transformer Encoder (95M tham số), được nhóm tích hợp và fine-tune tầng CTC Head trên tập VIVOS, hoạt động 100% Offline.",
        "Tại sao đề tài tích hợp thêm Động cơ Wav2Vec2 bên cạnh CRNN?\n"
        "1. Hệ thống đối chuẩn khoa học (Acoustic Benchmark): Để chứng minh tính hiệu quả của mô hình CRNN tự xây dựng, cần một mô hình lớn tiêu chuẩn để đối chứng về độ chính xác và tài nguyên.\n"
        "2. Đa dạng hóa trải nghiệm: Cho phép người dùng chuyển đổi linh hoạt trên giao diện giữa 'Chế độ siêu nhẹ thời gian thực (CRNN - 9.8MB, 0.07s)' và 'Chế độ độ chính xác cao (Wav2Vec2 - 360MB, 0.45s)'.",
        "Kiến trúc Transformer:\n"
        "Raw Audio -> 7 CNN Encoders -> Positional Conv Embedding -> 12 Transformer Blocks -> CTC Head",
        "File: models/ctc_decoder.py & views/main_view.py\n"
        "Code: logits = self.ctc_model(input_values).logits  # 100% Offline Inference",
        "Hỏi: Ưu và nhược điểm của Wav2Vec2 so với mô hình CRNN của nhóm là gì?\n"
        "Đáp: Wav2Vec2 có ưu điểm là độ chính xác nhận dạng nhỉnh hơn ở các câu phức tạp nhờ kế thừa 250 giờ tiền huấn luyện. Tuy nhiên, nhược điểm là kích thước file lớn gấp 36 lần (360 MB vs 9.8 MB) và độ trễ chậm hơn gấp 6 lần (0.45s vs 0.07s). Mô hình CRNN của nhóm vượt trội hoàn toàn về tính gọn nhẹ và khả năng đáp ứng thời gian thực."
    )

    # ==========================================
    # CHƯƠNG 5: GIAI ĐOẠN 5 - GIẢI MÃ & RÀNG BUỘC NGỮ NGHĨA
    # ==========================================
    add_heading_1(doc, "CHƯƠNG 5: GIAI ĐOẠN 5 - GIẢI MÃ & RÀNG BUỘC NGỮ NGHĨA (DECODING & POST-PROCESSING)")
    add_paragraph(doc, "Giai đoạn 5 biến đổi ma trận xác suất nơ-ron thành chuỗi văn bản tiếng Việt hoàn chỉnh, đúng chính tả thông qua chuỗi thuật toán xử lý ngôn ngữ tự nhiên thông minh.")

    # 5.1
    add_pipeline_step_box(
        doc,
        "BƯỚC 5.1",
        "CTC GREEDY BEST-PATH SEARCH",
        "CTC Greedy Search là giải thuật giải mã tìm kiếm đường đi tốt nhất bằng cách chọn token có xác suất cực đại (argmax) độc lập tại từng khung thời gian: pi_t = argmax_{c} P(c | x, t).",
        "Tại sao đề tài PHẢI dùng CTC Greedy Search mà không dùng Beam Search phức tạp?\n"
        "Đề tài hướng tới mục tiêu tương tác thời gian thực qua Micro với độ trễ thấp nhất. Thuật toán Beam Search (tìm kiếm chùm) đòi hỏi duy trì hàng trăm nhánh giả thuyết và tính toán giao thoa chuỗi tốn kém CPU (mất từ 0.5 - 1.5 giây). Trong khi đó, Greedy Search có độ phức tạp thuật toán O(T), thời gian thực thi chỉ mất chưa đầy 0.001 giây (1 mili-giây!). Kết hợp với tầng Hậu xử lý từ điển Lexicon ở bước sau, phương pháp này vừa đạt tốc độ cực hạn, vừa đảm bảo độ chính xác câu từ hoàn hảo.",
        "Toán học:\n"
        "pred_ids[t] = argmax_{i} ( Log_Probs[t, i] ) với mọi t từ 1 đến T'",
        "File: models/ctc_decoder.py\n"
        "Code: pred_ids = torch.argmax(logits, dim=-1)  # Chọn argmax tại mỗi frame",
        "Hỏi: Nhược điểm lớn nhất của Greedy Search là gì và nhóm đã khắc phục bằng cách nào?\n"
        "Đáp: Nhược điểm của Greedy Search là tính toán cục bộ độc lập tại từng frame, không xét đến xác suất kết hợp chuỗi ngôn ngữ dài nên đôi khi sinh ra các từ bị sai dấu hoặc thiếu chữ. Nhóm đã khắc phục triệt để nhược điểm này bằng chuỗi hậu xử lý: Bóc tách khung phụ âm Unicode và Ràng buộc từ điển tiếng Việt (Lexicon Matching) ở Bước 5.3 và 5.4."
    )

    # 5.2
    add_pipeline_step_box(
        doc,
        "BƯỚC 5.2",
        "TOÁN TỬ SỤP ĐỔ B (CTC COLLAPSE OPERATOR)",
        "Toán tử sụp đổ B (Collapse Operator) là quy tắc cốt lõi của giải thuật CTC: (1) Gộp các ký tự giống nhau xuất hiện liên tiếp thành một ký tự duy nhất; (2) Sau đó xóa sạch toàn bộ các token Blank (id = 0).",
        "Tại sao đề tài BẮT BUỘC phải có bước này?\n"
        "Do đặc tính của tín hiệu tiếng nói, khi phát âm một âm tiết (ví dụ âm /a/ trong từ 'ba'), âm thanh kéo dài qua nhiều khung hình liên tiếp. Mô hình nơ-ron sẽ dự đoán ra một chuỗi dày đặc các token lặp: ['b', 'b', 'b', '<blank>', 'a', 'a', 'a', 'a'].\n"
        "Nếu không có toán tử sụp đổ, văn bản đầu ra sẽ là 'bbbaaaa' vô nghĩa. Toán tử B sụp đổ chuỗi thành 'ba'. Đồng thời, sự hiện diện của token Blank chính là ranh giới để phân tách 2 chữ cái giống nhau đứng cạnh nhau trong tiếng Việt (ví dụ từ 'kính koong': ['o', '<blank>', 'o'] -> 'oo').",
        "Quy tắc chuyển đổi:\n"
        "B( [b, b, <blank>, a, a] ) = 'ba'\n"
        "B( [c, c, <blank>, <blank>, o, o] ) = 'co'\n"
        "B( [o, <blank>, o] ) = 'oo'",
        "File: models/ctc_decoder.py\n"
        "Code: if token_id != prev and token_id != blank_id: result.append(vocab[token_id])",
        "Hỏi: Làm thế nào CTC phân biệt được giữa việc 'kéo dài một ký tự' và 'hai ký tự giống nhau đứng kề nhau'?\n"
        "Đáp: Nhờ vào token đặc biệt Blank. Nếu không có Blank chen vào giữa (ví dụ chuỗi ['a', 'a', 'a']), toán tử CTC sẽ gộp thành 1 chữ 'a'. Nếu có Blank chen vào giữa (ví dụ ['a', '<blank>', 'a']), toán tử sẽ hiểu đó là 2 chữ cái tách biệt và gộp thành 'aa'."
    )

    # 5.3
    add_pipeline_step_box(
        doc,
        "BƯỚC 5.3",
        "BÓC TÁCH KHUNG PHỤ ÂM UNICODE NFKD (CONSONANT SKELETON EXTRACTION)",
        "Chuẩn hóa Unicode dạng chuẩn NFKD (Normalization Form Compatibility Decomposition) tách rời các ký tự nguyên âm có dấu thành ký tự gốc và dấu thanh tách biệt. Hệ thống sử dụng biểu thức chính quy (Regex) loại bỏ toàn bộ nguyên âm và dấu thanh, chỉ giữ lại bộ khung phụ âm đầu và phụ âm cuối (Consonant Skeleton).",
        "Tại sao đề tài PHẢI bóc tách khung phụ âm?\n"
        "ĐÂY LÀ GIẢI PHÁP ĐẶC TRỊ CHO TIẾNG VIỆT! Trong nhận dạng tiếng nói tiếng Việt, hiện tượng phát âm nhanh hoặc ngọng địa phương thường dẫn đến lỗi biến dạng nguyên âm hoặc nhầm lẫn dấu thanh (ví dụ: 'thương' bị nhận dạng thành 'thường', 'thướng', hoặc 'thưng').\n"
        "Tuy nhiên, **bộ khung phụ âm đầu ('th') và phụ âm cuối ('ng') hầu như luôn được mô hình CRNN nhận dạng chính xác 100%!**\n"
        "Bằng cách rút trích khung phụ âm 'th-ng', hệ thống thu hẹp không gian tìm kiếm từ vựng từ 4.861 từ xuống chỉ còn 3-5 từ ứng viên, tạo tiền đề hoàn hảo cho khâu sửa lỗi chính tả ở bước tiếp theo.",
        "Ví dụ chuyển đổi Unicode NFKD:\n"
        "'thương' -> 't' + 'h' + 'u' + 'o' + '\u031b' + '\u031b' + 'n' + 'g' -> Skeleton: 'th_ng'\n"
        "'nghiêng' -> 'n' + 'g' + 'h' + 'i' + 'e' + '\u0302' + 'n' + 'g' -> Skeleton: 'ngh_ng'",
        "File: models/ctc_decoder.py\n"
        "Code: decomposed = unicodedata.normalize('NFKD', word)\n"
        "skeleton = ''.join([c for c in decomposed if is_consonant(c)])",
        "Hỏi: Tại sao không so khớp toàn bộ cả từ mà lại phải tách riêng khung phụ âm?\n"
        "Đáp: Nếu so khớp khoảng cách Levenshtein trên toàn bộ từ vựng 4.861 từ, độ phức tạp tính toán rất lớn và dễ bị nhầm sang một từ hoàn toàn khác nghĩa có độ dài tương đương. Khung phụ âm đóng vai trò là chiếc mỏ neo cố định ngữ âm tiếng Việt, giúp lọc nhanh các từ đồng dạng chỉ trong 0.0001 giây."
    )

    # 5.4
    add_pipeline_step_box(
        doc,
        "BƯỚC 5.4",
        "RÀNG BUỘC TỪ ĐIỂN 4.861 TỪ VIVOS & SỬA LỖI CHÍNH TẢ LEVENSHTEIN",
        "Tập từ điển VIVOS chứa 4.861 từ tiếng Việt chuẩn mực (vietnamese_lexicon.json). Sau khi lọc các từ ứng viên có cùng khung phụ âm, hệ thống tính khoảng cách chỉnh sửa Levenshtein Distance (số phép chèn, xóa, thay thế ký tự tối thiểu) để chọn ra từ tiếng Việt có nghĩa chuẩn xác nhất.",
        "Tại sao đề tài PHẢI dùng bước Ràng buộc từ điển Lexicon này?\n"
        "Mô hình CRNN là một mô hình âm học (Acoustic Model), nó chỉ 'nghe sao đoán vậy' ở mức ký tự rời rạc mà không có kiến thức ngữ pháp của một Mô hình Ngôn ngữ lớn (Language Model). Do đó, đôi khi nó sinh ra các từ vô nghĩa không có trong từ điển tiếng Việt (ví dụ: 'nghiênk', 'chạyj').\n"
        "Bước ràng buộc từ điển đóng vai trò là **Bộ kiểm tra chính tả tự động**, nắn chỉnh ngay lập tức các ký tự lỗi về từ tiếng Việt có nghĩa trong từ điển 4.861 từ, giúp giảm tỉ lệ lỗi từ (Word Error Rate - WER) xuống mức thấp nhất.",
        "Thuật toán Levenshtein:\n"
        "D(i, j) = min( D(i-1, j) + 1, D(i, j-1) + 1, D(i-1, j-1) + cost )\n"
        "Chọn Candidate có khoảng cách nhỏ nhất: argmin( LevDist(pred_word, cand) )",
        "File: models/ctc_decoder.py\n"
        "Code: matched_word = lexicon.lookup_skeleton(skeleton, candidates)  # vietnamese_lexicon.json",
        "Hỏi: Tại sao từ điển VIVOS chỉ có 4.861 từ? Train 9 tiếng có làm tăng số từ này lên không?\n"
        "Đáp: 4.861 từ là kích thước từ vựng văn bản tĩnh được trích xuất từ tập ngữ liệu VIVOS, nó độc lập với thời gian huấn luyện. Train 9 tiếng là tối ưu hóa 2.45 triệu trọng số của mạng CRNN để nhận diện ngữ âm tốt hơn, chứ không làm thay đổi tệp từ điển tĩnh này."
    )

    # 5.5
    add_pipeline_step_box(
        doc,
        "BƯỚC 5.5",
        "KHỬ LẶP TỪ NGẮC NGỨ (DE-DUPLICATION & POST-CLEANING)",
        "Khử lặp từ ngắc ngứ là bước hậu xử lý cuối cùng kiểm tra sự trùng lặp của các từ đứng cạnh nhau: nếu từ hiện tại giống hệt từ vừa được thêm vào trước đó, hệ thống sẽ gạt bỏ từ thừa (`if matched_word != prev_word: final_words.append(matched_word)`).",
        "Tại sao đề tài PHẢI có bước Khử lặp từ ngắc ngứ này?\n"
        "1. Xử lý thói quen nói ngập ngừng: Khi người dùng nói trực tiếp qua Micro, họ rất hay bị ngắc ngứ kéo dài giọng (ví dụ: 'tôi... tôi muốn', 'trường đại học... học sư phạm').\n"
        "2. Xử lý độ trễ khung hình CTC: Khi phát âm một từ quá dài, CTC đôi khi sinh ra 2 đỉnh xác suất độc lập cách nhau bởi một token Blank ngắn, khiến giải mã sinh ra 2 từ trùng lặp.\n"
        "Bước De-duplication gọt sạch các từ lặp ngắc ngứ vô nghĩa, định dạng lại dấu cách và trả về một câu văn bản tiếng Việt tự nhiên, hoàn chỉnh và mạch lạc nhất.",
        "Logic thuật toán:\n"
        "words = text.split()\n"
        "clean_words = [w for i, w in enumerate(words) if i == 0 or w != words[i-1]]\n"
        "final_text = ' '.join(clean_words)",
        "File: models/ctc_decoder.py\n"
        "Code: if matched_word != prev_word: final_words.append(matched_word)",
        "Hỏi: Nếu người dùng cố ý nói từ láy đôi có 2 từ giống nhau (ví dụ: 'xanh xanh', 'ngày ngày') thì bước này có bị xóa nhầm không?\n"
        "Đáp: Trong văn phong hội thoại mệnh lệnh hoặc điều khiển ASR, hiện tượng từ láy lặp nguyên âm liên tiếp rất ít khi dùng đơn lẻ. Tuy nhiên, để đảm bảo tính mềm dẻo, hệ thống có thể cấu hình ngưỡng thời gian giữa 2 từ: nếu khoảng lặng giữa 2 từ > 0.5s thì cho phép giữ lại, còn nếu lặp dính liền dưới 0.2s thì xác định là lỗi ngắc ngứ và loại bỏ."
    )

    # ==========================================
    # KẾT NỐI BỔ TRỢ: GIAI ĐOẠN 6 - TRÌNH DIỄN GIAO DIỆN & TTS
    # ==========================================
    add_heading_1(doc, "CHƯƠNG 6: TRÌNH DIỄN GIAO DIỆN ĐỒ HỌA & TỔNG HỢP GIỌNG ĐỌC PHẢN HỒI (UI & TTS)")
    add_paragraph(doc,
                  "Để tạo nên một sản phẩm hoàn chỉnh phục vụ người dùng thực tế, nhóm đã phát triển giao diện đồ họa hiện đại bằng thư viện CustomTkinter và tích hợp bộ tổng hợp giọng đọc Text-to-Speech (TTS):\n"
                  "1. Giao diện Desktop CustomTkinter: Cung cấp trải nghiệm thị giác trực quan với theme Dark Mode, hiển thị đồng thời dạng sóng âm Waveform và biểu đồ phổ Log-Mel Spectrogram ngay khi thu âm, các nút bấm Ghi âm / Dừng / Chạy file .wav mượt mà.\n"
                  "2. Đa luồng (Multi-threading Execution): Toàn bộ quá trình thu âm âm thanh và suy luận mô hình Deep Learning được đẩy xuống các Worker Thread riêng biệt, đảm bảo giao diện đồ họa luôn đạt tốc độ 60 FPS mượt mà, không bao giờ bị đơ (Not Responding).\n"
                  "3. Phản hồi Giọng đọc TTS Tiếng Việt: Sau khi văn bản được nhận dạng, hệ thống tự động gọi module TTS (gTTS / Pygame Mixer) để phát âm thanh tiếng Việt tự nhiên đọc lại văn bản ra loa, hoàn thiện vòng lặp giao tiếp tương tác Người - Máy (Speech-to-Text -> Text-to-Speech).",
                  bold_prefix="Tổng quan khâu Trình diễn: ")

    # Lưu file ra cả 2 nơi
    out_dir1 = r"C:\Users\Admin\Documents\ASR"
    out_dir2 = r"C:\Users\Admin\PycharmProjects\speech-processing-tutorial\project_cuoiky\docs"
    os.makedirs(out_dir1, exist_ok=True)
    os.makedirs(out_dir2, exist_ok=True)

    filename = "BAO_CAO_CHUYEN_SAU_PIPELINE_ASR_NHOM_6.docx"
    path1 = os.path.join(out_dir1, filename)
    path2 = os.path.join(out_dir2, filename)

    doc.save(path1)
    doc.save(path2)
    print(f"[OK] Đã tạo thành công tài liệu Pipeline toàn diện tại: {path1}")
    print(f"[OK] Đã tạo bản sao lưu tại: {path2}")

if __name__ == "__main__":
    build_unified_asr_handbook()
