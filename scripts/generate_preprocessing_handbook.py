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

def add_header(doc, title, subtitle):
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
    p_sub.paragraph_format.space_after = Pt(14)
    run_sub = p_sub.add_run(subtitle)
    run_sub.font.name = "Times New Roman"
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
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
    run.font.size = Pt(12.5)
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

def add_concept_box(doc, term_title, what_is_it, math_physics, why_need_it, code_mapping, defense_qa):
    """
    Tạo một bảng chuẩn hóa 5 thành phần cho từng cụm thuật ngữ học thuật
    """
    table = doc.add_table(rows=6, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    col_widths = [Inches(1.8), Inches(5.0)]

    r0 = table.rows[0]
    r0.cells[0].merge(r0.cells[1])
    r0.cells[0].text = term_title
    r0.cells[0].paragraphs[0].runs[0].font.name = "Times New Roman"
    r0.cells[0].paragraphs[0].runs[0].font.size = Pt(12)
    r0.cells[0].paragraphs[0].runs[0].font.bold = True
    r0.cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    set_cell_background(r0.cells[0], "1B365D")

    sections = [
        ("1. Bản chất khái niệm\n(What is it?)", what_is_it, "F2F4F7"),
        ("2. Cơ sở vật lý & Toán học\n(Math & Physics)", math_physics, "FFFFFF"),
        ("3. Vai trò trong ASR\n(Why need it?)", why_need_it, "F2F4F7"),
        ("4. Dẫn chứng mã nguồn đồ án\n(Code Mapping)", code_mapping, "E8F4F8"),
        ("5. Vấn đáp bảo vệ (Hội đồng)\n(Defense Q&A)", defense_qa, "FFF2E6")
    ]

    for idx, (label, content, bg_color) in enumerate(sections, start=1):
        row = table.rows[idx]
        row.cells[0].text = label
        p_lbl = row.cells[0].paragraphs[0]
        p_lbl.runs[0].font.name = "Times New Roman"
        p_lbl.runs[0].font.size = Pt(10.5)
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
            set_cell_margins(row.cells[i], top=80, bottom=80, left=120, right=120)

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_after = Pt(8)

def build_preprocessing_handbook():
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    add_header(doc, 
               "CẨM NANG BẢO VỆ ĐỒ ÁN: GIAI ĐOẠN 1 & 2\nTỔNG QUAN HỆ THỐNG VÀ TIỀN XỬ LÝ ĐẶC TRƯNG TIẾNG NÓI",
               "Bộ môn: Xử lý Tiếng nói | GVHD: TS. Phù Khắc Anh | Nhóm thực hiện: Nhóm 6 (TV1 - Trưởng nhóm phụ trách)")

    # Lời mở đầu
    add_paragraph(doc, 
                  "Tài liệu này được biên soạn chuyên biệt phục vụ cho buổi bảo vệ đồ án của Thành viên 1 (Trưởng nhóm). Trọng tâm tài liệu bao quát toàn diện Giai đoạn 1 (Đề xuất & Khảo sát kiến trúc) và đi sâu tuyệt đối vào Giai đoạn 2 (Tiền xử lý tín hiệu âm thanh và Trích xuất đặc trưng tiếng nói - Audio Preprocessing & Feature Extraction). Mọi khái niệm đều được phân tích theo 5 trụ cột: Bản chất - Toán học/Vật lý - Vai trò ASR - Dẫn chứng mã nguồn - Mẹo trả lời phản biện Hội đồng đạt điểm tuyệt đối.",
                  bold_prefix="MỤC ĐÍCH & Ý NGHĨA: ")

    # ==========================================
    # PHẦN I: TỔNG QUAN ĐỒ ÁN & LỰA CHỌN MÔ HÌNH (GIAI ĐOẠN 1)
    # ==========================================
    add_heading_1(doc, "PHẦN I: TỔNG QUAN BÀI TOÁN & LỰA CHỌN GIẢI PHÁP KỸ THUẬT (GIAI ĐOẠN 1)")
    
    add_paragraph(doc,
                  "Trong Giai đoạn 1, nhóm đã xác định bài toán, khảo sát các mô hình hiện đại và đưa ra lựa chọn giải pháp tối ưu cho đồ án. Dưới đây là 3 nội dung trọng tâm mà Hội đồng thường xuyên chất vấn Trưởng nhóm về tính khoa học và tính khả thi của đề tài.")

    # Mục 1: Khảo sát 3 giải pháp
    add_heading_2(doc, "1. Khảo sát và Phân tích 03 Giải pháp Kiến trúc Nhận dạng Tiếng nói (ASR)")
    add_paragraph(doc, "Hội đồng rất quan tâm lý do tại sao nhóm không chọn mô hình cổ điển HMM hoặc mô hình siêu lớn như Whisper, mà lại chọn kiến trúc CRNN-CTC. Dưới đây là phân tích đối sánh chi tiết:")

    table_comp = doc.add_table(rows=4, cols=4)
    table_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_comp.style = 'Table Grid'
    headers = ["Tiêu chí so sánh", "1. HMM - GMM (Cổ điển)", "2. CRNN - CTC (Nhóm đề xuất)", "3. Transformer / Conformer"]
    for i, h in enumerate(headers):
        cell = table_comp.rows[0].cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].font.name = "Times New Roman"
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(10)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(cell, "1B365D")

    data_comp = [
        ("Bản chất kiến trúc", 
         "Mô hình chuỗi Markov ẩn (HMM) kết hợp hỗn hợp Gauss (GMM). Phân rã thành: Acoustic Model, Pronunciation Dictionary, Language Model riêng biệt.",
         "Mạng nơ-ron tích hợp End-to-End: 3 khối Conv2D trích xuất Formant + 2 tầng BiGRU học ngữ cảnh + Hàm mất mát CTC Loss gióng hàng tự động.",
         "Kiến trúc Attention toàn phần (Self-Attention + Convolutions). Điển hình: Whisper, Conformer, wav2vec 2.0."),
        ("Đặc trưng đầu vào & Căn chỉnh (Alignment)",
         "Bắt buộc dùng MFCC (13-39 chiều). Đòi hỏi quy trình căn chỉnh thời gian bắt buộc (Forced Alignment) ở cấp độ âm vị (Phoneme/Triphone) cực kỳ tốn công.",
         "Dùng trực tiếp 80 dải Log-Mel Spectrogram. Không cần căn chỉnh nhãn trước (Alignment-free), CTC tự học gióng hàng thông qua ma trận xác suất.",
         "Dùng 80 dải Mel Spectrogram hoặc raw waveform (wav2vec). Tự động học biểu diễn không gian thông qua cơ chế Attention."),
        ("Tài nguyên & Độ trễ (Latency) trong đồ án",
         "Huấn luyện phức tạp qua nhiều giai đoạn (flat start, monophone, triphone). Khó tùy biến giao diện trực quan và khó sửa lỗi chính tả theo từ điển tiếng Việt.",
         "Kích thước siêu gọn nhẹ (~9.8 MB). Thời gian suy luận cực nhanh (~0.07 giây/câu). Chạy mượt mà thời gian thực trên CPU máy tính cá nhân không cần GPU rời.",
         "Kích thước rất lớn (>150 MB đến 3 GB). Đòi hỏi GPU chuyên dụng VRAM lớn. Độ trễ cao, khó đáp ứng bài toán demo đồ án tương tác trực tiếp qua Micro.")
    ]

    for row_idx, row_data in enumerate(data_comp, start=1):
        for col_idx, text in enumerate(row_data):
            cell = table_comp.rows[row_idx].cells[col_idx]
            cell.text = text
            p = cell.paragraphs[0]
            p.runs[0].font.name = "Times New Roman"
            p.runs[0].font.size = Pt(9.5)
            p.paragraph_format.line_spacing = 1.15
            if col_idx == 0:
                p.runs[0].font.bold = True
                set_cell_background(cell, "D9E1F2")
            elif col_idx == 2:
                set_cell_background(cell, "E8F4F8")
            else:
                set_cell_background(cell, "FFFFFF")

    for row in table_comp.rows:
        for i, w in enumerate([Inches(1.5), Inches(1.8), Inches(1.9), Inches(1.8)]):
            row.cells[i].width = w
            set_cell_margins(row.cells[i], top=60, bottom=60, left=80, right=80)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(10)

    # ==========================================
    # PHẦN II: NỀN TẢNG ÂM THANH SỐ (DIGITAL AUDIO BASICS)
    # ==========================================
    add_heading_1(doc, "PHẦN II: NỀN TẢNG ÂM THANH SỐ & TÍN HIỆU TIẾNG NÓI")

    add_concept_box(
        doc,
        "CHỦ ĐỀ 1: SÓNG ÂM (ACOUSTIC WAVE) & QUÁ TRÌNH SỐ HÓA ÂM THANH (ADC)",
        "Sóng âm trong tự nhiên là sóng dọc cơ học, lan truyền dưới dạng sự dao động áp suất không khí liên tục theo thời gian. Khi người nói cất tiếng, luồng hơi từ phổi làm màng rung của Micro dao động, biến cơ năng thành tín hiệu điện áp tương tự (Analog Continuous Signal: s(t)). Quá trình số hóa âm thanh (Analog-to-Digital Conversion - ADC) chuyển điện áp liên tục này thành chuỗi các con số rời rạc mà máy tính có thể xử lý: x[n] = s(n*Ts), với Ts là chu kỳ lấy mẫu.",
        "Toán học: Quá trình số hóa bao gồm 2 bước độc lập:\n"
        "1. Lấy mẫu theo thời gian (Sampling): t -> n * Ts = n / Fs (với Fs là tần số lấy mẫu).\n"
        "2. Lượng tử hóa biên độ (Quantization): Biên độ liên tục s(t) được ánh xạ vào tập hữu hạn các mức số nguyên (thường là 16-bit nguyên có dấu: [-32768, 32767]).\n"
        "Tỉ số tín hiệu trên nhiễu lượng tử (SQNR): SQNR ≈ 6.02 * Q + 1.76 (dB). Với Q = 16 bit, dải động đạt xấp xỉ 98 dB, hoàn toàn vượt xa dải động của giọng nói con người (khoảng 40-60 dB).",
        "Hệ thống ASR không thể đọc trực tiếp điện áp từ màng rung micro. ASR bắt buộc phải nhận đầu vào là mảng số thực (Float32 Tensor 1D) chuẩn hóa về khoảng [-1.0, 1.0]. Nếu bước số hóa bị méo, cắt đỉnh (clipping do âm lượng quá lớn) hoặc dải động quá hẹp, tín hiệu đặc trưng trích xuất sau đó sẽ bị suy biến hoàn toàn.",
        "File: src/data/dataset.py và src/inference/realtime.py\n"
        "Code nạp âm thanh: waveform, sr = torchaudio.load(wav_path)\n"
        "Code ghi âm qua mic: audio_chunk = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0\n"
        "Nhận xét: Source code đồ án chia biên độ cho 32768.0 để ánh xạ int16 về khoảng [-1.0, 1.0].",
        "Hỏi: Tại sao trong code đồ án lại chia cho 32768.0 mà không giữ nguyên số nguyên int16?\n"
        "Đáp: Số nguyên 16-bit có dải giá trị từ -32768 đến +32767. Mạng nơ-ron sâu (Neural Networks) với các hàm kích hoạt và bộ lọc tích chập (Conv2D) rất nhạy cảm với thang đo giá trị. Nếu để biên độ hàng chục nghìn, gradient sẽ bị bùng nổ (exploding gradient). Việc chia 32768.0 chuẩn hóa âm thanh về khoảng [-1.0, 1.0] giúp giải thuật lan truyền ngược (Backpropagation) hội tụ ổn định và các phép tính STFT có độ chính xác số học cao nhất."
    )

    add_concept_box(
        doc,
        "CHỦ ĐỀ 2: TẦN SỐ LẤY MẪU (SAMPLING RATE - 16.000 HZ), ĐỊNH LÝ NYQUIST & CHỒNG PHỔ (ALIASING)",
        "Tần số lấy mẫu (Sampling Rate - Fs) là số lượng mẫu âm thanh được đo và ghi lại trong 1 giây (đơn vị Hertz - Hz). Định lý lấy mẫu Nyquist-Shannon khẳng định: để khôi phục hoàn hảo một tín hiệu liên tục mà không bị biến dạng, tần số lấy mẫu Fs phải lớn hơn ít nhất gấp đôi tần số cực đại có trong tín hiệu (Fs >= 2 * f_max). Nửa tần số lấy mẫu (Fs / 2) được gọi là Tần số Nyquist (Nyquist Frequency).",
        "Toán học: Nếu tín hiệu chứa thành phần tần số f > Fs/2, thành phần này sẽ bị 'gập gương' (fold back) qua tần số Nyquist và biến thành một tần số giả mạo thấp hơn nằm trong dải phân tích: f_alias = |Fs - f|. Đây là hiện tượng Chồng phổ (Aliasing).\n"
        "Trong đồ án: Fs = 16.000 Hz => Tần số Nyquist f_max = 8.000 Hz.\n"
        "Cơ sở vật lý: Tai người nghe được từ 20 Hz - 20.000 Hz, nhưng đối với giọng nói tiếng người:\n"
        "- Tần số cơ bản F0: 85 - 255 Hz.\n"
        "- Các Formant nhận diện nguyên âm quan trọng nhất (F1, F2, F3): nằm dưới 3.500 Hz.\n"
        "- Phụ âm xát có tần số cao nhất (/s/, /x/): tập trung dưới 7.500 Hz.\n"
        "Do đó, dải tần 0 - 8.000 Hz là hoàn hảo để nhận diện chính xác 100% ngữ âm tiếng Việt.",
        "Tiết kiệm tối đa chi phí tính toán. Nếu dùng chuẩn Audio CD (44.100 Hz) hoặc Studio (48.000 Hz), số lượng mẫu tăng gấp gần 3 lần, làm kích thước ma trận STFT phình to gấp 3, tốc độ trích xuất đặc trưng và tính toán qua mạng CRNN chậm đi gấp 3 lần mà không làm tăng độ chính xác nhận dạng ký tự tiếng Việt.",
        "File: src/config/config.py và src/features/extraction.py\n"
        "Code cấu hình: SAMPLE_RATE = 16000\n"
        "Kiểm tra và Resample: if sr != 16000: waveform = torchaudio.transforms.Resample(sr, 16000)(waveform)",
        "Hỏi: Tại sao ngành ASR thế giới và đồ án của bạn đều thống nhất chọn Fs = 16.000 Hz thay vì 44.100 Hz như các file nhạc MP3 thông thường?\n"
        "Đáp: Âm nhạc cần dải tần lên tới 20.000 Hz để tái hiện tiếng chũm chọe, nhạc cụ gõ tinh vi nên cần Fs = 44.1 kHz. Tuy nhiên, tiếng nói con người có băng thông hữu ích chỉ nằm trong khoảng 0 đến 7.500 Hz. Lựa chọn Fs = 16.000 Hz đảm bảo tần số Nyquist là 8.000 Hz, bao trọn toàn bộ các Formant F1, F2, F3 và phụ âm tiếng Việt. Quan trọng nhất, 16 kHz giúp giảm 64% khối lượng dữ liệu đầu vào so với 44.1 kHz, giúp hệ thống suy luận thời gian thực (realtime latency chỉ 0.07 giây) trên máy tính người dùng."
    )

    add_concept_box(
        doc,
        "CHỦ ĐỀ 3: ĐỘ SÂU BIT (BIT DEPTH - 16-BIT PCM) & ĐƠN ÂM (MONO) VS ĐA ÂM (STEREO)",
        "Độ sâu bit (Bit Depth) là số lượng bit nhị phân được máy tính sử dụng để mã hóa biên độ của mỗi mẫu âm thanh. Chuẩn 16-bit PCM (Pulse Code Modulation) phân chia trục biên độ thành 2^16 = 65.536 mức rời rạc. Kênh âm thanh (Channel): Mono là âm thanh 1 kênh (tất cả tín hiệu thu gom vào 1 dòng dữ liệu), trong khi Stereo là âm thanh 2 kênh độc lập (kênh trái - Left và kênh phải - Right) nhằm mô phỏng hiệu ứng không gian 3D cho tai nghe.",
        "Toán học: \n"
        "1. Dải động lý thuyết: Dynamic Range (dB) ≈ 20 * log10(2^Q) ≈ 6.02 * Q (dB). Với Q = 16 bit: Dynamic Range = 96.3 dB.\n"
        "2. Công thức chuyển đổi Stereo sang Mono trong code:\n"
        "x_mono[n] = 0.5 * (x_left[n] + x_right[n]), hoặc đơn giản là lấy kênh 1 (x_mono = x[0, :]).",
        "Tiếng nói của một người phát ra từ một nguồn điểm âm học duy nhất (vocal tract). ASR là bài toán giải mã chuỗi âm thanh thành chuỗi ký tự, hoàn toàn không cần thông tin vị trí không gian trái/phải của Stereo. Giữ 2 kênh chỉ làm tăng gấp đôi bộ nhớ GPU và gây sai lệch độ trễ pha (phase shift) giữa hai mic.",
        "File: src/data/dataset.py\n"
        "Code chuyển mono: if waveform.shape[0] > 1: waveform = torch.mean(waveform, dim=0, keepdim=True)\n"
        "Nhận xét: Đồ án tính trung bình cộng giữa 2 kênh để bảo toàn trọn vẹn năng lượng của cả 2 mic nếu người dùng cắm tai nghe có mic kép.",
        "Hỏi: Nếu người dùng cắm micro Stereo hoặc tai nghe Bluetooth có 2 kênh, điều gì xảy ra nếu bạn không chuyển về Mono?\n"
        "Đáp: Nếu giữ nguyên Stereo, tensor âm thanh sẽ có kích thước shape là [2, N] thay vì [1, N]. Khi đưa qua module trích xuất đặc trưng Log-Mel Spectrogram, kích thước ma trận sẽ bị sai lệch shape so với cấu hình mạng Conv2D (vốn nhận channel = 1), gây lỗi Crash chương trình ngay lập tức. Do đó, đồ án đã lập trình cơ chế phòng thủ: luôn kiểm tra `shape[0] > 1` và lấy `torch.mean` để đưa về chuẩn Mono 1 kênh duy nhất trước khi xử lý."
    )

    # ==========================================
    # PHẦN III: QUY TRÌNH TIỀN XỬ LÝ DỮ LIỆU ÂM THANH THÔ
    # ==========================================
    add_heading_1(doc, "PHẦN III: QUY TRÌNH TIỀN XỬ LÝ TÍN HIỆU ÂM THANH THÔ (DATA PREPROCESSING PIPELINE)")

    add_concept_box(
        doc,
        "CHỦ ĐỀ 4: TÁI LẤY MẪU (RESAMPLING) & BỘ LỌC ĐA PHA (POLYPHASE FILTERING)",
        "Tái lấy mẫu (Resampling) là kỹ thuật biến đổi một chuỗi tín hiệu số từ tần số lấy mẫu ban đầu F_orig (ví dụ: 44.100 Hz từ điện thoại hoặc 48.000 Hz từ mic thu âm máy tính) sang tần số lấy mẫu chuẩn của hệ thống F_target (16.000 Hz). Đây không chỉ là việc bỏ bớt mẫu (decimation) đơn thuần mà là một quy trình toán học nghiêm ngặt gồm: Nội suy (Interpolation) -> Lọc thông thấp chống chồng phổ (Anti-Aliasing Filter) -> Hạ mẫu (Downsampling).",
        "Toán học: \n"
        "Tỉ số lấy mẫu: L / M = F_target / F_orig. Ví dụ từ 48 kHz về 16 kHz: L/M = 1/3.\n"
        "Nếu hạ mẫu 3 lần bằng cách cứ 3 mẫu bỏ 2 mẫu mà không lọc trước, các thành phần tần số từ 8 kHz đến 24 kHz trong tín hiệu 48 kHz sẽ bị dội ngược (aliasing) vào dải 0 - 8 kHz, tạo ra tiếng rít và méo tiếng kim loại phá hủy đặc trưng Log-Mel.\n"
        "Thuật toán sinc interpolation (Kaiser windowed sinc filter) được sử dụng để nội suy chính xác giá trị biên độ tại các mốc thời gian mới.",
        "Trong thực tế sử dụng, người dùng có thể tải lên file .wav ghi từ điện thoại iPhone (44.1 kHz), micro phòng thu (48 kHz), hoặc ghi âm trực tiếp qua SoundCard. Module Resampling đảm bảo tính bất biến (Invariance) của toàn bộ pipeline trích xuất đặc trưng.",
        "File: src/inference/realtime.py và src/data/dataset.py\n"
        "Code: resampler = torchaudio.transforms.Resample(orig_freq=orig_sr, new_freq=16000)\n"
        "waveform = resampler(waveform)",
        "Hỏi: Tại sao hạ mẫu (Downsampling) bắt buộc phải đi kèm với một bộ lọc thông thấp (Low-pass filter)?\n"
        "Đáp: Theo định lý Nyquist, ở tần số mới 16 kHz, hệ thống chỉ có khả năng biểu diễn các tần số tối đa là 8 kHz. Nếu file gốc là 48 kHz, nó chứa dải tần lên tới 24 kHz. Nếu hạ mẫu trực tiếp mà không dùng bộ lọc thông thấp cắt bỏ trước toàn bộ các tần số trên 8 kHz, thì các dải tần cao đó sẽ bị gập ngược (aliasing) vào dải 0 - 8 kHz, làm biến dạng hoàn toàn phổ Formant của nguyên âm, dẫn tới nhận diện sai từ."
    )

    add_concept_box(
        doc,
        "CHỦ ĐỀ 5: CHUẨN HÓA BIÊN ĐỘ (PEAK & RMS NORMALIZATION)",
        "Chuẩn hóa biên độ (Amplitude Normalization) là kỹ thuật điều chỉnh độ lớn âm lượng của toàn bộ tín hiệu âm thanh về một thang đo chuẩn đồng nhất. Trong thực tế, có người nói rất to sát mic, có người nói thì thầm ở xa mic, hoặc các loại micro có độ nhạy (sensitivity/gain) khác nhau một trời một vực. Chuẩn hóa biên độ giúp triệt tiêu sự chênh lệch này.",
        "Toán học:\n"
        "1. Chuẩn hóa theo đỉnh (Peak Normalization): \n"
        "x_norm[n] = x[n] / (max(|x|) + eps)\n"
        "Biên độ sau chuẩn hóa nằm chính xác trong khoảng [-1.0, 1.0].\n"
        "2. Chuẩn hóa theo năng lượng hiệu dụng (RMS Normalization): \n"
        "RMS = sqrt( (1/N) * sum_{n=1}^N x[n]^2 )\n"
        "x_rms[n] = x[n] * (target_rms / (RMS + eps)). Thường chọn target_rms = 0.1.",
        "Mạng CRNN sử dụng hàm phi tuyến ReLU/ELU và BiGRU. Nếu câu nói quá nhỏ, năng lượng Mel filterbank quá thấp, tín hiệu sẽ bị chìm vào ngưỡng zero sau khi trừ mean CMVN. Nếu câu nói quá to bị rè (clipping), tín hiệu sẽ bão hòa. Chuẩn hóa đưa mọi giọng nói về cùng một dải động lý tưởng.",
        "File: src/features/extraction.py\n"
        "Code: waveform = waveform - waveform.mean()\n"
        "waveform = waveform / (waveform.abs().max() + 1e-7)",
        "Hỏi: Điểm khác nhau giữa Peak Normalization và RMS Normalization là gì? Tại sao phải trừ đi mean trước?\n"
        "Đáp: Peak Normalization dựa vào giá trị mẫu lớn nhất (đỉnh) trong file để chia tỉ lệ, rất nhanh nhưng dễ bị ảnh hưởng bởi 1 tiếng lách cách (tiếng gõ micro). RMS Normalization dựa vào năng lượng trung bình thực tế của toàn câu nói, phản ánh độ to cảm nhận của tai người (loudness) tốt hơn. Việc trừ `waveform.mean()` trước khi chia là để loại bỏ độ lệch một chiều (DC Offset) do lỗi mạch phần cứng của micro giá rẻ gây ra, đưa gốc dao động về đúng điểm 0."
    )

    add_concept_box(
        doc,
        "CHỦ ĐỀ 6: BỘ LỌC TIỀN NHẤN (PRE-EMPHASIS FILTER)",
        "Bộ lọc Tiền nhấn (Pre-emphasis Filter) là một bộ lọc số thông cao (High-pass FIR Filter) bậc 1 đơn giản nhưng cực kỳ hiệu quả, được áp dụng ngay trên dạng sóng miền thời gian trước khi đưa vào phân tích Fourier. Bản chất của bộ lọc này là lấy mẫu hiện tại trừ đi một phần tỉ lệ của mẫu ngay trước đó.",
        "Toán học & Vật lý âm học:\n"
        "Công thức lọc: y[n] = x[n] - alpha * x[n-1], với hệ số alpha thường chọn trong khoảng [0.95, 0.97] (trong đồ án chọn 0.97).\n"
        "Hàm truyền đạt trong miền Z: H(z) = 1 - alpha * z^(-1).\n"
        "Đáp ứng tần số: Biên độ khuếch đại tăng dần khi tần số f tăng từ 0 đến Fs/2.\n"
        "Cơ sở vật lý: \n"
        "1. Nguồn xung thanh đới (Glottal source) phát ra luồng khí có năng lượng suy giảm tự nhiên theo quy luật -6 dB/octave khi tần số tăng.\n"
        "2. Bức xạ môi (Lip radiation) khuếch đại +6 dB/octave.\n"
        "3. Kết quả tổng thể: Các tần số cao (chứa phụ âm xát, phụ âm tắc như /s/, /t/, /k/) bị suy hao năng lượng rất lớn so với nguyên âm dải thấp. Bộ lọc tiền nhấn khuếch đại khoảng +20 dB ở dải cao để cân bằng phổ (spectral flattening).",
        "Nếu không có tiền nhấn, năng lượng dải tần số thấp (100 - 500 Hz) sẽ áp đảo hoàn toàn ma trận Log-Mel, khiến mạng nơ-ron chỉ học các nguyên âm mà bỏ qua các chi tiết tinh vi của các phụ âm quan trọng.",
        "File: src/features/extraction.py\n"
        "Code triển khai: \n"
        "def pre_emphasis(signal, alpha=0.97):\n"
        "    return np.append(signal[0], signal[1:] - alpha * signal[:-1])",
        "Hỏi: Bộ lọc tiền nhấn khuếch đại dải tần nào? Tại sao phải làm như vậy trong nhận dạng tiếng nói?\n"
        "Đáp: Bộ lọc tiền nhấn là bộ lọc thông cao bậc 1, nó khuếch đại dải tần số cao (từ 1 kHz đến 8 kHz) thêm khoảng 15-20 dB. Nguyên nhân vật lý là do thanh đới con người phát ra âm thanh bị suy giảm tự nhiên khoảng -6 dB trên mỗi quãng tám (octave) ở tần số cao. Điều này khiến các phụ âm vô thanh như /s/, /x/, /t/, /f/ có năng lượng rất yếu trên Spectrogram. Tiền nhấn giúp cân bằng động học toàn dải phổ, giúp mạng CRNN 'nhìn thấy' rõ nét các phụ âm này."
    )

    add_concept_box(
        doc,
        "CHỦ ĐỀ 7: PHÁT HIỆN TIẾNG NÓI & GỌT BỎ KHOẢNG LẶNG (VAD - VOICE ACTIVITY DETECTION)",
        "Voice Activity Detection (VAD) là kỹ thuật phân tách tín hiệu âm thanh thành 2 trạng thái: Vùng có tiếng nói (Speech) và Vùng khoảng lặng/nhiễu nền (Silence / Non-speech). Silence Trimming là thao tác cắt bỏ hoàn toàn các đoạn im lặng vô nghĩa ở đầu và cuối bản ghi trước khi đưa vào mô hình nhận dạng.",
        "Toán học:\n"
        "Các thuật toán VAD phổ biến trong đồ án:\n"
        "1. Ngưỡng decibel tương đối (Relative dB threshold): \n"
        "Tính đường bao công suất theo frame: P_frame = 10 * log10( sum(x^2) + eps ).\n"
        "Điểm bắt đầu/kết thúc tiếng nói được xác định khi P_frame vượt qua ngưỡng: Threshold = P_max - Top_dB (thường chọn top_db = 20 đến 30 dB).\n"
        "2. Kết hợp Năng lượng ngắn hạn (STE) và Tốc độ qua điểm không (ZCR): Tiếng nói bắt đầu khi STE vượt ngưỡng cao T_E1, hoặc ZCR vượt ngưỡng T_ZCR trong nhiều khung liên tiếp.",
        "Trong thực tế, khi người dùng bấm 'Bắt đầu ghi âm', họ thường mất 1-2 giây chuẩn bị trước khi nói và ngập ngừng 1-2 giây sau khi nói xong. Nếu đưa 4 giây im lặng này qua mạng CRNN, CTC Loss sẽ sinh ra toàn bộ token <blank>, làm tăng thời gian suy luận (latency) và dễ gây lỗi lặp từ.",
        "File: src/inference/realtime.py và src/data/dataset.py\n"
        "Code dùng librosa: trimmed_audio, _ = librosa.effects.trim(waveform, top_db=25)\n"
        "Nhận xét: Tham số top_db=25 nghĩa là mọi đoạn âm thanh có năng lượng thấp hơn đỉnh cao nhất 25 dB sẽ bị coi là khoảng lặng và bị gọt bỏ.",
        "Hỏi: Nếu đặt ngưỡng top_db quá nhỏ (ví dụ 10 dB) hoặc quá lớn (ví dụ 60 dB) trong hàm trim thì điều gì xảy ra?\n"
        "Đáp: Nếu đặt top_db quá nhỏ (10 dB), điều kiện để coi là tiếng nói quá khắt khe, hệ thống sẽ cắt mất các âm đuôi hoặc phụ âm phát âm nhẹ (như /h/, /c/, /p/), gây mất chữ (Deletion Error). Ngược lại, nếu đặt top_db quá lớn (60 dB), hệ thống sẽ không cắt được khoảng lặng vì tiếng thở nhẹ hay tiếng quạt gió máy tính cũng bị giữ lại, làm mô hình phải giải mã thừa nhiều frame vô ích."
    )

    # ==========================================
    # PHẦN IV: PHÂN KHUNG, CỬA SỔ HÓA VÀ ĐẶC TRƯNG MIỀN THỜI GIAN
    # ==========================================
    add_heading_1(doc, "PHẦN IV: PHÂN KHUNG, CỬA SỔ HÓA & ĐẶC TRƯNG MIỀN THỜI GIAN")

    add_concept_box(
        doc,
        "CHỦ ĐỀ 8: TÍNH DỪNG CỤC BỘ (QUASI-STATIONARITY), PHÂN KHUNG (FRAMING) & ĐỘ CHỒNG LẤP (OVERLAP)",
        "Tính dừng (Stationarity) là tính chất mà các đặc trưng thống kê của tín hiệu (kỳ vọng, phương sai, hàm tự tương quan) không thay đổi theo thời gian. Toàn bộ tín hiệu tiếng nói là một chuỗi ngẫu nhiên phi dừng (Non-stationary) vì các âm vị liên tục biến đổi. Tuy nhiên, trong các khoảng thời gian cực ngắn (20ms - 30ms), vị trí cơ học của bộ máy phát âm (dây thanh, môi, lưỡi, quai hàm) chưa kịp dịch chuyển đáng kể. Do đó, tín hiệu tiếng nói được coi là 'Dừng cục bộ' (Quasi-stationary / Short-time stationary).",
        "Toán học:\n"
        "Kỹ thuật Phân khung (Framing) chia dòng âm thanh x[n] liên tục thành các đoạn ngắn:\n"
        "- Frame Length (Độ dài khung): N = 25 ms = 0.025 * 16.000 = 400 mẫu (samples).\n"
        "- Frame Shift / Hop Length (Độ dịch khung): H = 10 ms = 0.010 * 16.000 = 160 mẫu (samples).\n"
        "- Độ chồng lấp (Overlap): Overlap = (N - H) / N = (400 - 160) / 400 = 240 mẫu = 60%.\n"
        "Số lượng khung thời gian T thu được từ file âm thanh có L mẫu:\n"
        "T = floor((L - N) / H) + 1. Cứ 1 giây âm thanh (16.000 mẫu) sẽ sinh ra đúng 98 - 100 frames.",
        "Phân tích Fourier (FFT) chỉ áp dụng được trên tín hiệu dừng. Phân khung 25ms là điều kiện tiên quyết để áp dụng STFT. Độ chồng lấp 60% đảm bảo thông tin ngữ âm liên tục không bị gián đoạn hay mất mát ở các đường biên khung.",
        "File: src/config/config.py và src/features/extraction.py\n"
        "Code cấu hình:\n"
        "N_FFT = 400          # 25ms tại 16kHz\n"
        "HOP_LENGTH = 160     # 10ms tại 16kHz\n"
        "WIN_LENGTH = 400     # Cửa sổ dài bằng N_FFT",
        "Hỏi: Tại sao không chọn khung thời gian dài hơn (ví dụ 100ms) hoặc ngắn hơn (ví dụ 2ms)?\n"
        "Đáp: Đây là bài toán đánh đổi thời gian - tần số (Heisenberg-Gabor Trade-off). Nếu chọn khung 100ms, cơ quan phát âm đã kịp chuyển từ nguyên âm này sang âm khác, tín hiệu không còn dừng cục bộ nữa, làm nhòe phổ. Nếu chọn khung quá ngắn 2ms (chỉ có 32 mẫu ở 16kHz), độ phân giải tần số delta_f = 16000 / 32 = 500 Hz sẽ quá thô, không thể phân biệt được các dải Formant nguyên âm (thường cách nhau chỉ 200 - 300 Hz). Khoảng 20ms - 25ms là tiêu chuẩn vàng của ngành xử lý tiếng nói."
    )

    add_concept_box(
        doc,
        "CHỦ ĐỀ 9: RÒ RỈ PHỔ (SPECTRAL LEAKAGE) & CỬA SỔ HAMMING / HANN",
        "Khi cắt một khung âm thanh x[n] dài 400 mẫu ra khỏi dòng tín hiệu, ta vô tình nhân nó với Cửa sổ chữ nhật (Rectangular Window - nhận giá trị 1 bên trong khung và 0 bên ngoài). Việc cắt đột ngột này tạo ra sự gián đoạn biên độ (discontinuity) rất lớn ở 2 đầu mép khung. Khi biến đổi Fourier, sự gián đoạn mép tạo ra các thành phần tần số giả mạo lan tỏa sang các tần số lân cận. Hiện tượng này gọi là Rò rỉ phổ (Spectral Leakage).",
        "Toán học & Cơ chế khắc phục:\n"
        "Trong miền thời gian: x_windowed[n] = x[n] * w[n], với 0 <= n <= N-1.\n"
        "Trong miền tần số: X_win(e^jw) = X(e^jw) * W(e^jw) (Tích chập với phổ của hàm cửa sổ).\n"
        "- Cửa sổ chữ nhật có thùy bên (side lobe) chỉ suy giảm -13 dB, gây rò rỉ phổ cực nặng.\n"
        "- Cửa sổ Hamming làm mượt 2 đầu mép khung dần về tiệm cận 0 bằng hàm Cosine:\n"
        "w_hamming[n] = 0.54 - 0.46 * cos( 2 * pi * n / (N - 1) )\n"
        "- Cửa sổ Hann (Hanning) đưa chính xác 2 đầu mép về đúng bằng 0:\n"
        "w_hann[n] = 0.5 * [1 - cos( 2 * pi * n / (N - 1) )] = sin^2( pi * n / (N - 1) )\n"
        "Độ suy giảm thùy bên của Hamming đạt -43 dB, của Hann đạt -31 dB, giúp triệt tiêu hoàn toàn rò rỉ phổ.",
        "Đảm bảo các đỉnh phổ (Spectral peaks - Formant) trên Spectrogram sắc nét, chính xác, không bị các thùy bên giả mạo làm mờ đục.",
        "File: src/features/extraction.py\n"
        "Code triển khai: window_fn = torch.hann_window(400)\n"
        "torchaudio.transforms.MelSpectrogram(n_fft=400, win_length=400, hop_length=160, window_fn=torch.hann_window)",
        "Hỏi: Tại sao bắt buộc phải nhân hàm cửa sổ (Windowing) trước khi thực hiện FFT?\n"
        "Đáp: Thuật toán FFT coi khung tín hiệu đầu vào lặp lại tuần hoàn vô tận từ -vô cùng đến +vô cùng. Nếu không nhân hàm cửa sổ làm mượt 2 đầu mép về 0, điểm kết thúc của chu kỳ này nối với điểm bắt đầu của chu kỳ tiếp theo sẽ tạo ra một bước nhảy gián đoạn thẳng đứng. Bước nhảy góc nhọn này sinh ra vô số họa tần tần số cao nhân tạo (rò rỉ phổ), làm nhòe toàn bộ ma trận Log-Mel và khiến mạng nơ-ron nhận diện sai các âm vị."
    )

    add_concept_box(
        doc,
        "CHỦ ĐỀ 10: NĂNG LƯỢNG NGẮN HẠN (SHORT-TIME ENERGY - STE) & TỐC ĐỘ QUA ĐIỂM KHÔNG (ZCR)",
        "Năng lượng ngắn hạn (Short-Time Energy - STE) và Tốc độ qua điểm không (Zero Crossing Rate - ZCR) là 2 đặc trưng miền thời gian cơ bản nhất, tính toán cực nhanh, dùng để phân loại bản chất vật lý của các đoạn âm thanh thành 3 nhóm: Âm hữu thanh (Voiced), Âm vô thanh (Unvoiced) và Khoảng lặng (Silence).",
        "Toán học:\n"
        "1. Năng lượng ngắn hạn của khung thứ m (STE):\n"
        "E[m] = sum_{n=0}^{N-1} ( x[m*H + n] * w[n] )^2\n"
        "2. Tốc độ qua điểm không (ZCR) - đếm số lần tín hiệu đổi dấu giữa các mẫu liên tiếp:\n"
        "ZCR[m] = (1 / 2N) * sum_{n=1}^{N-1} | sgn(x[n]) - sgn(x[n-1]) |\n"
        "Quy luật vật lý đối sánh:\n"
        "- Âm hữu thanh (Voiced - /a/, /e/, /m/, /u/): Dây thanh đới rung tuần hoàn, biên độ lớn => STE rất CAO, ZCR rất THẤP (tần số thấp).\n"
        "- Âm vô thanh (Unvoiced - /s/, /x/, /t/, /f/): Luồng khí cọ xát cơ quan miệng hỗn loạn như tạp âm trắng, biên độ nhỏ => STE THẤP, ZCR rất CAO (đổi dấu liên tục).\n"
        "- Khoảng lặng (Silence): Không có tiếng nói => Cả STE và ZCR đều xấp xỉ 0 (hoặc ZCR chỉ do nhiễu micro gây ra).",
        "Dùng trong các thuật toán VAD phân đoạn ranh giới từ nhanh chóng mà không cần tốn chi phí chạy qua mạng nơ-ron sâu.",
        "File: scripts/verify_preprocessing.py\n"
        "Code ZCR: zcr = librosa.feature.zero_crossing_rate(waveform, frame_length=400, hop_length=160)\n"
        "Code STE: energy = np.sum(librosa.util.frame(waveform, frame_length=400, hop_length=160)**2, axis=0)",
        "Hỏi: Dựa vào STE và ZCR, làm thế nào để bạn phân biệt được âm /a/ và âm /s/?\n"
        "Đáp: Âm /a/ là nguyên âm hữu thanh (dây thanh đới rung mạnh), năng lượng tập trung ở dải tần số thấp nên Năng lượng ngắn hạn STE rất lớn và Tốc độ qua điểm không ZCR rất thấp. Ngược lại, âm /s/ là phụ âm xát vô thanh (dây thanh không rung, chỉ có luồng hơi cọ xát qua kẽ răng), tạo ra tín hiệu dao động hỗn loạn tần số cao nên STE thấp nhưng ZCR rất cao. Sự kết hợp giữa STE và ZCR là chỉ dấu kinh điển để nhận dạng ranh giới âm vị trong xử lý tiếng nói."
    )

    # ==========================================
    # PHẦN V: ĐẶC TRƯNG MIỀN TẦN SỐ & SO SÁNH ĐỐI ĐẦU CHUYÊN SÂU
    # ==========================================
    add_heading_1(doc, "PHẦN V: ĐẶC TRƯNG MIỀN TẦN SỐ NÂNG CAO & ĐỐI SÁNH KỸ THUẬT")

    add_concept_box(
        doc,
        "CHỦ ĐỀ 11: NARROWBAND SPECTROGRAM VS WIDEBAND SPECTROGRAM",
        "Spectrogram (Phổ ký) là biểu diễn 2D trực quan thể hiện sự phân bố năng lượng của tín hiệu âm thanh theo cả Thời gian (trục hoành X) và Tần số (trục tung Y). Tùy thuộc vào việc lựa chọn độ dài cửa sổ phân tích (Window Length N), ta sẽ thu được 2 loại biểu đồ phổ ký có tính chất hoàn toàn đối lập: Phổ dải hẹp (Narrowband Spectrogram) và Phổ dải rộng (Wideband Spectrogram).",
        "Toán học (Nguyên lý bất định thời gian - tần số Heisenberg-Gabor):\n"
        "delta_t * delta_f >= 1 / (4 * pi)\n"
        "1. Phổ dải hẹp (Narrowband - Cửa sổ thời gian dài N ~ 40ms - 50ms):\n"
        "Thời gian dài => delta_t lớn => delta_f cực nhỏ (độ phân giải tần số cao).\n"
        "Nhìn thấy rõ từng vạch điều hòa (Harmonic horizontal lines: F0, 2F0, 3F0) chạy ngang song song. Dùng để đo Cao độ (Pitch F0).\n"
        "2. Phổ dải rộng (Wideband - Cửa sổ thời gian ngắn N ~ 3ms - 5ms):\n"
        "Thời gian ngắn => delta_t nhỏ (độ phân giải thời gian cao) => delta_f lớn.\n"
        "Các vạch điều hòa bị nhòe hợp nhất thành các dải đen đậm lớn nằm ngang: đó chính là các Formant (F1, F2). Đồng thời nhìn rõ từng vạch sọc đứng (vertical striations) thể hiện từng lần đóng mở của dây thanh đới.\n"
        "3. Lựa chọn trong ASR đồ án: Cửa sổ N = 25ms (400 mẫu ở 16kHz) là điểm cân bằng tối ưu (Sweet spot) giữa Wideband và Narrowband.",
        "ASR cần nhận dạng âm vị (nguyên âm/phụ âm) dựa vào vị trí Formant, đồng thời cần theo dõi sự chuyển biến ngữ âm nhanh chóng. Cửa sổ 25ms cung cấp đủ độ phân giải thời gian để bắt kịp phụ âm và đủ phân giải tần số để tách biệt Formant.",
        "File: src/features/extraction.py\n"
        "Code phân tích: Đồ án dùng N_FFT = 400, WIN_LENGTH = 400. Đây là kích thước phổ dải rộng vừa phải giúp làm nổi bật Formant cho mạng Conv2D học đặc trưng.",
        "Hỏi: Trên biểu đồ Spectrogram, tại sao phổ dải rộng lại thấy được Formant còn phổ dải hẹp lại thấy được các vạch Pitch Harmonics?\n"
        "Đáp: Theo nguyên lý bất định Gabor, cửa sổ càng dài trong miền thời gian thì độ phân giải tần số càng mịn (delta_f nhỏ). Phổ dải hẹp dùng cửa sổ dài (40ms) nên delta_f nhỏ hơn khoảng cách giữa các họa âm (F0 ~ 100-200Hz), giúp ta nhìn rõ từng đường kẻ ngang điều hòa của Pitch. Ngược lại, phổ dải rộng dùng cửa sổ ngắn (5ms) nên delta_f lớn (khoảng 300Hz), tích hợp năng lượng của nhiều họa âm kề nhau lại, làm lộ ra đường bao bao quát của khoang cộng hưởng miệng: đó chính là các dải Formant nguyên âm."
    )

    add_concept_box(
        doc,
        "CHỦ ĐỀ 12: MÔ HÌNH NGUỒN - BỘ LỌC (SOURCE-FILTER MODEL) & MÃ HÓA DỰ BÁO TUYẾN TÍNH (LPC)",
        "Mô hình Nguồn - Bộ lọc (Source-Filter Model) là nền tảng lý thuyết kinh điển của âm học tiếng nói (Acoustic Phonetics). Mô hình này chia quá trình phát âm của con người thành 2 thành phần độc lập hoàn toàn:\n"
        "1. Nguồn kích thích (Source): Luồng hơi từ phổi đi qua thanh đới tạo ra chuỗi xung tuần hoàn (đối với âm hữu thanh) hoặc luồng khí nhiễu hỗn loạn (đối với âm vô thanh).\n"
        "2. Bộ lọc khoang phát âm (Filter): Khoang miệng, mũi, hầu và môi đóng vai trò là một bộ lọc cộng hưởng âm học làm biến điệu phổ tần số của nguồn âm.\n"
        "Mã hóa dự báo tuyến tính (Linear Predictive Coding - LPC) là thuật toán toán học ước lượng chính xác hàm truyền đạt của Bộ lọc khoang miệng bằng cách giả định mẫu âm hiện tại x[n] có thể dự đoán xấp xỉ bằng tổ hợp tuyến tính của p mẫu quá khứ.",
        "Toán học LPC:\n"
        "Dự đoán mẫu: x_hat[n] = sum_{k=1}^p a_k * x[n-k]\n"
        "Sai số dự báo: e[n] = x[n] - x_hat[n] = x[n] - sum_{k=1}^p a_k * x[n-k]\n"
        "Hàm truyền đạt bộ lọc all-pole: H(z) = 1 / [ 1 - sum_{k=1}^p a_k * z^(-k) ]\n"
        "Bằng cách giải hệ phương trình Yule-Walker (dùng thuật toán Levinson-Durbin), ta tìm được các hệ số a_k. Các nghiệm cực (poles) của H(z) trên mặt phẳng phức chính là các tần số cộng hưởng Formant (F1, F2, F3) của nguyên âm!",
        "LPC giúp tách biệt hoàn toàn đặc trưng giọng người (bộ lọc khoang miệng - nhận diện chữ) ra khỏi cao độ người nói (nguồn thanh đới). Đây là cơ sở tại sao cùng nói chữ 'A' mà giọng nam trầm hay giọng nữ cao hệ thống đều nhận ra đúng chữ 'A'.",
        "File: scripts/verify_preprocessing.py\n"
        "Code tính LPC: a = librosa.lpc(y=frame, order=16)\n"
        "Nhận xét: Bậc LPC p = 16 (ở 16kHz) tương ứng với mô hình hóa được 8 cặp cực cộng hưởng (tối thiểu 4-5 Formant quan trọng).",
        "Hỏi: Mô hình Nguồn - Bộ lọc (Source-Filter Model) giải thích hiện tượng cùng nói một nguyên âm nhưng người khác nhau có giọng khác nhau như thế nào?\n"
        "Đáp: Theo mô hình Nguồn - Bộ lọc, nội dung từ ngữ (nguyên âm nào) được quyết định bởi Bộ lọc khoang miệng (vị trí lưỡi, môi tạo ra các Formant F1, F2). Còn âm sắc riêng biệt của từng người (nam, nữ, già, trẻ) được quyết định bởi Nguồn âm thanh đới (độ dài và độ căng dây thanh tạo ra tần số cơ bản Pitch F0). Khi người nam và nữ cùng nói từ 'MẸ', tần số Pitch F0 của họ khác nhau, nhưng hình dạng bộ lọc và cấu trúc các Formant F1, F2 của họ đều tương đương nhau, giúp hệ thống ASR giải mã chính xác cùng một văn bản."
    )

    add_concept_box(
        doc,
        "CHỦ ĐỀ 13: ĐỐI SÁNH TOÀN DIỆN: TẠI SAO DEEP LEARNING CHỌN LOG-MEL SPECTROGRAM THAY VÌ MFCC?",
        "Đây là CÂU HỎI KINH ĐIỂN NHẤT mà Hội đồng luôn dùng để kiểm tra sinh viên làm về Nhận dạng tiếng nói. MFCC (Mel-Frequency Cepstral Coefficients) là 'ông vua' của kỷ nguyên ASR truyền thống (HMM-GMM). Tuy nhiên, trong toàn bộ các hệ thống Deep Learning hiện đại (bao gồm mô hình CRNN của nhóm, Whisper của OpenAI hay Conformer của Google), các kỹ sư đều loại bỏ MFCC và quay lại sử dụng trực tiếp Log-Mel Spectrogram.",
        "Quy trình so sánh:\n"
        "Waveform -> STFT -> Mel Filterbank -> Log -> [DCT - Discrete Cosine Transform] -> MFCC\n"
        "Ta thấy rõ ràng: MFCC = Log-Mel Spectrogram + Phép biến đổi DCT!\n"
        "Bản chất của phép biến đổi DCT (Discrete Cosine Transform):\n"
        "1. Nén năng lượng vào một số ít hệ số đầu tiên (thường giữ 13 hệ số Cepstral).\n"
        "2. Giải tương quan (Decorrelation): Biến các dải tần kề cận đang phụ thuộc lẫn nhau thành các thành phần trực giao, độc lập thống kê với nhau.\n"
        "Lý do HMM-GMM bắt buộc dùng MFCC: Mô hình GMM sử dụng ma trận hiệp phương sai đường chéo (Diagonal Covariance Matrix) để tiết kiệm tham số. Ma trận đường chéo giả định các đặc trưng đầu vào phải độc lập thống kê. Nếu không có DCT giải tương quan, GMM sẽ bị lỗi dự đoán nghiêm trọng.\n"
        "Lý do Deep Learning (CNN/CRNN) LẠI BỎ MFCC VÀ DÙNG LOG-MEL:\n"
        "1. Mạng tích chập Conv2D hoạt động dựa trên giả định Không gian Cục bộ (Local Receptive Field): Các dải tần kề cận trên Log-Mel Spectrogram có mối tương quan cấu trúc không gian chặt chẽ (tạo thành các dải Formant liền mạch theo thời gian). Conv2D dùng kernel quét qua để bắt các mẫu cạnh, góc, vân phổ này.\n"
        "2. Phép biến đổi DCT làm xáo trộn và phá hủy hoàn toàn cấu trúc không gian hình học giữa các dải tần, khiến mạng Conv2D mất đi khả năng học đặc trưng cục bộ.\n"
        "3. Mạng Deep Learning có hàng trăm nghìn trọng số thừa khả năng tự giải tương quan thông qua các tầng nơ-ron ẩn, không cần sự can thiệp thô bạo của phép biến đổi DCT.",
        "Cung cấp ma trận đặc trưng 80 dải Mel bảo toàn 100% cấu trúc không gian phổ, làm đầu vào hoàn hảo cho 3 khối Conv2D trích xuất đặc trưng Formant trong mô hình của đồ án.",
        "File: src/features/extraction.py\n"
        "Code đồ án: torchaudio.transforms.MelSpectrogram(sample_rate=16000, n_fft=400, hop_length=160, n_mels=80)\n"
        "torch.log(mel_spec + 1e-6)  # Log-Mel, hoàn toàn không gọi hàm DCT/MFCC!",
        "Hỏi: Tại sao nhóm bạn không sử dụng đặc trưng MFCC mà lại dùng Log-Mel Spectrogram cho mô hình CRNN?\n"
        "Đáp: MFCC là phiên bản của Log-Mel sau khi đi qua phép biến đổi Cosine rời rạc (DCT) để giải tương quan. Điều này cực kỳ cần thiết cho các mô hình cổ điển như HMM-GMM vì GMM bắt buộc các đặc trưng phải độc lập thống kê để dùng ma trận hiệp phương sai đường chéo. Tuy nhiên, mô hình của nhóm em sử dụng mạng tích chập Conv2D. Conv2D cần giữ nguyên cấu trúc tương quan không gian giữa các dải tần số kề nhau để 'nhìn' thấy các dải Formant giống như nhận diện đường nét trong ảnh. Phép biến đổi DCT làm nén và xáo trộn cấu trúc không gian tần số, làm mất thông tin hữu ích cho Conv2D. Do đó, Log-Mel Spectrogram 80 chiều là đặc trưng tối ưu vượt trội cho kiến trúc Deep Learning CRNN."
    )

    add_concept_box(
        doc,
        "CHỦ ĐỀ 14: CHUẨN HÓA THỐNG KÊ PHỔ (CMVN - CEPSTRAL MEAN & VARIANCE NORMALIZATION)",
        "Chuẩn hóa Thống kê Phổ (Cepstral Mean and Variance Normalization - CMVN) là kỹ thuật chuẩn hóa Z-score trực tiếp trên từng dải tần số của ma trận đặc trưng Log-Mel Spectrogram theo chiều thời gian. Kỹ thuật này trừ đi giá trị trung bình (Mean) và chia cho độ lệch chuẩn (Standard Deviation) của từng hàng dải tần.",
        "Toán học & Mô hình Kênh truyền Méo tuyến tính:\n"
        "Giả sử tín hiệu tiếng nói s(t) đi qua micro và phòng thu có đáp ứng xung h(t) cùng nhiễu cộng n(t): x(t) = s(t) * h(t) + n(t).\n"
        "Trong miền tần số (bỏ qua nhiễu cộng): X(f) = S(f) * H(f).\n"
        "Khi lấy Log năng lượng: log |X(f)| = log |S(f)| + log |H(f)|.\n"
        "Ta thấy: Kênh truyền méo của micro và phòng thu H(f) bị biến thành một đại lượng CỘNG TĨNH (Additive Offset) không đổi theo thời gian!\n"
        "Khi tính giá trị trung bình theo thời gian: Mean[ log |X(f)| ] ≈ Mean[ log |S(f)| ] + log |H(f)|.\n"
        "Phép trừ Mean (Mean Subtraction):\n"
        "log |X(f)| - Mean[ log |X(f)| ] = log |S(f)| - Mean[ log |S(f)| ] (ĐÃ TRIỆT TIÊU HOÀN TOÀN log |H(f)|!).\n"
        "Công thức chuẩn hóa Z-score hoàn chỉnh cho mỗi dải tần số f:\n"
        "X_norm[f, t] = ( X[f, t] - mu[f] ) / ( sigma[f] + eps ).",
        "CMVN triệt tiêu hoàn toàn sự sai lệch âm học (Acoustic Channel Mismatch) giữa các micro thu âm khác nhau (ví dụ: mic phòng thu trong tập huấn luyện VIVOS vs mic laptop giá rẻ khi người dùng nói trực tiếp).",
        "File: src/features/extraction.py\n"
        "Code: mean = mel_spec.mean(dim=-1, keepdim=True)\n"
        "std = mel_spec.std(dim=-1, keepdim=True)\n"
        "normalized_mel = (mel_spec - mean) / (std + 1e-6)",
        "Hỏi: Tại sao phép trừ Mean trong CMVN lại có thể loại bỏ được sự méo mó âm thanh của Micro hay phòng thu?\n"
        "Đáp: Trong miền thời gian, tiếng nói bị cuộn (tích chập) với đáp ứng tần số của Micro. Khi chuyển sang miền phổ và lấy Logarit, phép nhân tích chập biến thành phép cộng đại số: Log(Âm thanh ghi được) = Log(Tiếng nói) + Log(Đặc tính Micro). Do đặc tính của Micro là cố định không đổi trong suốt câu nói, nên khi ta lấy trung bình theo thời gian và lấy từng khung trừ đi giá trị trung bình này, thành phần méo của Micro sẽ bị trừ triệt tiêu hoàn toàn, chỉ giữ lại sự biến thiên động học của tiếng nói con người."
    )

    # ==========================================
    # PHẦN VI: DỮ LIỆU THỰC NGHIỆM VIVOS & GIẢI PHÁP MICRO THỰC TẾ
    # ==========================================
    add_heading_1(doc, "PHẦN VI: TẬP DỮ LIỆU VIVOS & XỬ LÝ NHIỄU MICRO THỰC TẾ (DEMO)")

    add_concept_box(
        doc,
        "CHỦ ĐỀ 15: TẬP NGỮ LIỆU TIẾNG VIỆT VIVOS & CẤU TRÚC PHÂN CHIA HUẤN LUYỆN",
        "VIVOS là một trong những bộ ngữ liệu tiếng Việt chuẩn mở quy mô và uy tín nhất được phát triển bởi nhóm AILab (Trường ĐH Khoa học Tự nhiên - ĐHQG TP.HCM). Tập dữ liệu được thu âm bởi 65 người nói thuộc nhiều độ tuổi và vùng miền khác nhau, trong môi trường phòng cách âm chuyên nghiệp.",
        "Thông số chi tiết trong đồ án:\n"
        "- Tổng thời lượng: 15.4 giờ âm thanh.\n"
        "- Tổng số mẫu câu: 12.426 câu ghi âm (Tập train: 11.660 câu của 46 người nói; Tập test: 766 câu của 19 người nói độc lập hoàn toàn - Speaker-independent).\n"
        "- Định dạng file: WAV chuẩn Mono, Sampling rate 16.000 Hz, Bit depth 16-bit Signed PCM.\n"
        "- Từ điển từ vựng (Vocabulary): 105 tokens (bao gồm 26 chữ cái cơ bản, các chữ cái tiếng Việt có dấu: á, à, ả, ã, ạ, ă, ắ..., chữ số, dấu cách ' ' và token đặc biệt <blank> mã hóa ở vị trí số 0).\n"
        "- Tập từ vựng văn bản (Lexicon): 4.861 từ tiếng Việt đơn phân tách rõ ràng.",
        "Cung cấp tập dữ liệu mẫu chuẩn mực để mô hình âm học CRNN học được các phân phối xác suất âm vị tiếng Việt chuẩn xác trước khi thử nghiệm môi trường bên ngoài.",
        "File: src/data/dataset.py và models/weights/vietnamese_lexicon.json\n"
        "Code nạp từ điển: with open('models/weights/vietnamese_lexicon.json', 'r', encoding='utf-8') as f: lexicon = json.load(f)\n"
        "Nhận xét: File lexicon chứa đúng 4.861 từ tiếng Việt có nghĩa dùng cho thuật toán đối soát chính tả ở bước Hậu xử lý.",
        "Hỏi: Tập test của VIVOS có bị trùng người nói (Speaker Overlap) với tập train không? Ý nghĩa khoa học của việc này là gì?\n"
        "Đáp: Trong tập dữ liệu VIVOS, 19 người nói trong tập test hoàn toàn độc lập và không hề xuất hiện trong 46 người nói của tập train (Speaker-Independent Testing). Ý nghĩa khoa học là để đánh giá khả năng tổng quát hóa (Generalization) thực sự của mô hình học máy: đảm bảo mô hình nhận diện được ngữ âm tiếng Việt chứ không phải học vẹt (overfitting) chất giọng riêng của một vài người nói cụ thể."
    )

    add_concept_box(
        doc,
        "CHỦ ĐỀ 16: GIẢI QUYẾT BẤT ĐỒNG NHẤT ÂM HỌC (ACOUSTIC MISMATCH) KHI THU ÂM THỰC TẾ QUA MICRO",
        "Acoustic Mismatch (Bất đồng nhất âm học) là hiện tượng độ chính xác của hệ thống ASR bị tụt giảm nghiêm trọng khi chuyển từ môi trường thử nghiệm lý tưởng sang ứng dụng thực tế. Mô hình được huấn luyện trên tập VIVOS thu trong phòng thu tĩnh chuẩn, nhưng khi người dùng demo thực tế trên Micro Laptop hoặc Tai nghe Bluetooth sẽ gặp 3 loại nhiễu nghiêm trọng:\n"
        "1. Nhiễu môi trường (Ambient Noise): Tiếng quạt tản nhiệt laptop, tiếng gõ phím cạch cạch, tiếng nói chuyện xung quanh.\n"
        "2. Âm vang phòng (Room Reverberation): Sóng âm dội vào tường, kính, trần nhà tạo tiếng vang.\n"
        "3. Méo đáp ứng tần số của Micro: Micro giá rẻ bị suy giảm trầm trọng dải âm cao trên 5 kHz.",
        "Giải pháp kỹ thuật toàn diện được lập trình trong đồ án:\n"
        "1. Tiền xử lý âm thanh thời gian thực: Tích hợp module PyAudio thu âm trực tiếp ở định dạng mono 16kHz, chuyển đổi float32 tức thì.\n"
        "2. VAD động (Dynamic Energy VAD): Tự động phát hiện điểm bắt đầu nói và điểm kết thúc câu nói, loại bỏ toàn bộ tạp âm quạt tản nhiệt trong lúc người dùng chưa nói.\n"
        "3. Chuẩn hóa CMVN trực tiếp theo từng khung hình (Per-utterance CMVN): Triệt tiêu ngay lập tức độ lệch gain và đáp ứng tần số riêng của từng loại micro phần cứng.\n"
        "4. Negative Blank Bias (-3.0) & Lexicon Matching: Hậu xử lý sửa chữa các từ bị méo do nhiễu micro bằng cách đối sánh từ điển VIVOS 4.861 từ.",
        "Đảm bảo chương trình demo nhận diện giọng nói trực tiếp qua Micro (realtime inference) chạy mượt mà, đạt độ trễ cực thấp chỉ ~0.07 giây/câu, hạn chế tối đa lỗi nhận dạng sai.",
        "File: src/inference/realtime.py và test_mic.py\n"
        "Code thu âm: p = pyaudio.PyAudio(); stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)\n"
        "Code CMVN và Decode: log_mel = compute_log_mel(audio_chunk); text = decoder.decode(model(log_mel))",
        "Hỏi: Khi demo trực tiếp bằng Micro của laptop trong phòng có tiếng ồn, mô hình của nhóm bạn có những giải pháp gì để không bị nhận diện sai?\n"
        "Đáp: Nhóm em đã thiết kế chuỗi phòng thủ 4 lớp trong pipeline tiền xử lý và suy luận:\n"
        "Lớp 1: Khâu VAD lọc khoảng lặng dựa trên ngưỡng năng lượng để chặn tiếng quạt gió và tiếng ồn nền khi người dùng chưa nói.\n"
        "Lớp 2: Tiền xử lý chuẩn hóa CMVN trên từng câu nói để triệt tiêu đáp ứng tần số méo của micro laptop.\n"
        "Lớp 3: Kỹ thuật khởi tạo Bias âm (bias[blank] = -3.0) ngăn mô hình tự động đoán token Blank khi gặp đoạn âm thanh có nhiễu rè nhẹ.\n"
        "Lớp 4: Tầng hậu xử lý ràng buộc từ điển tiếng Việt (Lexicon Matching) và khử lặp từ (De-duplication) tự động nắn chỉnh các từ bị nhận diện lệch ngữ âm về từ tiếng Việt chuẩn có nghĩa."
    )

    # ==========================================
    # BẢNG TỔNG KẾT TẤT CẢ THÔNG SỐ TIỀN XỬ LÝ CỦA ĐỒ ÁN
    # ==========================================
    add_heading_1(doc, "BẢNG TRA CỨU NHANH THÔNG SỐ TIỀN XỬ LÝ (QUICK REFERENCE CHEAT SHEET)")
    add_paragraph(doc, "Bảng tra cứu tóm tắt các hằng số cấu hình chuẩn được thiết lập trong mã nguồn của nhóm (src/config/config.py), giúp Trưởng nhóm trả lời số liệu nhanh chóng khi Hội đồng vấn đáp:")

    tbl_summary = doc.add_table(rows=11, cols=4)
    tbl_summary.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_summary.style = 'Table Grid'
    sum_headers = ["Tham số kỹ thuật", "Giá trị trong đồ án", "Ý nghĩa vật lý / toán học", "Mã nguồn cài đặt"]
    for i, h in enumerate(sum_headers):
        c = tbl_summary.rows[0].cells[i]
        c.text = h
        c.paragraphs[0].runs[0].font.name = "Times New Roman"
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(10)
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(c, "1B365D")

    sum_rows = [
        ("Sampling Rate (Fs)", "16.000 Hz", "Tần số lấy mẫu, tần số Nyquist = 8.000 Hz bao trọn âm vị tiếng Việt.", "SAMPLE_RATE = 16000"),
        ("Channel Format", "1 (Mono)", "Âm thanh đơn kênh, triệt tiêu lệch pha và giảm dung lượng tính toán.", "torch.mean(waveform, dim=0)"),
        ("Frame Size (N_FFT)", "400 mẫu (25 ms)", "Khoảng thời gian tín hiệu đạt tính dừng cục bộ (Quasi-stationary).", "N_FFT = 400"),
        ("Frame Shift (Hop Length)", "160 mẫu (10 ms)", "Độ dịch khung, tạo độ chồng lấp 60% bảo toàn liên tục thông tin.", "HOP_LENGTH = 160"),
        ("Window Function", "Hann Window", "Làm mượt 2 đầu mép về 0, triệt tiêu hoàn toàn rò rỉ phổ (Spectral Leakage).", "window_fn = torch.hann_window"),
        ("Pre-emphasis Alpha", "0.97", "Lọc thông cao khuếch đại dải tần cao +20dB, bù suy hao nguồn thanh đới.", "y[n] = x[n] - 0.97 * x[n-1]"),
        ("Number of Mel Bands", "80 dải lọc", "Mô phỏng độ nhạy phi tuyến của ốc tai người theo thang tần số Mel.", "N_MELS = 80"),
        ("Log Transformation", "log(Mel + 1e-6)", "Nén dải động phi tuyến mô phỏng tai người cảm nhận âm lượng Decibel.", "torch.log(mel + 1e-6)"),
        ("Normalization (CMVN)", "Z-score theo thời gian", "Trừ mean chia std từng dải tần, triệt tiêu méo kênh truyền Micro.", "(mel - mean) / (std + 1e-6)"),
        ("Vocabulary Size", "105 tokens", "Tập nhãn đầu ra: 26 chữ cái, chữ cái tiếng Việt có dấu, số, space và blank.", "len(VOCAB) == 105")
    ]

    for row_idx, data in enumerate(sum_rows, start=1):
        for col_idx, val in enumerate(data):
            cell = tbl_summary.rows[row_idx].cells[col_idx]
            cell.text = val
            p = cell.paragraphs[0]
            p.runs[0].font.name = "Times New Roman"
            p.runs[0].font.size = Pt(9.5)
            p.paragraph_format.line_spacing = 1.15
            if col_idx == 0:
                p.runs[0].font.bold = True
                set_cell_background(cell, "D9E1F2")
            elif col_idx == 1:
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(0x00, 0x4B, 0x87)
                set_cell_background(cell, "FFFFFF")
            elif col_idx == 3:
                p.runs[0].font.italic = True
                set_cell_background(cell, "E8F4F8")
            else:
                set_cell_background(cell, "FFFFFF")

    for row in tbl_summary.rows:
        for i, w in enumerate([Inches(1.8), Inches(1.5), Inches(2.2), Inches(1.5)]):
            row.cells[i].width = w
            set_cell_margins(row.cells[i], top=60, bottom=60, left=80, right=80)

    # Lưu file ra cả 2 nơi
    out_dir1 = r"C:\Users\Admin\Downloads"
    out_dir2 = r"C:\Users\Admin\PycharmProjects\speech-processing-tutorial\project_cuoiky\docs"
    os.makedirs(out_dir1, exist_ok=True)
    os.makedirs(out_dir2, exist_ok=True)

    filename = "GIAI_MA_CHUYEN_SAU_TIEN_XU_LY_TIN_HIEU_TIENG_NOI_NHOM_6.docx"
    path1 = os.path.join(out_dir1, filename)
    path2 = os.path.join(out_dir2, filename)

    doc.save(path1)
    doc.save(path2)
    print(f"[OK] Đã tạo thành công cẩm nang Tiền xử lý tại: {path1}")
    print(f"[OK] Đã tạo thành công cẩm nang Tiền xử lý tại: {path2}")

if __name__ == "__main__":
    build_preprocessing_handbook()
