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

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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
    p_title.paragraph_format.space_after = Pt(2)
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

def add_layer_card(doc, layer_name, explanation, formula, calculation, role, total_str):
    """
    Tạo bảng thẻ (Card) chuẩn hóa 4 phần cho từng Layer
    """
    table = doc.add_table(rows=5, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    col_widths = [Inches(1.8), Inches(5.0)]

    # Hàng tiêu đề Layer
    r0 = table.rows[0]
    r0.cells[0].merge(r0.cells[1])
    p_head = r0.cells[0].paragraphs[0]
    p_head.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_head1 = p_head.add_run(f"📌 {layer_name}   |   ")
    r_head1.font.name = "Times New Roman"
    r_head1.font.size = Pt(11.5)
    r_head1.font.bold = True
    r_head1.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    r_head2 = p_head.add_run(f"Tổng tham số: {total_str}")
    r_head2.font.name = "Times New Roman"
    r_head2.font.size = Pt(11.5)
    r_head2.font.bold = True
    r_head2.font.color.rgb = RGBColor(0xFF, 0xCC, 0x00) # Gold accent
    set_cell_background(r0.cells[0], "1B365D")

    sections = [
        ("1. Cách hiểu bản chất\n(Intuitive Concept)", explanation, "F9FAFC"),
        ("2. Công thức toán học\n(Mathematical Formula)", formula, "FFFFFF"),
        ("3. Thay số chi tiết đồ án\n(Detailed Calculation)", calculation, "EBF3FA"),
        ("4. Vai trò trong ASR\n(Role in Model)", role, "FFF9F2")
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

def generate_beautified_doc():
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    add_header(
        doc,
        "CẨM NANG TOÁN HỌC & BÓC TÁCH THAM SỐ HỌC ĐƯỢC (WEIGHT & BIAS)",
        "MÔ HÌNH NHẬN DẠNG TIẾNG NÓI CRNN-CTC TIẾNG VIỆT",
        "Bộ môn: Xử lý Tiếng nói | GVHD: TS. Phù Khắc Anh | Nhóm thực hiện: Nhóm 6 (Trưởng nhóm phụ trách)"
    )

    # ==========================================
    # LỜI NÓI ĐẦU & NGUYÊN TẮC BẤT BIẾN
    # ==========================================
    add_heading_1(doc, "LỜI MỞ ĐẦU: BẢN CHẤT CỦA WEIGHT VÀ BIAS TRONG MẠNG NƠ-RON")
    add_paragraph(doc,
                  "Trong học sâu (Deep Learning) nói chung và bài toán Nhận dạng tiếng nói tự động (ASR) nói riêng, các tham số cần học (Learnable Parameters) của mô hình là những giá trị số thực được tối ưu hóa liên tục thông qua thuật toán Lan truyền ngược (Backpropagation) và Bộ tối ưu AdamW để giảm thiểu hàm mất mát CTC Loss.",
                  bold_prefix="Định nghĩa tổng quan: ")

    add_paragraph(doc,
                  "Là ma trận các hệ số khuếch đại thể hiện độ quan trọng của mối liên kết giữa nơ-ron đầu vào và nơ-ron đầu ra. Weight làm nhiệm vụ co giãn không gian đặc trưng (Scaling / Rotation) để trích xuất các dải Formant hoặc biến đổi ngữ cảnh thời gian.",
                  bold_prefix="1. Weight (Trọng số W): ")

    add_paragraph(doc,
                  "Là vector độ lệch được cộng thêm độc lập vào tổng có trọng số (Affine transformation: Y = X * W^T + b). Bias cho phép hàm kích hoạt dịch chuyển sang trái hoặc sang phải (Translation / Shifting) dọc theo trục tọa độ, giúp nơ-ron có khả năng kích hoạt ngay cả khi đầu vào xấp xỉ 0.",
                  bold_prefix="2. Bias (Độ lệch b): ")

    add_paragraph(doc,
                  "Khi tính toán số lượng tham số học được của một mạng nơ-ron ASR, chúng ta chỉ đếm các tham số nội tại cố định của kiến trúc mạng (Weights và Biases). Số lượng khung thời gian T (Time frames) của file âm thanh TUYỆT ĐỐI KHÔNG được nhân vào số lượng Weight/Bias. Lý do: mạng CRNN sử dụng cơ chế Chia sẻ trọng số theo thời gian (Weight Sharing across Time) – cùng một bộ trọng số Conv2D, cùng một tế bào BiGRU và cùng một ma trận Linear Classifier được tái sử dụng tuần hoàn cho mọi frame t từ 1 đến T.",
                  bold_prefix="⭐ NGUYÊN TẮC BẤT BIẾN (HỘI ĐỒNG RẤT HAY BẪY): ")

    add_paragraph(doc,
                  "Trong toàn bộ 5 giai đoạn của đồ án, chỉ có Giai đoạn 4 (Mạng nơ-ron CRNN) là chứa Weight và Bias học được. Giai đoạn 1 & 2 (Tiền xử lý: STFT, Mel Filterbank, Hann Window, CMVN) hoàn toàn là các phép biến đổi xử lý tín hiệu số cố định (Static DSP). Giai đoạn 5 (CTC Greedy Decoding, Ràng buộc từ điển Lexicon) là các thuật toán suy luận và tìm kiếm chuỗi ký tự, hoàn toàn không có tham số học được.",
                  bold_prefix="Phân định 5 giai đoạn: ")

    # ==========================================
    # BẢNG TỔNG KẾT MASTER
    # ==========================================
    add_heading_1(doc, "BẢNG TỔNG HỢP MASTER: CHI TIẾT THAM SỐ CỦA MÔ HÌNH CRNN-CTC")
    add_paragraph(doc, "Bảng đối soát đầy đủ toàn bộ các tầng mạng trong mã nguồn models/crnn_model.py và file trọng số models/weights/vivos_ctc_model.pth của nhóm:")

    table_master = doc.add_table(rows=10, cols=7)
    table_master.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_master.style = 'Table Grid'
    headers = ["STT", "Tầng mạng (Layer)", "Cấu hình Kích thước", "Công thức tính", "Weight", "Bias", "Tổng cộng"]
    for i, h in enumerate(headers):
        c = table_master.rows[0].cells[i]
        c.text = h
        c.paragraphs[0].runs[0].font.name = "Times New Roman"
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(9.5)
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(c, "1B365D")

    master_data = [
        ("1", "Conv1 + BatchNorm1", "Cin=1, Cout=32, K=3x3", "32x1x3x3 + 32 + 2x32", "288", "32 + 64", "384"),
        ("2", "Conv2 + BatchNorm2", "Cin=32, Cout=64, K=3x3", "64x32x3x3 + 64 + 2x64", "18,432", "64 + 128", "18,624"),
        ("3", "Conv3 + BatchNorm3", "Cin=64, Cout=128, K=3x3", "128x64x3x3 + 128 + 2x128", "73,728", "128 + 256", "74,112"),
        ("4", "FC Projection (Linear)", "In=1,280 -> Out=256", "256 x 1,280 + 256", "327,680", "256", "327,936"),
        ("5", "BiGRU Layer 1", "In=256, Hidden=256 (2 chiều)", "2 x [3x256x256 + 3x256² + 6x256]", "786,432", "3,072", "789,504"),
        ("6", "BiGRU Layer 2", "In=512, Hidden=256 (2 chiều)", "2 x [3x256x512 + 3x256² + 6x256]", "1,179,648", "3,072", "1,182,720"),
        ("7", "CTC Classifier", "In=512 -> Out=105 tokens", "105 x 512 + 105", "53,760", "105", "53,865"),
        ("--", "TỔNG THAM SỐ TRAINABLE", "Toàn bộ mạng CRNN-CTC", "Tổng cộng 7 khối trên", "2,439,968", "7,177", "2,447,145"),
        ("⭐", "KÍCH THƯỚC FILE (.pth)", "Checkpoint float32 lưu đĩa", "Gồm cả running stats BatchNorm", "--", "--", "~9.79 MB")
    ]

    for row_idx, rdata in enumerate(master_data, start=1):
        row = table_master.rows[row_idx]
        for col_idx, val in enumerate(rdata):
            cell = row.cells[col_idx]
            cell.text = val
            p = cell.paragraphs[0]
            p.runs[0].font.name = "Times New Roman"
            p.runs[0].font.size = Pt(9)
            p.paragraph_format.line_spacing = 1.15
            if row_idx == 8: # Hàng tổng cộng
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(0x99, 0x00, 0x00)
                set_cell_background(cell, "FFF2E6")
            elif row_idx == 9: # Hàng file size
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(0x00, 0x4B, 0x87)
                set_cell_background(cell, "E8F4F8")
            elif col_idx in [0, 4, 5, 6]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if col_idx == 6:
                    p.runs[0].font.bold = True
                set_cell_background(cell, "F9FAFC")
            else:
                set_cell_background(cell, "FFFFFF")

    for row in table_master.rows:
        for i, w in enumerate([Inches(0.4), Inches(1.8), Inches(1.6), Inches(1.8), Inches(0.8), Inches(0.7), Inches(0.9)]):
            row.cells[i].width = w
            set_cell_margins(row.cells[i], top=60, bottom=60, left=60, right=60)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(10)

    # ==========================================
    # PHẦN I: KHỐI TÍCH CHẬP 2D & BATCH NORMALIZATION
    # ==========================================
    add_heading_1(doc, "PHẦN I: KHỐI TÍCH CHẬP 2D & CHUẨN HÓA THEO BATCH (CONV2D & BATCHNORM)")
    add_paragraph(doc,
                  "Khối tích chập trong đồ án gồm 3 tầng Conv2D liên tiếp kết hợp BatchNorm2D, hàm kích hoạt Hardtanh và MaxPool2D. Khối này làm nhiệm vụ quét các bộ lọc không gian cục bộ (Local Receptive Fields) trên ma trận Log-Mel Spectrogram để trích xuất các dải Formant nguyên âm và đặc trưng chuyển tiếp phụ âm.")

    # 1. Conv1 + BN1
    add_layer_card(
        doc,
        "1. KHỐI TÍCH CHẬP 1 (Conv1 + BatchNorm1)",
        "Conv1 nhận đầu vào là ma trận Mel Spectrogram đơn kênh (Cin = 1 channel) và tạo ra 32 bản đồ đặc trưng (Cout = 32 channels). Kích thước mỗi bộ lọc (kernel) là 3 x 3.\n"
        "- Mỗi output channel cần 1 kernel 3D kích thước (Cin x Kh x Kw) = (1 x 3 x 3) = 9 trọng số.\n"
        "- Có 32 output channels nên có 32 kernel độc lập, cùng 32 giá trị Bias riêng biệt.\n"
        "- BatchNorm1 chuẩn hóa đầu ra của 32 channels, mỗi channel có 2 tham số học được là scale (gamma) và shift (beta).",
        "• Số Weight Conv2d = Cout x Cin x Kh x Kw\n"
        "• Số Bias Conv2d = Cout\n"
        "• Số tham số BatchNorm2d = 2 x Cout (gồm Cout gamma + Cout beta)\n"
        "• Tổng tham số Khối 1 = (Cout x Cin x Kh x Kw + Cout) + (2 x Cout)",
        "• Weight Conv1: 32 x 1 x 3 x 3 = 288 weights\n"
        "• Bias Conv1: 32 biases\n"
        "  => Tham số Conv1 = 288 + 32 = 320\n"
        "• Tham số BatchNorm1: 2 x 32 = 64 (32 gamma + 32 beta)\n"
        "  => TỔNG CỘNG KHỐI 1 = 320 + 64 = 384 tham số",
        "Bắt các chi tiết cạnh phổ cơ bản ở mức thấp (Low-level spectral edges), đồng thời tầng MaxPool2D(2, 2) nén giảm 1/2 trục tần số (80 -> 40) và 1/2 trục thời gian (T -> T/2) để giảm chiều dữ liệu tính toán.",
        "384 tham số"
    )

    # 2. Conv2 + BN2
    add_layer_card(
        doc,
        "2. KHỐI TÍCH CHẬP 2 (Conv2 + BatchNorm2)",
        "Conv2 nhận 32 channels từ Khối 1 (Cin = 32) và tạo ra 64 channels mới (Cout = 64). Bộ lọc vẫn có kích thước 3 x 3.\n"
        "- Mỗi output channel cần 1 khối kernel 3D quét qua toàn bộ 32 kênh đầu vào: (32 x 3 x 3) = 288 trọng số.\n"
        "- Với 64 output channels, ta có tổng cộng: 64 x 288 = 18,432 weights.\n"
        "- Mỗi output channel có 1 giá trị Bias riêng => 64 biases.\n"
        "- BatchNorm2 học 64 hệ số gamma và 64 hệ số beta cho 64 kênh đầu ra.",
        "• Weight Conv2 = Cout x Cin x Kh x Kw = 64 x 32 x 3 x 3\n"
        "• Bias Conv2 = Cout = 64\n"
        "• BatchNorm2 = 2 x Cout = 2 x 64 = 128\n"
        "• Tổng tham số Khối 2 = (18,432 + 64) + 128",
        "• Weight Conv2: 64 x 32 x 3 x 3 = 18,432 weights\n"
        "• Bias Conv2: 64 biases\n"
        "  => Tham số Conv2 = 18,432 + 64 = 18,496\n"
        "• Tham số BatchNorm2: 2 x 64 = 128\n"
        "  => TỔNG CỘNG KHỐI 2 = 18,496 + 128 = 18,624 tham số",
        "Kết hợp các cạnh phổ cơ bản thành các mẫu Formant nguyên âm bậc trung (Mid-level spectral patterns). Tầng MaxPool2D(2, 2) tiếp tục giảm tần số (40 -> 20) và thời gian (T/2 -> T/4).",
        "18,624 tham số"
    )

    # 3. Conv3 + BN3
    add_layer_card(
        doc,
        "3. KHỐI TÍCH CHẬP 3 (Conv3 + BatchNorm3)",
        "Conv3 nhận 64 channels từ Khối 2 (Cin = 64) và xuất ra 128 channels (Cout = 128). Kernel kích thước 3 x 3.\n"
        "- Mỗi output channel cần 1 khối kernel: (64 x 3 x 3) = 576 trọng số.\n"
        "- Có 128 output channels => 128 x 576 = 73,728 weights.\n"
        "- Kèm theo 128 giá trị Bias tương ứng.\n"
        "- BatchNorm3 học 128 gamma và 128 beta cho 128 channels.",
        "• Weight Conv3 = Cout x Cin x Kh x Kw = 128 x 64 x 3 x 3\n"
        "• Bias Conv3 = Cout = 128\n"
        "• BatchNorm3 = 2 x Cout = 2 x 128 = 256\n"
        "• Tổng tham số Khối 3 = (73,728 + 128) + 256",
        "• Weight Conv3: 128 x 64 x 3 x 3 = 73,728 weights\n"
        "• Bias Conv3: 128 biases\n"
        "  => Tham số Conv3 = 73,728 + 128 = 73,856\n"
        "• Tham số BatchNorm3: 2 x 128 = 256\n"
        "  => TỔNG CỘNG KHỐI 3 = 73,856 + 256 = 74,112 tham số",
        "Trích xuất các đặc trưng âm học bậc cao (High-level acoustic features). ĐẶC BIỆT: Tầng MaxPool2D(2, 1) chỉ giảm tần số (20 -> 10) nhưng GIỮ NGUYÊN trục thời gian T' = T/4 để bảo toàn độ phân giải âm vị cho CTC.",
        "74,112 tham số"
    )

    add_paragraph(doc,
                  "384 (Khối 1) + 18,624 (Khối 2) + 74,112 (Khối 3) = 93,120 tham số (chiếm khoảng 3.8% toàn bộ mô hình).",
                  bold_prefix="📊 TỔNG CỘNG 3 KHỐI CONV2D: ")

    # ==========================================
    # PHẦN II: TẦNG CHIẾU TUYẾN TÍNH (FC PROJECTION)
    # ==========================================
    add_heading_1(doc, "PHẦN II: TẦNG KẾT NỐI TUYẾN TÍNH (FC PROJECTION / LINEAR LAYER)")
    add_layer_card(
        doc,
        "4. TẦNG CHIẾU ĐẶC TRƯNG (FC Projection: Linear(1280, 256))",
        "Sau 3 khối CNN, tại mỗi bước thời gian (timestep), tensor đặc trưng có kích thước:\n"
        "  128 channels  x  10 dải tần số còn lại (80 mel bins // 8 = 10)\n"
        "Để chuẩn bị đưa vào mạng hồi quy BiGRU, tensor được biến đổi duỗi thẳng (flatten) kết hợp channel và tần số lại thành 1 vector 1 chiều tại mỗi frame:\n"
        "  Kích thước đặc trưng đầu vào: 128 x 10 = 1,280 chiều.\n"
        "Tầng Fully Connected (Linear) có nhiệm vụ chiếu vector 1,280 chiều này về đúng kích thước ẩn 256 chiều của BiGRU.",
        "Với tầng Tuyến tính nn.Linear(in_features, out_features):\n"
        "• Số Weight = out_features x in_features\n"
        "• Số Bias = out_features\n"
        "• Tổng tham số = out_features x in_features + out_features",
        "• in_features = 1,280 (128 channels x 10 freq bins)\n"
        "• out_features = 256 (hidden size của BiGRU)\n"
        "• Weight: 256 x 1,280 = 327,680 weights\n"
        "• Bias: 256 biases\n"
        "  => TỔNG CỘNG TẦNG FC = 327,680 + 256 = 327,936 tham số",
        "Đóng vai trò là cầu nối tương thích kích thước (Bottleneck adapter) giữa mạng trích xuất không gian CNN và mạng mô hình hóa chuỗi thời gian BiGRU, giúp giảm bớt số chiều dư thừa để BiGRU tính toán nhanh hơn.",
        "327,936 tham số"
    )

    # ==========================================
    # PHẦN III: KHỐI MẠNG HỒI QUY HAI CHIỀU (BiGRU)
    # ==========================================
    add_heading_1(doc, "PHẦN III: KHỐI MẠNG HỒI QUY HAI CHIỀU (BI-DIRECTIONAL GRU - BiGRU)")
    add_paragraph(doc,
                  "BiGRU là 'trái tim' của mô hình ASR, chịu trách nhiệm mô hình hóa ngữ cảnh âm thanh 2 chiều (quá khứ và tương lai). Khối này bao gồm 2 tầng BiGRU chồng lên nhau (2 layers), mỗi tầng chạy song song 2 chiều (Forward và Backward). Đây là khối chiếm tỉ trọng tham số áp đảo nhất (hơn 80% toàn mô hình).")

    add_paragraph(doc,
                  "Một tế bào GRU (Gated Recurrent Unit) tiêu chuẩn trong PyTorch bao gồm 3 cổng tính toán chính:\n"
                  "1. Cổng Reset (Reset Gate r): Quyết định lượng thông tin trạng thái ẩn quá khứ cần quên đi.\n"
                  "2. Cổng Cập nhật (Update Gate z): Quyết định lượng thông tin trạng thái ẩn mới cần đưa vào.\n"
                  "3. Trạng thái Bộ nhớ ứng viên (New Memory Candidate n): Tổng hợp thông tin đầu vào hiện tại và trạng thái quá khứ đã lọc.\n"
                  "Mỗi cổng đều có ma trận trọng số cho đầu vào (W_ih kích thước H x I), ma trận trọng số cho trạng thái ẩn (W_hh kích thước H x H), cùng 2 vector bias độc lập (b_ih và b_hh đều có độ dài H).\n"
                  "Do đó, đối với 1 hướng đơn của GRU, số lượng tham số là:\n"
                  "  Parameters (1 hướng) = 3 x (H x I) + 3 x (H x H) + 3 x H + 3 x H = 3HI + 3H² + 6H\n"
                  "Vì mạng là Bi-directional (chạy 2 chiều Forward & Backward) nên số lượng tham số nhân chính xác gấp 2 lần: 2 x [3HI + 3H² + 6H].",
                  bold_prefix="Giải thích bản chất công thức GRU (Tại sao có số 3 và số 6?): ")

    # BiGRU Layer 1
    add_layer_card(
        doc,
        "5. BiGRU TẦNG 1 (BiGRU Layer 1: In=256, Hidden=256, 2 chiều)",
        "Tầng 1 nhận đầu vào từ tầng FC Projection (Input size I = 256). Kích thước trạng thái ẩn Hidden size H = 256.\n"
        "- Chiều Forward (Tiến): Học ngữ cảnh từ đầu câu nói đến cuối câu nói.\n"
        "- Chiều Backward (Lùi): Học ngữ cảnh từ cuối câu nói ngược về đầu câu nói.\n"
        "Cả 2 chiều hoạt động độc lập và có bộ trọng số riêng biệt hoàn toàn.",
        "Với I = 256, H = 256:\n"
        "• Weight Input (W_ih): 3 x H x I\n"
        "• Weight Hidden (W_hh): 3 x H x H\n"
        "• Bias (b_ih + b_hh): 6 x H\n"
        "• Tổng tham số 1 hướng = 3HI + 3H² + 6H\n"
        "• Tổng tham số BiGRU Layer 1 = 2 x [3HI + 3H² + 6H]",
        "• Chiều Forward (1 hướng):\n"
        "  - W_ih: 3 x 256 x 256 = 196,608\n"
        "  - W_hh: 3 x 256 x 256 = 196,608\n"
        "  - Biases: 6 x 256 = 1,536\n"
        "  => Tổng 1 hướng = 196,608 + 196,608 + 1,536 = 394,752\n"
        "• Hai chiều (Forward + Backward):\n"
        "  => TỔNG CỘNG BiGRU LAYER 1 = 394,752 x 2 = 789,504 tham số\n"
        "  (Trong đó: 786,432 Weights và 3,072 Biases)",
        "Nắm bắt sự biến thiên ngữ âm ngắn hạn và liên kết cục bộ giữa các âm tiết tiếng Việt kề nhau.",
        "789,504 tham số"
    )

    # BiGRU Layer 2
    add_layer_card(
        doc,
        "6. BiGRU TẦNG 2 (BiGRU Layer 2: In=512, Hidden=256, 2 chiều)",
        "ĐÂY LÀ ĐIỂM HỘI ĐỒNG RẤT HAY HỎI: Tại sao Layer 2 lại nhận Input = 512 thay vì 256?\n"
        "- Layer 1 là mạng hai chiều (Bidirectional). Tại mỗi timestep t, Layer 1 xuất ra trạng thái ẩn h_forward (256 chiều) và h_backward (256 chiều).\n"
        "- PyTorch tự động ghép nối (concatenate) 2 vector này lại thành: h_out = [h_forward; h_backward] có kích thước: 256 + 256 = 512 chiều!\n"
        "- Do đó, Layer 2 bắt buộc phải nhận đầu vào có kích thước I = 512. Kích thước ẩn của Layer 2 vẫn giữ nguyên H = 256.",
        "Với I = 512, H = 256:\n"
        "• Weight Input (W_ih): 3 x H x I = 3 x 256 x 512\n"
        "• Weight Hidden (W_hh): 3 x H x H = 3 x 256 x 256\n"
        "• Bias (b_ih + b_hh): 6 x H = 6 x 256\n"
        "• Tổng tham số BiGRU Layer 2 = 2 x [3HI + 3H² + 6H]",
        "• Chiều Forward (1 hướng):\n"
        "  - W_ih: 3 x 256 x 512 = 393,216\n"
        "  - W_hh: 3 x 256 x 256 = 196,608\n"
        "  - Biases: 6 x 256 = 1,536\n"
        "  => Tổng 1 hướng = 393,216 + 196,608 + 1,536 = 591,360\n"
        "• Hai chiều (Forward + Backward):\n"
        "  => TỔNG CỘNG BiGRU LAYER 2 = 591,360 x 2 = 1,182,720 tham số\n"
        "  (Trong đó: 1,179,648 Weights và 3,072 Biases)",
        "Nắm bắt ngữ cảnh câu dài và trật tự từ vựng tiếng Việt, giúp phân biệt các từ đồng âm khác nghĩa dựa trên ngữ cảnh phát âm toàn câu.",
        "1,182,720 tham số"
    )

    add_paragraph(doc,
                  "789,504 (Layer 1) + 1,182,720 (Layer 2) = 1,972,224 tham số (chiếm tới 80.6% tổng trọng số của toàn bộ mô hình!).",
                  bold_prefix="📊 TỔNG CỘNG KHỐI BiGRU: ")

    # ==========================================
    # PHẦN IV: TẦNG ĐẦU RA PHÂN LỚP CTC
    # ==========================================
    add_heading_1(doc, "PHẦN IV: TẦNG CHIẾU ĐẦU RA CTC (CTC CLASSIFIER / LINEAR OUTPUT)")
    add_layer_card(
        doc,
        "7. TẦNG ĐẦU RA CTC (Linear(512, 105))",
        "Sau 2 tầng BiGRU, tại mỗi timestep t ta thu được một vector ngữ cảnh 512 chiều (ghép nối 256 forward + 256 backward của Layer 2).\n"
        "Tầng CTC Classifier là một phép biến đổi tuyến tính chiếu từ không gian ẩn 512 chiều sang 105 lớp tương ứng với 105 tokens trong từ điển tiếng Việt (26 chữ cái la-tinh, các nguyên âm có dấu á, à, ả..., chữ số, khoảng trắng ' ' và token đặc biệt <blank> ở vị trí id = 0).\n"
        "Tại mỗi timestep, tầng này sinh ra 105 logits thô. Sau đó hàm F.log_softmax chuyển thành xác suất logarit để tính CTC Loss.",
        "Với nn.Linear(in_features=512, out_features=105):\n"
        "• Số Weight = out_features x in_features = 105 x 512\n"
        "• Số Bias = out_features = 105\n"
        "• Tổng tham số = 105 x 512 + 105",
        "• Weight: 105 x 512 = 53,760 weights\n"
        "• Bias: 105 biases\n"
        "  => TỔNG CỘNG TẦNG CTC CLASSIFIER = 53,760 + 105 = 53,865 tham số\n"
        "• Kỹ thuật can thiệp đặc biệt trong đồ án: Nhóm đã gán sẵn bias[0] = -3.0 (Negative Blank Bias) ngay khi khởi tạo mô hình để chống sụp đổ Blank.",
        "Phát sinh phân phối xác suất trên toàn bộ bảng chữ cái tiếng Việt tại từng khung thời gian, làm đầu vào cho thuật toán giải mã CTC Greedy Search.",
        "53,865 tham số"
    )

    # ==========================================
    # PHẦN V: TỔNG KẾT & PHÂN TÍCH TỈ TRỌNG
    # ==========================================
    add_heading_1(doc, "PHẦN V: TỔNG KẾT TOÀN DIỆN & PHÂN TÍCH ĐỐI CHIẾU")

    add_paragraph(doc,
                  "Cộng tổng số tham số học được của tất cả 7 khối mạng:\n"
                  "  Total Trainable Parameters = 93,120 (CNN) + 327,936 (FC) + 1,972,224 (BiGRU) + 53,865 (CTC)\n"
                  "                             = 2,447,145 tham số (xấp xỉ 2.45 triệu tham số).",
                  bold_prefix="Phép tính tổng kết cuối cùng: ")

    add_paragraph(doc,
                  "Khối BiGRU chiếm tỉ trọng khổng lồ (80.6%), trong khi khối CNN chỉ chiếm 3.8% và tầng đầu ra CTC Classifier chỉ chiếm 2.2%. Điều này hoàn toàn phù hợp với lý thuyết ASR hiện đại: khâu trích xuất đặc trưng không gian (CNN) chỉ cần các kernel nhỏ 3x3 để bắt Formant, còn năng lực học máy chủ yếu phải dồn vào mạng hồi quy (BiGRU) để giải mã sự biến thiên phức tạp của âm điệu và ngữ nghĩa tiếng Việt.",
                  bold_prefix="Nhận xét về tỉ trọng kiến trúc: ")

    add_paragraph(doc,
                  "Khi lưu trữ file checkpoint vivos_ctc_model.pth trên ổ đĩa, file PyTorch lưu toàn bộ state_dict gồm 2,447,596 giá trị số thực float32 (dung lượng đúng 9.79 MB). Con số này chênh lệch đúng 451 giá trị so với 2,447,145 trainable params ở trên. 451 giá trị này chính là các thông số thống kê running_mean, running_var và num_batches_tracked của 3 tầng BatchNorm2D. Các biến này không cần tính đạo hàm (requires_grad = False) nhưng bắt buộc phải lưu lại để phục vụ quá trình suy luận (Inference / Eval mode).",
                  bold_prefix="Lý giải con số 2,447,596 trong file Checkpoint: ")

    # ==========================================
    # PHẦN VI: BỘ CÂU HỎI VẤN ĐÁP BẢO VỆ HỘI ĐỒNG
    # ==========================================
    add_heading_1(doc, "PHẦN VI: BỘ CÂU HỎI VẤN ĐÁP BẢO VỆ HỘI ĐỒNG VỀ WEIGHT & BIAS (ĐIỂM 10)")

    qa_list = [
        ("Câu 1: Tại sao số frame thời gian T của file âm thanh không được nhân vào số lượng Weight và Bias của mô hình?",
         "Dạ thưa Thầy/Cô, số lượng frame T là kích thước của dữ liệu đầu vào (data dimension) và liên tục thay đổi tùy theo độ dài câu nói (ví dụ nói 2 giây thì T ≈ 200, nói 5 giây thì T ≈ 500). Trong khi đó, Weight và Bias là các tham số cấu trúc nội tại của mạng nơ-ron.\n"
         "Mô hình CRNN hoạt động theo nguyên lý Chia sẻ trọng số (Weight Sharing across Time): một ma trận trọng số BiGRU duy nhất và một ma trận Linear Classifier duy nhất được dùng lặp đi lặp lại để tính toán cho tất cả các timestep từ 1 đến T. Vì vậy, số lượng tham số học được là một hằng số cố định (2,447,145 tham số) và hoàn toàn độc lập với thời lượng âm thanh T."),
        
        ("Câu 2: Tại sao Layer 2 của BiGRU lại có kích thước đầu vào I = 512 trong khi Layer 1 chỉ có I = 256?",
         "Dạ thưa Thầy/Cô, do Layer 1 được thiết lập là mạng hai chiều (bidirectional = True). Tại mỗi bước thời gian t, Layer 1 đồng thời xuất ra 2 vector trạng thái ẩn: vector theo chiều tiến h_forward (256 chiều) và vector theo chiều lùi h_backward (256 chiều).\n"
         "PyTorch thực hiện phép ghép nối (concatenation) 2 vector này lại thành vector đầu ra có độ dài: 256 + 256 = 512. Vector này chính là đầu vào của Layer 2, do đó Layer 2 bắt buộc phải có kích thước đầu vào I = 512."),

        ("Câu 3: Tại sao tầng BatchNorm2D lại có tham số học được, trong khi chuẩn hóa âm lượng (Normalization) hay chuẩn hóa CMVN ở khâu tiền xử lý lại không có tham số học được?",
         "Dạ thưa Thầy/Cô, các phép chuẩn hóa ở khâu tiền xử lý (như RMS Normalization hay CMVN) là các phép biến đổi xử lý tín hiệu số thống kê tĩnh: chúng chỉ tính trung bình (mean) và độ lệch chuẩn (std) của tín hiệu rồi trừ và chia thuần túy, không có bất kỳ trọng số nào được cập nhật bằng Gradient Descent.\n"
         "Ngược lại, tầng BatchNorm2D trong mạng nơ-ron sau khi đưa dữ liệu về phân phối chuẩn (mean=0, var=1) thì cung cấp thêm 2 tham số có thể học được là Scale (hệ số gamma) và Shift (hệ số beta). Hai tham số này được cập nhật liên tục qua lan truyền ngược để mạng tự do khôi phục lại dải động tối ưu nếu phân phối chuẩn vô tình làm mất tính phi tuyến của dữ liệu."),

        ("Câu 4: Khối mạng nào chiếm nhiều tham số nhất trong mô hình của nhóm và tại sao nhóm không dùng LSTM thay cho GRU?",
         "Dạ thưa Thầy/Cô, khối BiGRU chiếm tới 1.972.224 tham số (chiếm 80.6% toàn bộ mô hình). Nhóm lựa chọn GRU thay vì LSTM vì:\n"
         "1. Tế bào GRU chỉ có 3 cổng (Reset, Update, Candidate) nên số tham số ít hơn 25% so với LSTM (LSTM có 4 cổng: Input, Forget, Output, Cell candidate).\n"
         "2. Với ít tham số hơn, GRU tính toán nhanh hơn 20-30%, giúp giảm độ trễ suy luận (realtime latency đạt 0.07s/câu trên CPU) và hạn chế hiện tượng overfitting trên tập dữ liệu 15.4 giờ VIVOS, trong khi hiệu năng mô hình hóa ngữ âm tiếng Việt vẫn tương đương với LSTM."),

        ("Câu 5: Tại sao trong tầng CTC Classifier nhóm lại can thiệp khởi tạo sẵn bias[0] = -3.0?",
         "Dạ thưa Thầy/Cô, trong bài toán CTC Loss, token ở chỉ số 0 là token đặc biệt <blank>. Trong giai đoạn đầu huấn luyện, token Blank xuất hiện với tần suất áp đảo (chiếm hơn 90% số khung thời gian vì khoảng lặng và các đoạn kéo dài âm). Nếu để khởi tạo bias ngẫu nhiên quanh 0, mạng nơ-ron sẽ bị rơi vào 'Bẫy sụp đổ cực tiểu Blank' (Blank Collapse) – tức là mô hình học mẹo chỉ đoán toàn bộ token Blank để giảm loss nhanh nhất mà không chịu học các ký tự tiếng Việt.\n"
         "Bằng cách gán bias[0] = -3.0, xác suất ban đầu của token Blank qua hàm Softmax sẽ bị giảm mạnh xuống (e^(-3) ≈ 0.05), ép buộc các gradient của mạng phải tập trung cập nhật trọng số cho 104 ký tự chữ cái tiếng Việt ngay từ những epoch đầu tiên.")
    ]

    for q, a in qa_list:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(3)
        p_q.paragraph_format.keep_with_next = True
        r_q = p_q.add_run(q)
        r_q.font.name = "Times New Roman"
        r_q.font.size = Pt(11)
        r_q.font.bold = True
        r_q.font.color.rgb = RGBColor(0x99, 0x00, 0x00)

        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_after = Pt(8)
        p_a.paragraph_format.line_spacing = 1.15
        r_a = p_a.add_run(a)
        r_a.font.name = "Times New Roman"
        r_a.font.size = Pt(10.5)

    # Lưu đè trực tiếp vào C:\Users\Admin\Documents\ASR\bias+weight.docx
    target_path = r"C:\Users\Admin\Documents\ASR\bias+weight.docx"
    doc.save(target_path)
    print(f"[OK] Đã ghi đè thành công file trình bày đẹp tại: {target_path}")

    # Lưu thêm 1 bản vào thư mục docs của đồ án
    docs_path = r"C:\Users\Admin\PycharmProjects\speech-processing-tutorial\project_cuoiky\docs\bias+weight.docx"
    doc.save(docs_path)
    print(f"[OK] Đã lưu bản sao dự phòng tại: {docs_path}")

if __name__ == "__main__":
    generate_beautified_doc()
