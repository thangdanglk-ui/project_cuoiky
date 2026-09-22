import os
import sys
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def set_cell_background(cell, hex_color):
    """Đặt màu nền cho cell trong bảng"""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Đặt lề (padding) bên trong cell"""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_registration_docx(output_path):
    doc = docx.Document()

    # Thiết lập lề trang giấy chuẩn A4
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)

    # Đặt font chữ mặc định là Times New Roman
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0, 0, 0)

    # 1. TIÊU ĐỀ TÀI LIỆU
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(2)
    p_title.paragraph_format.space_before = Pt(0)
    run_title = p_title.add_run("PHIẾU ĐĂNG KÝ ĐỒ ÁN MÔN XỬ LÝ TIẾNG NÓI")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(16)
    run_title.font.bold = True

    p_group = doc.add_paragraph()
    p_group.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_group.paragraph_format.space_after = Pt(4)
    run_group = p_group.add_run("NHÓM 6")
    run_group.font.name = 'Times New Roman'
    run_group.font.size = Pt(14)
    run_group.font.bold = True

    p_topic = doc.add_paragraph()
    p_topic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_topic.paragraph_format.space_after = Pt(12)
    run_topic = p_topic.add_run("TÊN ĐỀ TÀI: XÂY DỰNG HỆ THỐNG NHẬN DẠNG TIẾNG NÓI TIẾNG VIỆT TỰ ĐỘNG (ASR) SỬ DỤNG MÔ HÌNH CRNN-CTC TRÊN TẬP DỮ LIỆU VIVOS")
    run_topic.font.name = 'Times New Roman'
    run_topic.font.size = Pt(11)
    run_topic.font.bold = True
    run_topic.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

    # 2. PHẦN 1: DANH SÁCH THÀNH VIÊN
    p_sec1 = doc.add_paragraph()
    p_sec1.paragraph_format.space_after = Pt(4)
    p_sec1.paragraph_format.space_before = Pt(6)
    run_sec1 = p_sec1.add_run("1. Danh sách thành viên")
    run_sec1.font.bold = True
    run_sec1.font.size = Pt(12)

    # Bảng thành viên
    table_tv = doc.add_table(rows=4, cols=3)
    table_tv.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_tv.style = 'Table Grid'

    headers_tv = ["STT TV", "MSSV", "Họ và tên"]
    col_widths_tv = [Inches(1.2), Inches(2.2), Inches(3.4)]

    # Header row
    hdr_cells = table_tv.rows[0].cells
    for i, title in enumerate(headers_tv):
        hdr_cells[i].text = title
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True
        hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(hdr_cells[i], "F2F2F2")

    # Data rows
    members_data = [
        ("TV1", "24110333", "Trần Đăng Thắng"),
        ("TV2", "24110395", "Nguyễn Minh Trí"),
        ("TV3", "24110176", "Nông Văn Cường")
    ]
    for row_idx, (stt, mssv, name) in enumerate(members_data, start=1):
        row_cells = table_tv.rows[row_idx].cells
        row_cells[0].text = stt
        row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[1].text = mssv
        row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[2].text = name
        row_cells[2].paragraphs[0].runs[0].font.bold = True

    # Set widths & padding
    for row in table_tv.rows:
        for i, w in enumerate(col_widths_tv):
            row.cells[i].width = w
            set_cell_margins(row.cells[i], top=100, bottom=100, left=150, right=150)

    # 3. PHẦN 2: ĐỀ XUẤT ĐỒ ÁN (ĐIỀN ĐẦY ĐỦ CHO ĐỒ ÁN HIỆN TẠI)
    p_sec2 = doc.add_paragraph()
    p_sec2.paragraph_format.space_after = Pt(4)
    p_sec2.paragraph_format.space_before = Pt(14)
    run_sec2 = p_sec2.add_run("2. Đề xuất đồ án")
    run_sec2.font.bold = True
    run_sec2.font.size = Pt(12)

    sec2_data = [
        ("Bài toán", 
         "Xây dựng hệ thống nhận dạng tiếng nói tự động (ASR), chuyển đổi audio tiếng Việt nguyên câu thành văn bản."),
        
        ("Mục tiêu", 
         "Xây dựng trọn vẹn pipeline nhận dạng tiếng nói tự động (ASR): thu âm qua Micro (laptop/tai phone) hoặc nạp file âm thanh (.wav), trích xuất đặc trưng Log-Mel Spectrogram, huấn luyện mô hình CRNN-CTC và giải mã văn bản tiếng Việt trên giao diện trực quan."),
        
        ("Input", 
         "File âm thanh (.wav) hoặc ghi âm trực tiếp qua Micro (Micro Laptop, Tai phone cắm giắc 3.5mm/Bluetooth), định dạng mono 16.000 Hz."),
        
        ("Output", 
         "Văn bản tiếng Việt có dấu tương ứng với nội dung âm thanh và độ trễ xử lý (latency)."),
        
        ("Phạm vi", 
         "Câu tiếng Việt liên tục có độ dài khoảng 2-10 giây, tập trung trên tập ngữ liệu VIVOS (15.4 giờ) và đàm thoại thực tế qua Micro."),
        
        ("Model", 
         "Mô hình CRNN-CTC (3 khối tích chập Conv2D trích xuất Formant + 2 tầng BiGRU học ngữ cảnh hai chiều + hàm mất mát CTC Loss)."),
        
        ("Cải tiến", 
         "Trích xuất 80 dải lọc Mel kết hợp chuẩn hóa CMVN; can thiệp bias âm (bias[0] = -3.0) chống sụp đổ Blank; giải mã CTC Greedy kết hợp lọc nhiễu âm đơn và ràng buộc từ điển VIVOS sửa lỗi chính tả."),
        
        ("Metric", 
         "CTC Loss (đạt 1.21), WER, CER, thời gian suy luận (latency ~0.07s/câu), kích thước mô hình (9.8 MB).")
    ]

    table_sec2 = doc.add_table(rows=len(sec2_data), cols=2)
    table_sec2.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_sec2.style = 'Table Grid'
    col_widths_sec2 = [Inches(1.5), Inches(5.3)]

    for row_idx, (field, content) in enumerate(sec2_data):
        row_cells = table_sec2.rows[row_idx].cells
        row_cells[0].text = field
        p0 = row_cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.runs[0].font.bold = True
        set_cell_background(row_cells[0], "F9F9F9")
        
        row_cells[1].text = content
        p1 = row_cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.line_spacing = 1.15
        p1.paragraph_format.space_after = Pt(2)

    for row in table_sec2.rows:
        for i, w in enumerate(col_widths_sec2):
            row.cells[i].width = w
            set_cell_margins(row.cells[i], top=100, bottom=100, left=150, right=150)

    # 4. PHẦN 3: TÍNH THỰC TIỄN CỦA ĐỒ ÁN (ĐIỀN ĐẦY ĐỦ CHO ĐỒ ÁN HIỆN TẠI)
    p_sec3 = doc.add_paragraph()
    p_sec3.paragraph_format.space_after = Pt(4)
    p_sec3.paragraph_format.space_before = Pt(14)
    run_sec3 = p_sec3.add_run("3. Tính thực tiễn của đồ án")
    run_sec3.font.bold = True
    run_sec3.font.size = Pt(12)

    sec3_data = [
        ("Đúng trọng tâm môn học", 
         "Nhận dạng tiếng nói tự động (ASR) là bài toán trọng tâm của Xử lý Tiếng nói, kết hợp toàn diện chuỗi kiến thức từ xử lý tín hiệu số DSP đến mô hình âm học mạng nơ-ron."),
        
        ("Đúng cơ sở lý thuyết", 
         "Bám sát Slide 2b bài giảng của Thầy Phù Khắc Anh: phân tích STFT, trích xuất 80 dải Log Mel-Spectrogram, chuẩn hóa CMVN và tối ưu gióng hàng chuỗi bằng CTC Loss."),
        
        ("Có mô hình kỹ thuật rõ ràng", 
         "Kiến trúc mô hình CRNN-CTC: 3 khối Conv2D trích xuất Formant, 2 tầng BiGRU học ngữ cảnh thời gian hai chiều và CTC Greedy Decoder giải mã văn bản tiếng Việt."),
        
        ("Có metric đánh giá phù hợp", 
         "Sử dụng CTC Loss theo dõi quá trình hội tụ (đạt mức 1.21), cùng các độ đo chuẩn quốc tế WER, CER và thời gian suy luận (latency ~0.07s/câu).")
    ]

    table_sec3 = doc.add_table(rows=len(sec3_data), cols=2)
    table_sec3.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_sec3.style = 'Table Grid'
    col_widths_sec3 = [Inches(1.8), Inches(5.0)]

    for row_idx, (criteria, content) in enumerate(sec3_data):
        row_cells = table_sec3.rows[row_idx].cells
        row_cells[0].text = criteria
        p0 = row_cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.runs[0].font.bold = True
        set_cell_background(row_cells[0], "F9F9F9")
        
        row_cells[1].text = content
        p1 = row_cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.line_spacing = 1.15
        p1.paragraph_format.space_after = Pt(2)

    for row in table_sec3.rows:
        for i, w in enumerate(col_widths_sec3):
            row.cells[i].width = w
            set_cell_margins(row.cells[i], top=100, bottom=100, left=150, right=150)

    # 5. PHẦN 4: XÂY DỰNG KẾ HOẠCH VÀ PHÂN CÔNG NHIỆM VỤ (CHUẨN MẪU RUBRIC)
    doc.add_page_break()

    p_sec4 = doc.add_paragraph()
    p_sec4.paragraph_format.space_after = Pt(4)
    p_sec4.paragraph_format.space_before = Pt(6)
    run_sec4 = p_sec4.add_run("4. Xây dựng kế hoạch và phân công nhiệm vụ")
    run_sec4.font.bold = True
    run_sec4.font.size = Pt(12)

    # 4.1. Bảng kế hoạch Giữa kỳ
    p_mid = doc.add_paragraph()
    p_mid.paragraph_format.space_after = Pt(4)
    run_mid = p_mid.add_run("- Bảng kế hoạch và phân công nhiệm vụ cho Báo cáo sơ bộ giữa kỳ:")
    run_mid.font.bold = True
    run_mid.font.size = Pt(11)

    midterm_rows = [
        # (STT, Nội dung, Phân công, Hạn, is_section_header)
        ("GIAI ĐOẠN 1: ĐỀ XUẤT ĐỒ ÁN", "", "", "", True),
        ("1", "Xác định rõ bài toán xử lý tiếng nói cần giải quyết, mục tiêu của hệ thống và kết quả đầu ra mong muốn", "TV1, TV2, TV3", "DONE", False),
        ("2", "Đồ án có tính thực tiễn, phù hợp với nội dung môn học và có khả năng ứng dụng các kỹ thuật xử lý tiếng nói để giải quyết bài toán", "TV1, TV2, TV3", "DONE", False),
        ("3", "Xây dựng kế hoạch thực hiện và phân công nhiệm vụ cụ thể cho từng thành viên trong nhóm", "TV1", "DONE", False),
        ("GIAI ĐOẠN 2: BÁO CÁO VÀ DEMO GIỮA KỲ", "", "", "", True),
        ("1. Tổng quan đồ án", "", "", "", True),
        ("1.1", "Trình bày rõ bài toán, mục tiêu, dữ liệu đầu vào và kết quả đầu ra của hệ thống", "TV1", "DONE", False),
        ("1.2", "Khảo sát tối thiểu ý tưởng 03 mô hình, thuật toán hoặc giải pháp liên quan đến đồ án", "TV2", "DONE", False),
        ("1.3", "Trình bày nguyên lý hoạt động hoặc kiến trúc tổng quát của các mô hình/giải pháp đã khảo sát", "TV3", "DONE", False),
        ("1.4", "So sánh ưu điểm, nhược điểm và khả năng áp dụng của các mô hình/giải pháp đối với đồ án", "TV2", "DONE", False),
        ("1.5", "Lựa chọn giải pháp đề xuất cho đồ án và giải thích lý do lựa chọn", "TV1", "DONE", False),
        ("2. Dữ liệu và đặc trưng tiếng nói", "", "", "", True),
        ("2.1", "Trình bày tổng quan về các dataset sử dụng cho đồ án hoặc phương án thu thập dữ liệu (nếu có)", "TV2", "DONE", False),
        ("2.2", "Mô tả cấu trúc dữ liệu: số lượng mẫu, nhãn, định dạng file, thời lượng, tần số lấy mẫu và các thuộc tính liên quan", "TV2", "DONE", False),
        ("2.3", "Trình bày quy trình chuẩn bị dữ liệu: (cắt đoạn, chuẩn hóa âm lượng, khử nhiễu, gán nhãn hoặc chia dữ liệu, v.v...)", "TV3", "DONE", False),
        ("2.4", "Trích xuất các đặc trưng sử dụng trong đồ án như (waveform, spectrogram, MFCC, LPC, pitch, energy hoặc ZCR, vv...)", "TV1", "DONE", False),
        ("2.5", "Minh họa và nhận xét dữ liệu/đặc trưng bằng ví dụ cụ thể, hình ảnh hoặc biểu đồ", "TV1", "DONE", False),
        ("3. Giải pháp cài đặt ban đầu", "", "", "", True),
        ("3.1", "Trình bày kiến trúc hoặc quy trình hoạt động của giải pháp đề xuất", "TV1", "DONE", False),
        ("3.2", "Cài đặt được mô hình, thuật toán hoặc phương pháp xử lý tiếng nói đã lựa chọn", "TV3", "DONE", False),
        ("3.3", "Có kết quả thực nghiệm ban đầu hoặc kết quả huấn luyện ban đầu để minh chứng tính khả thi của giải pháp", "TV2", "DONE", False),
        ("3.4", "Demo được các chức năng cơ bản của hệ thống ở mức giữa kỳ", "TV3", "DONE", False)
    ]

    table_mid = doc.add_table(rows=len(midterm_rows) + 1, cols=4)
    table_mid.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_mid.style = 'Table Grid'
    col_widths_plan = [Inches(0.8), Inches(4.2), Inches(1.1), Inches(0.7)]

    # Header
    mid_hdr = table_mid.rows[0].cells
    hdr_titles = ["STT", "NỘI DUNG CÔNG VIỆC / ĐÁNH GIÁ", "PHÂN CÔNG", "HẠN"]
    for i, t in enumerate(hdr_titles):
        mid_hdr[i].text = t
        mid_hdr[i].paragraphs[0].runs[0].font.bold = True
        mid_hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(mid_hdr[i], "D9E1F2")

    for r_idx, (stt, content, assign, deadline, is_sec) in enumerate(midterm_rows, start=1):
        cells = table_mid.rows[r_idx].cells
        if is_sec:
            # Dòng tiêu đề mục lớn
            cells[0].text = stt
            cells[1].text = content
            cells[2].text = assign
            cells[3].text = deadline
            for c in cells:
                set_cell_background(c, "EAECEE")
                if len(c.paragraphs[0].runs) > 0:
                    c.paragraphs[0].runs[0].font.bold = True
        else:
            cells[0].text = stt
            cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cells[1].text = content
            cells[2].text = assign
            cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cells[3].text = deadline
            cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    for row in table_mid.rows:
        for i, w in enumerate(col_widths_plan):
            row.cells[i].width = w
            set_cell_margins(row.cells[i], top=80, bottom=80, left=100, right=100)

    # 4.2. Bảng kế hoạch Cuối kỳ
    p_final = doc.add_paragraph()
    p_final.paragraph_format.space_before = Pt(14)
    p_final.paragraph_format.space_after = Pt(4)
    run_final = p_final.add_run("- Bảng kế hoạch và phân công nhiệm vụ cho Báo cáo toàn diện cuối kỳ:")
    run_final.font.bold = True
    run_final.font.size = Pt(11)

    final_rows = [
        ("1. GIẢI PHÁP HOÀN CHỈNH", "", "", "", True),
        ("1.1", "Xây dựng được hệ thống xử lý tiếng nói hoàn chỉnh đúng theo mục tiêu đồ án", "TV2", "29/09/2026", False),
        ("1.2", "Cài đặt thành công mô hình, thuật toán hoặc phương pháp xử lý tiếng nói đã lựa chọn", "TV3", "29/09/2026", False),
        ("1.3", "Đề xuất và triển khai cải tiến cho mô hình, thuật toán, module xử lý đặc trưng hoặc kiến trúc hệ thống", "TV1", "29/09/2026", False),
        ("1.4", "Phân tích được ảnh hưởng của cải tiến đối với hệ thống thông qua kết quả thực nghiệm", "TV1", "29/09/2026", False),
        ("1.5", "Xây dựng giao diện hoặc chương trình minh họa giúp người dùng nhập dữ liệu âm thanh, chạy hệ thống và quan sát kết quả", "TV2", "29/09/2026", False),
        ("1.6", "Tối ưu hóa mã nguồn, đóng gói pipeline xử lý âm thanh thời gian thực và kiểm thử tính ổn định của hệ thống", "TV3", "29/09/2026", False),
        ("2. THỰC NGHIỆM VÀ ĐÁNH GIÁ", "", "", "", True),
        ("2.1", "Xây dựng được bộ dữ liệu, tập kiểm thử hoặc kịch bản đánh giá phù hợp với bài toán xử lý tiếng nói", "TV2", "29/09/2026", False),
        ("2.2", "Thực hiện huấn luyện, kiểm thử hoặc chạy thực nghiệm và thu thập đầy đủ kết quả đánh giá", "TV3", "29/09/2026", False),
        ("2.3", "Phân tích kết quả dựa trên tiêu chí phù hợp (accuracy, precision, recall, F1-score, WER, CER, loss, confusion matrix hoặc thời gian xử lý, vv...)", "TV2", "29/09/2026", False),
        ("2.4", "So sánh với mô hình, thuật toán hoặc giải pháp tham chiếu để làm rõ hiệu quả của giải pháp", "TV1", "29/09/2026", False),
        ("2.5", "Thực hiện đánh giá mở rộng trên dữ liệu khác, giọng nói khác, môi trường nhiều khác hoặc tình huống kiểm thử khác", "TV1", "29/09/2026", False),
        ("2.6", "Đo đạc và phân tích chi tiết độ trễ xử lý (latency), tốc độ suy luận (Realtime Factor) và mức độ sử dụng tài nguyên hệ thống", "TV3", "29/09/2026", False),
        ("3. FILE BÁO CÁO ĐỒ ÁN", "", "", "", True),
        ("3.1", "Báo cáo đầy đủ các nội dung theo yêu cầu: giới thiệu, cơ sở lý thuyết, dữ liệu, giải pháp đề xuất, thực nghiệm, kết luận và tài liệu tham khảo", "TV1", "29/09/2026", False),
        ("3.2", "Nội dung báo cáo thể hiện rõ quá trình khảo sát, xây dựng, cài đặt và đánh giá giải pháp xử lý tiếng nói", "TV3", "29/09/2026", False),
        ("3.3", "Hình ảnh, bảng biểu, sơ đồ hệ thống, thuật toán và kết quả thực nghiệm được trình bày đầy đủ, khoa học và có chú thích rõ ràng", "TV2", "29/09/2026", False),
        ("3.4", "Trích dẫn và tài liệu tham khảo đầy đủ, đúng quy cách và phù hợp với nội dung đồ án", "TV2", "29/09/2026", False),
        ("3.5", "Hình thức trình bày báo cáo đúng quy định, bố cục rõ ràng, hạn chế lỗi chính tả và đảm bảo tính học thuật", "TV3", "29/09/2026", False),
        ("3.6", "Rà soát, hoàn thiện toàn bộ nội dung báo cáo, biên soạn tài liệu tóm tắt và xây dựng slide thuyết trình bảo vệ đồ án", "TV1", "29/09/2026", False)
    ]

    table_final = doc.add_table(rows=len(final_rows) + 1, cols=4)
    table_final.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_final.style = 'Table Grid'

    fin_hdr = table_final.rows[0].cells
    for i, t in enumerate(hdr_titles):
        fin_hdr[i].text = t
        fin_hdr[i].paragraphs[0].runs[0].font.bold = True
        fin_hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(fin_hdr[i], "FCE4D6")

    for r_idx, (stt, content, assign, deadline, is_sec) in enumerate(final_rows, start=1):
        cells = table_final.rows[r_idx].cells
        if is_sec:
            cells[0].text = stt
            cells[1].text = content
            cells[2].text = assign
            cells[3].text = deadline
            for c in cells:
                set_cell_background(c, "EAECEE")
                if len(c.paragraphs[0].runs) > 0:
                    c.paragraphs[0].runs[0].font.bold = True
        else:
            cells[0].text = stt
            cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cells[1].text = content
            cells[2].text = assign
            cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cells[3].text = deadline
            cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    for row in table_final.rows:
        for i, w in enumerate(col_widths_plan):
            row.cells[i].width = w
            set_cell_margins(row.cells[i], top=80, bottom=80, left=100, right=100)

    # Lưu file
    doc.save(output_path)
    print(f"[OK] Đã tạo thành công file Word tại: {output_path}")

if __name__ == "__main__":
    # 1. Thư mục Documents\ASR
    asr_dir = r"C:\Users\Admin\Documents\ASR"
    os.makedirs(asr_dir, exist_ok=True)
    asr_file = os.path.join(asr_dir, "NHÓM 6 - PHIẾU ĐĂNG KÝ ĐỒ ÁN MÔN XỬ LÝ TIẾNG NÓI.docx")
    create_registration_docx(asr_file)

    # 2. Thư mục Downloads
    out_dir = r"C:\Users\Admin\Downloads"
    os.makedirs(out_dir, exist_ok=True)
    out_file1 = os.path.join(out_dir, "NHÓM 6 - PHIẾU ĐĂNG KÝ ĐỒ ÁN MÔN XỬ LÝ TIẾNG NÓI.docx")
    out_file2 = os.path.join(out_dir, "PHIEU_DANG_KY_DO_AN_MON_XU_LY_TIENG_NOI.docx")
    create_registration_docx(out_file1)
    create_registration_docx(out_file2)

    # 3. Thư mục docs của project
    project_docs = r"C:\Users\Admin\PycharmProjects\speech-processing-tutorial\project_cuoiky\docs"
    os.makedirs(project_docs, exist_ok=True)
    p_file1 = os.path.join(project_docs, "NHÓM 6 - PHIẾU ĐĂNG KÝ ĐỒ ÁN MÔN XỬ LÝ TIẾNG NÓI.docx")
    p_file2 = os.path.join(project_docs, "PHIEU_DANG_KY_DO_AN_MON_XU_LY_TIENG_NOI.docx")
    create_registration_docx(p_file1)
    create_registration_docx(p_file2)
