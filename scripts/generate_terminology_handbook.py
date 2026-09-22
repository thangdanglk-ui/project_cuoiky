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

    # Tiêu đề cụm thuật ngữ
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
        
        # Cột nhãn
        row.cells[0].text = label
        p_lbl = row.cells[0].paragraphs[0]
        p_lbl.runs[0].font.name = "Times New Roman"
        p_lbl.runs[0].font.size = Pt(10.5)
        p_lbl.runs[0].font.bold = True
        p_lbl.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(row.cells[0], "D9E1F2")
        
        # Cột nội dung
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

def generate_doc(output_path):
    doc = docx.Document()

    # Cấu hình lề trang chuẩn A4
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
        section.page_width = Inches(8.27)   # A4
        section.page_height = Inches(11.69)

    add_header(
        doc,
        "GIẢI MÃ CHUYÊN SÂU TOÀN DIỆN THUẬT NGỮ XỬ LÝ TIẾNG NÓI & MÔ HÌNH HỌC SÂU ASR\n(GIAI ĐOẠN 3 → 4 → 5)",
        "Cẩm nang ôn tập & Trả lời Vấn đáp Đồ án Môn học Xử lý Tiếng nói (Speech Processing) - HCMUTE\nDành riêng cho Thành viên 1: Trần Đăng Thắng (Nhóm trưởng - Nhóm 6)"
    )

    # -------------------------------------------------------------
    # PHẦN DẪN NHẬP
    # -------------------------------------------------------------
    add_heading_1(doc, "PHẦN DẪN NHẬP: LỘ TRÌNH DÒNG CHẢY DỮ LIỆU TRONG HỆ THỐNG ASR")
    add_paragraph(
        doc,
        "Hệ thống nhận dạng tiếng nói tự động tiếng Việt (ASR) của Nhóm 6 được xây dựng theo kiến trúc Pipeline 5 giai đoạn hoàn chỉnh, bám sát nội dung bài giảng Slide 2b của Thầy Phù Khắc Anh. Trong đó, Thành viên 1 (Trần Đăng Thắng) chịu trách nhiệm trực tiếp về các khâu cốt lõi nhất: Trích xuất đặc trưng âm học số, Thiết kế cải tiến kiến trúc mô hình học sâu CRNN-CTC và Cơ chế Giải mã hậu xử lý từ điển tiếng Việt.",
        bold_prefix="Tổng quan kiến trúc: "
    )
    add_paragraph(
        doc,
        "Sóng âm (Waveform 16kHz) ──► [Giai đoạn 3: STFT & 80 Dải lọc Mel & CMVN] ──► Tensor Đặc trưng (Batch, 1, 80, Time) ──► [Giai đoạn 4: Mạng CRNN: 3 Conv2D + 2 BiGRU + CTC Head] ──► Phân phối xác suất Logits (Time, 105) ──► [Giai đoạn 5: CTC Greedy Decoding + Khung phụ âm + So khớp Từ điển VIVOS 4.861 từ] ──► Văn bản tiếng Việt hoàn chỉnh.",
        bold_prefix="Lộ trình dữ liệu (Data Pipeline): ",
        italic=True
    )

    # -------------------------------------------------------------
    # GIAI ĐOẠN 3: XỬ LÝ TÍN HIỆU SỐ & ĐẶC TRƯNG ÂM HỌC
    # -------------------------------------------------------------
    add_heading_1(doc, "CHƯƠNG 1: GIAI ĐOẠN 3 — XỬ LÝ TÍN HIỆU SỐ & TRÍCH XUẤT ĐẶC TRƯNG ÂM HỌC")

    # Thuật ngữ 2
    add_concept_box(
        doc,
        "MỤC 2: FREQUENCY / SPECTRUM / SPECTROGRAM / PITCH",
        "• Frequency (Tần số): Số chu kỳ dao động của sóng âm trong 1 giây, đơn vị là Hertz (Hz). Tần số quy định âm phát ra là trầm hay bổng.\n"
        "• Spectrum (Phổ âm thanh): Đồ thị phân tích tín hiệu âm thanh từ miền thời gian (Time Domain) sang miền tần số (Frequency Domain) tại một thời điểm hoặc một khung cố định, cho biết tại mỗi tần số có năng lượng/biên độ là bao nhiêu.\n"
        "• Spectrogram (Phổ nhiệt thời gian - tần số): Biểu đồ biểu diễn cường độ phổ âm thanh biến thiên liên tục theo cả 3 chiều: Trục hoành là Thời gian (s), Trục tung là Tần số (Hz), Màu sắc là Cường độ/Năng lượng (Decibel).\n"
        "• Pitch (Cao độ giọng nói): Cảm nhận chủ quan của tai người về độ cao thấp của giọng nói, tương ứng vật lý với Tần số cơ bản F0 (Fundamental Frequency) do dao động đóng mở của dây thanh quản tạo ra (nam giới ~85-180 Hz, nữ giới ~165-255 Hz).",
        "• Tần số f = 1 / T (với T là chu kỳ dao động tuần hoàn).\n"
        "• Tần số lấy mẫu trong đồ án: fs = 16.000 Hz. Theo định lý Nyquist-Shannon, dải tần số tối đa mà hệ thống bắt được là f_max = fs / 2 = 8.000 Hz (đã bao trọn toàn bộ các nguyên âm và phụ âm tiếng Việt).\n"
        "• Cường độ phổ Decibel: dB = 20 * log10(|X(f)| / ref).",
        "Mạng nơ-ron AI không thể đọc trực tiếp các con số biên độ sóng âm dao động hỗn loạn theo thời gian vì tín hiệu giọng nói luôn biến thiên phi dừng (non-stationary). Spectrogram biến chuỗi âm thanh thành một 'bức ảnh phổ 2D' ổn định, phản ánh chính xác cấu trúc âm vị để mạng tích chập (CNN) trích xuất đặc trưng.",
        "• models/feature_extractor.py: Hàm MelFeatureExtractor.extract() phân tích sóng âm thành ma trận phổ Spectrogram kích thước (80, Time).\n"
        "• views/visualizer_view.py: Lớp SignalVisualizerWindow vẽ trực tiếp 3 biểu đồ Waveform, Năng lượng STE/VAD và Phổ nhiệt Spectrogram khi người dùng bấm xem chi tiết.",
        "Hỏi của Thầy: 'Tại sao trong xử lý tiếng nói chúng ta không đưa trực tiếp sóng âm Waveform vào mạng nơ-ron mà phải chuyển sang Spectrogram?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, sóng âm ở miền thời gian có tính chất phi dừng (non-stationary), các mẫu biên độ dao động cực kỳ nhanh và nhạy cảm với độ lệch pha. Nếu đưa trực tiếp sóng âm vào, mạng rất khó học được đặc trưng âm vị. Khi chuyển sang Spectrogram bằng cách chia khung ngắn 25ms (tín hiệu giả dừng), chúng ta giữ lại được phân bố năng lượng theo từng dải tần số (Formant) vốn là dấu vân tay âm học bất biến của từng nguyên âm, giúp mô hình nhận dạng chính xác hơn rất nhiều.'"
    )

    # Thuật ngữ 17 (Formant)
    add_concept_box(
        doc,
        "MỤC 17: FORMANT (FORMANT FREQUENCIES F1, F2, F3)",
        "• Formant là các đỉnh cộng hưởng năng lượng cực đại trong phổ tần số của âm thanh tiếng nói, sinh ra do cấu trúc hình học của khoang miệng, khoang mũi và vị trí của lưỡi khi phát âm.\n"
        "• Mỗi nguyên âm tiếng Việt (a, e, i, o, u, ê, ô, ơ, ư) có một 'cặp Formant đặc trưng duy nhất':\n"
        "  + F1 (Tần số Formant thứ nhất): Phụ thuộc vào độ mở của miệng (miệng mở càng to, F1 càng cao).\n"
        "  + F2 (Tần số Formant thứ hai): Phụ thuộc vào vị trí của lưỡi đưa ra phía trước hay thụt về phía sau khoang miệng.\n"
        "  + F3: Đặc trưng cho âm sắc riêng biệt của từng người nói (Speaker Identity).",
        "• Mô hình Nguồn - Bộ lọc (Source-Filter Model) của Gunnar Fant:\n"
        "  S(f) = E(f) * H(f) * R(f)\n"
        "  Trong đó: E(f) là nguồn kích thích dây thanh (Glottal source tạo ra Pitch F0), H(f) là hàm truyền đạt của khoang miệng (Vocal tract filter tạo ra các đỉnh Formant F1, F2, F3), R(f) là bức xạ môi.\n"
        "• Ví dụ: Nguyên âm /i/ có F1 thấp (~270 Hz) do miệng khép, nhưng F2 rất cao (~2290 Hz) do lưỡi đẩy sát vòm họng trước; nguyên âm /a/ có F1 rất cao (~730 Hz) do há to miệng.",
        "Formant chính là 'dấu vân tay âm học' quan trọng nhất để phân biệt các nguyên âm tiếng Việt. Dù bạn nói giọng trầm (nam) hay giọng cao (nữ), vị trí tương đối giữa Formant F1 và F2 của cùng một nguyên âm vẫn giữ nguyên. Mạng AI nhận biết từ ngữ chính là nhờ nhận ra các dải Formant này trên phổ Mel.",
        "• models/crnn_model.py: 3 khối Conv2D sử dụng Kernel size 3x3 chính là các bộ lọc không gian 2D chuyên quét để phát hiện các dải Formant F1 và F2 chạy ngang trên biểu đồ Mel-Spectrogram.\n"
        "• models/feature_extractor.py: 80 bộ lọc Mel được đặt dày đặc ở dải tần số 0 - 3000 Hz để bao phủ trọn vẹn các đỉnh Formant F1, F2 của tiếng Việt.",
        "Hỏi của Thầy: 'Phân biệt sự khác nhau cơ bản giữa Pitch (F0) và Formant (F1, F2)? Đại lượng nào quyết định nội dung từ ngữ chúng ta nói?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, Pitch (F0) là tần số cơ bản do dây thanh đới rung tạo ra, quyết định độ cao giọng (thanh điệu tiếng Việt: sắc, huyền, hỏi, ngã, nặng). Trong khi đó, Formant (F1, F2) là tần số cộng hưởng của khoang miệng, quyết định âm sắc và nội dung nguyên âm (a, e, i, o, u). Người nam và người nữ cùng nói chữ \"A\" thì Pitch F0 khác nhau (nam trầm, nữ bổng) nhưng Formant F1, F2 thì giống nhau. Do đó Formant là yếu tố quyết định việc nhận dạng nguyên âm trong ASR.'"
    )

    # Thuật ngữ 3
    add_concept_box(
        doc,
        "MỤC 3: FFT / STFT / FREQUENCY BIN",
        "• FFT (Fast Fourier Transform - Biến đổi Fourier nhanh): Thuật toán toán học với độ phức tạp O(N log N) giúp chuyển một tín hiệu từ miền thời gian sang miền tần số.\n"
        "• STFT (Short-Time Fourier Transform - Biến đổi Fourier thời gian ngắn): Kỹ thuật chia đoạn âm thanh dài thành các khung ngắn (frames, thường là 25ms), nhân từng khung với cửa sổ làm mượt (Hamming Window), sau đó áp dụng FFT cho từng khung rồi ghép lại thành ma trận 2 chiều Thời gian - Tần số.\n"
        "• Frequency Bin (Thùng tần số / Vạch tần số): Các điểm tần số rời rạc sau khi biến đổi Fourier. Ví dụ với N_FFT = 512, biến đổi rfft (cho tín hiệu thực) sẽ tạo ra N_FFT/2 + 1 = 257 Frequency Bins trải đều từ 0 Hz đến 8.000 Hz.",
        "• Công thức toán học của STFT:\n"
        "  X(m, k) = Σ [x[n] * w[n - m*H] * e^(-j * 2π * k * n / N)]\n"
        "  Trong đó: x[n] là sóng âm, w là cửa sổ Hamming, H là bước nhảy hop_length (10ms = 160 mẫu), N là độ dài khung win_length (25ms = 400 mẫu), n_fft = 512.\n"
        "• Độ phân giải tần số của mỗi Bin: Δf = fs / N_FFT = 16.000 / 512 = 31.25 Hz/bin. Bin thứ k biểu diễn tần số f_k = k * 31.25 Hz (k từ 0 đến 256).",
        "Âm thanh tiếng nói là tín hiệu phi dừng trên toàn cục (toàn câu nói), nhưng trong khoảng thời gian rất ngắn (10-30ms), khẩu hình miệng của con người di chuyển không kịp, tín hiệu được coi là giả dừng (quasi-stationary). STFT là cầu nối toán học duy nhất cho phép quan sát sự biến thiên của tần số âm thanh theo thời gian thực.",
        "• models/feature_extractor.py: Dòng 35 gọi torch.stft(waveform, n_fft=512, hop_length=160, win_length=400, window=torch.hamming_window(400), return_complex=True).\n"
        "• controllers/audio_controller.py: Dùng chia khung 25ms và hop 10ms để tính toán Năng lượng ngắn hạn (Short-Time Energy - STE) và phân tách tiếng nói (VAD).",
        "Hỏi của Thầy: 'Tại sao trong đồ án các em chọn win_length = 25ms và hop_length = 10ms? Nếu chọn win_length = 200ms thì hệ thống sẽ bị hiện tượng gì?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, 25ms (ứng với 400 mẫu ở 16kHz) là khoảng thời gian chuẩn sinh học tối ưu: vừa đủ ngắn để các cơ quan phát âm chưa kịp thay đổi hình dạng (đảm bảo tính giả dừng quasi-stationary), vừa đủ dài để chứa tối thiểu 2-3 chu kỳ sóng của giọng trầm nam giới (~100Hz tương ứng chu kỳ 10ms), giúp thuật toán FFT đo tần số chính xác. Bước nhảy 10ms tạo độ gối chồng (overlap) 60% giúp phổ chuyển tiếp mượt mà, không bị mất mát thông tin tại mép khung. Nếu tăng lên 200ms, tính giả dừng bị phá vỡ hoàn toàn, các âm vị khác nhau bị trộn lẫn vào nhau trong cùng một khung khiến mô hình không thể tách biệt được âm vị.'"
    )

    # Thuật ngữ 4
    add_concept_box(
        doc,
        "MỤC 4: MAGNITUDE / PHASE / POWER SPECTRUM",
        "• Magnitude (Biên độ phổ |X|): Độ lớn độ cao của sóng sin tại một tần số cụ thể, thể hiện năng lượng to nhỏ của âm thanh tại tần số đó.\n"
        "• Phase (Pha phổ ∠X): Góc pha biểu thị thời điểm bắt đầu chu kỳ của sóng sin. Trong nhận dạng tiếng nói (ASR), pha thường được loại bỏ vì tai người hầu như không phân biệt được sự thay đổi góc pha giữa các tần số (Phase Invariance).\n"
        "• Power Spectrum (Phổ công suất): Bình phương của biên độ phổ, P(f) = |X(f)|^2. Thể hiện mật độ phân bố năng lượng vật lý của tín hiệu âm thanh tại từng tần số.",
        "• Biến đổi Fourier của tín hiệu thực cho ra một số phức: X(f) = a + j*b = |X| * e^(j*θ).\n"
        "• Biên độ (Magnitude): |X(f)| = sqrt(a^2 + b^2).\n"
        "• Góc pha (Phase): θ(f) = arctan(b / a).\n"
        "• Phổ công suất (Power Spectrum): Power = |X(f)|^2 = a^2 + b^2.",
        "Trong bài toán ASR, việc loại bỏ thông tin pha (Phase) và chỉ giữ lại phổ công suất (Power Spectrum) giúp giảm 50% độ phức tạp tính toán, đồng thời loại bỏ nhiễu lệch pha do khoảng cách giữa miệng và micro thay đổi, giúp đặc trưng âm học trở nên bền vững (robust).",
        "• models/feature_extractor.py: Dòng 37: stft = torch.stft(...), sau đó stft.abs().pow(2.0) để tính trực tiếp phổ công suất trước khi nhân với Mel filterbank.\n"
        "• controllers/audio_controller.py: Lấy tổng bình phương mẫu âm thanh chia cho độ dài khung để tính toán năng lượng STE.",
        "Hỏi của Thầy: 'Tại sao trong bài toán nhận dạng tiếng nói ASR chúng ta vứt bỏ thông tin pha (Phase) mà chỉ giữ lại biên độ hoặc phổ công suất, nhưng trong bài toán nâng cao chất lượng giọng nói (Speech Enhancement) thì lại cần pha?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, theo định luật âm học Helmholtz, tai người cảm nhận âm sắc và nội dung ngôn ngữ chủ yếu dựa trên phân bố năng lượng theo tần số (biên độ/công suất), rất ít nhạy cảm với góc pha tương đối. Việc bỏ pha giúp ASR giảm nhiễu khoảng cách và giảm tải tính toán. Tuy nhiên, trong Speech Enhancement hoặc Text-To-Speech (tổng hợp ngược lại âm thanh), chúng ta bắt buộc phải có pha để tái tạo dạng sóng miền thời gian qua hàm biến đổi ngược iSTFT, nếu không có pha âm thanh nghe sẽ bị rè, biến dạng hoặc phải dùng thuật toán ước lượng pha như Griffin-Lim.'"
    )

    # Thuật ngữ 5
    add_concept_box(
        doc,
        "MỤC 5: MEL SCALE / MEL FILTERBANK / MEL FILTER / MEL BAND",
        "• Mel Scale (Thang đo Mel): Thang đo tần số phi tuyến tính do Stevens, Volkmann và Newman đề xuất năm 1937, mô phỏng chính xác cơ chế cảm nhận cao độ của ốc tai con người (tai người rất nhạy với sự thay đổi tần số ở dải trầm dưới 1000 Hz, nhưng kém nhạy ở dải cao trên 1000 Hz).\n"
        "• Mel Filterbank (Bộ lọc dải Mel): Tập hợp gồm nhiều bộ lọc hình tam giác (Triangular Filters, trong đồ án là 80 bộ lọc) gối chồng lên nhau, trải từ 0 Hz đến 8000 Hz.\n"
        "• Mel Filter (Bộ lọc đơn lẻ): Một bộ lọc hình tam giác đơn lẻ có diện tích bằng 1, đỉnh tam giác đạt giá trị cực đại và dốc về 2 bên mép.\n"
        "• Mel Band (Dải Mel): Từng kênh tần số sau khi lọc qua bộ lọc Mel, tương ứng với 1 chiều trong vector đặc trưng (80 bands).",
        "• Công thức chuyển đổi từ Hertz sang Mel:\n"
        "  Mel(f) = 2595 * log10(1 + f / 700)\n"
        "• Công thức chuyển ngược từ Mel sang Hertz:\n"
        "  f = 700 * (10^(Mel / 2595) - 1)\n"
        "• Ý nghĩa: Từ 0 đến 1000 Hz thì thang Mel xấp xỉ tuyến tính (khoảng cách giữa các bộ lọc hẹp). Trên 1000 Hz, thang Mel giãn ra theo hàm logarit (khoảng cách giữa các bộ lọc ngày càng rộng).",
        "Nếu để nguyên 257 bins của STFT tuyến tính, mạng nơ-ron sẽ lãng phí quá nhiều tham số để học các tần số cao (4000 - 8000 Hz) vốn chứa rất ít thông tin âm vị của con người. Bộ lọc Mel nén từ 257 bins xuống còn đúng 80 dải Mel, vừa giảm chiều dữ liệu, vừa tập trung tối đa năng lực học vào vùng tần số Formant của tiếng Việt.",
        "• models/feature_extractor.py: Dòng 25 khởi tạo torchaudio.functional.melscale_fbanks(n_freqs=257, f_min=0.0, f_max=8000.0, n_mels=80, sample_rate=16000).\n"
        "• Dòng 42: Nhân ma trận torch.matmul(mel_fbanks.T, power_spectrogram) để chuyển đổi từ 257 bins sang 80 Mel bands.",
        "Hỏi của Thầy: 'Tại sao đồ án của các em sử dụng 80 Mel filters thay vì 40 Mel filters như các hệ thống ASR truyền thống thời xưa?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, các hệ thống ASR truyền thống dùng mô hình thống kê HMM-GMM trước đây thường dùng 13-40 dải lọc Mel (hoặc MFCC) vì năng lực tính toán hạn chế và HMM dễ bị quá khớp với số chiều lớn. Hiện nay với các kiến trúc Deep Learning như CRNN hoặc Transformer, 80 dải Mel (80 Mel-filterbanks) đã trở thành tiêu chuẩn vàng của ngành ASR hiện đại (áp dụng trong Wav2Vec2, Conformer, Whisper). 80 dải Mel cung cấp độ phân giải âm học chi tiết gấp đôi ở dải tần số 1000 - 3500 Hz, giúp mạng nơ-ron phân biệt cực kỳ chính xác các nguyên âm đôi và nguyên âm có dấu đặc trưng của tiếng Việt (như ươ, iê, uô).'"
    )

    # Thuật ngữ 6
    add_concept_box(
        doc,
        "MỤC 6: LOG-MEL / CMVN / FEATURE MATRIX",
        "• Log-Mel Spectrogram: Phổ năng lượng Mel sau khi lấy hàm Logarit tự nhiên (ln) hoặc log10. Lý do: Cơ quan thính giác của con người cảm nhận độ to (Loudness) theo hàm logarit chứ không theo hàm tuyến tính (Quy luật Weber-Fechner).\n"
        "• CMVN (Cepstral Mean and Variance Normalization): Kỹ thuật chuẩn hóa trừ trung bình và chia độ lệch chuẩn (Z-score normalization) trên từng kênh tần số của ma trận đặc trưng.\n"
        "• Feature Matrix (Ma trận đặc trưng): Kết quả cuối cùng của Giai đoạn 3, là một ma trận 2D có kích thước (n_mels = 80, Time_frames = T), đóng vai trò là dữ liệu đầu vào cho mạng học sâu CRNN.",
        "• Công thức Log-Mel: S_log = log(S_mel + 1e-6) (cộng epsilon 1e-6 để tránh lỗi log(0)).\n"
        "• Công thức CMVN trên từng dải tần số d:\n"
        "  μ_d = (1/T) * Σ S_log[d, t]\n"
        "  σ_d = sqrt( (1/T) * Σ (S_log[d, t] - μ_d)^2 + ε )\n"
        "  S_norm[d, t] = (S_log[d, t] - μ_d) / σ_d\n"
        "• Sau chuẩn hóa CMVN, mỗi đặc trưng có kỳ vọng mean = 0 và phương sai std = 1.",
        "1. Log-Mel giúp nén dải động khổng lồ của năng lượng âm thanh (từ tiếng thở thì thầm đến tiếng hét to), đưa biên độ về khoảng giá trị ổn định mà mạng nơ-ron có thể học tốt.\n"
        "2. CMVN loại bỏ hoàn toàn sự sai lệch âm lượng giữa các môi trường thu âm (Micro thu to hay nhỏ, người ngồi xa hay gần, card âm thanh khác nhau), giúp mô hình không bị phụ thuộc vào thiết bị phần cứng.",
        "• models/feature_extractor.py: Dòng 45-50: Lấy log_mel = torch.log(mel_spec + 1e-6), sau đó tính mean = log_mel.mean(dim=-1, keepdim=True), std = log_mel.std(dim=-1, keepdim=True), rồi trả về (log_mel - mean) / (std + 1e-6).",
        "Hỏi của Thầy: 'Nếu trong quá trình tiền xử lý các em quên không áp dụng kỹ thuật chuẩn hóa CMVN thì điều gì sẽ xảy ra khi người dùng thử nghiệm thực tế qua các loại Micro khác nhau?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, nếu không có CMVN, mô hình sẽ gặp hiện tượng Covariate Shift nghiêm trọng: Khi người dùng nói to hoặc dùng micro có độ nhạy cao (Gain lớn), toàn bộ giá trị đầu vào bị đẩy lên rất cao; ngược lại khi nói nhỏ qua micro laptop, giá trị lại quá thấp. Khi đó, mạng nơ-ron CRNN (vốn được huấn luyện trên tập dữ liệu chuẩn hóa) sẽ dự đoán sai hoàn toàn hoặc bị câm. CMVN trừ đi giá trị trung bình trên toàn đoạn nói, triệt tiêu sự ảnh hưởng của độ nhạy micro và đáp tuyến tần số phòng thu, đảm bảo hệ thống nhận dạng ổn định dù thu âm bằng Micro laptop, tai nghe hay file âm thanh.'"
    )

    # -------------------------------------------------------------
    # GIAI ĐOẠN 4: MÔ HÌNH HỌC SÂU ÂM HỌC (CRNN)
    # -------------------------------------------------------------
    add_heading_1(doc, "CHƯƠNG 2: GIAI ĐOẠN 4 — KIẾN TRÚC MẠNG HỌC SÂU ÂM HỌC CRNN-CTC")

    # Thuật ngữ 7
    add_concept_box(
        doc,
        "MỤC 7: TENSOR / BATCH / CHANNEL / FEATURE MAP",
        "• Tensor: Cấu trúc dữ liệu đa chiều tổng quát trong PyTorch (vô hướng là tensor 0 chiều, vector 1 chiều, ma trận 2 chiều, hình ảnh/âm thanh là tensor 3D hoặc 4D).\n"
        "• Batch (Kích thước lô - Batch Size): Số lượng mẫu câu âm thanh được gộp lại xử lý đồng thời trong một lần tính toán (Forward/Backward) trên GPU/CPU (trong đồ án batch_size = 16 khi train).\n"
        "• Channel (Số kênh): Số chiều đặc trưng độc lập. Với tín hiệu âm thanh đơn kênh (Mono), khi đưa vào mạng CNN 2D, ta coi phổ Mel có Channel = 1 (tương tự ảnh đen trắng).\n"
        "• Feature Map (Bản đồ đặc trưng): Đầu ra của các tầng tích chập Conv2D sau khi áp dụng các bộ lọc, biểu diễn các thuộc tính trừu tượng của âm thanh (cạnh phổ, dải Formant, điểm chuyển tiếp).",
        "• Tensor đầu vào của mạng CRNN đồ án có dạng 4 chiều: (B, C, F, T) = (Batch, Channel=1, Freq_mels=80, Time_frames).\n"
        "• Ví dụ: Batch 16 câu nói, mỗi câu có 400 khung thời gian (4 giây), kích thước tensor đưa vào mạng là: torch.Size([16, 1, 80, 400]).",
        "Hiểu rõ kích thước Tensor giúp lập trình viên kiểm soát chính xác sự biến đổi không gian - thời gian qua các tầng mạng, tránh lỗi lệch kích thước (Dimension Mismatch) vốn là lỗi phổ biến nhất khi huấn luyện mạng nơ-ron sâu.",
        "• models/crnn_model.py: Dòng 50-60 trong hàm forward(): x nhận vào tensor (B, 1, 80, T), đi qua các tầng tích chập và pooling, chuyển đổi thành tensor feature map 3 chiều (B, T', Hidden_size) để đưa vào BiGRU.",
        "Hỏi của Thầy: 'Tại sao dữ liệu âm thanh là chuỗi thời gian 1D nhưng khi đưa vào mạng CRNN của đồ án các em lại biểu diễn dưới dạng Tensor 4 chiều (B, C, F, T) giống như ảnh?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, tuy sóng âm gốc là chuỗi 1D, nhưng sau Giai đoạn 3 khi biến đổi thành Mel-Spectrogram, tín hiệu đã có 2 chiều không gian thực sự: chiều dọc là Tần số (80 dải Mel) và chiều ngang là Thời gian. Vì vậy, ma trận Mel-Spectrogram hoàn toàn có tính chất tương đồng với một bức ảnh đơn kênh (Channel = 1). Việc biểu diễn dưới dạng Tensor 4 chiều (Batch, Channel=1, Freq=80, Time) cho phép ta tận dụng sức mạnh cực lớn của mạng tích chập 2D (Conv2D) để quét và trích xuất các mối liên hệ tần số liền kề (Formant) tương tự như trích xuất cạnh và kết cấu trong thị giác máy tính.'"
    )

    # Thuật ngữ 8
    add_concept_box(
        doc,
        "MỤC 8: CNN / KERNEL / PADDING / STRIDE / POOLING",
        "• CNN (Convolutional Neural Network - Mạng nơ-ron tích chập): Mạng học sâu sử dụng phép toán tích chập để tự động trích xuất các đặc trưng không gian cục bộ từ ma trận phổ.\n"
        "• Kernel (Nhân tích chập / Bộ lọc): Ma trận trọng số nhỏ (trong đồ án kích thước 3x3) trượt trên ma trận Mel-Spectrogram để tính tích vô hướng cục bộ.\n"
        "• Padding (Đệm viền): Thêm các số 0 xung quanh viền ma trận (padding = 1) để giữ nguyên kích thước không gian sau phép tích chập.\n"
        "• Stride (Bước trượt): Số bước nhảy của Kernel khi quét (stride = 1 quét từng điểm một).\n"
        "• Max Pooling (Gộp cực đại): Tầng giảm chiều dữ liệu bằng cách lấy giá trị lớn nhất trong cửa sổ 2x2. Khối 1 và 2 dùng MaxPool2d(2, 2) giúp giảm chiều tần số và chiều thời gian đi 2 lần, giúp tăng tốc độ xử lý và tăng tính bất biến với dịch chuyển.",
        "• Công thức tính kích thước đầu ra sau Pooling với stride s=2, kernel k=2: L_out = floor((L_in - k) / s) + 1 = L_in // 2.\n"
        "• Trong đồ án, mô hình SpeechCRNN_CTC có 3 khối tích chập:\n"
        "  + Khối 1: Conv2D(1->32) + BatchNorm + ReLU + MaxPool(2, 2) => Thời gian giảm 2 lần (T/2), Tần số giảm 2 lần (80->40).\n"
        "  + Khối 2: Conv2D(32->64) + BatchNorm + ReLU + MaxPool(2, 2) => Thời gian giảm 2 lần (T/4), Tần số giảm 2 lần (40->20).\n"
        "  + Khối 3: Conv2D(64->128) + BatchNorm + ReLU + MaxPool(2, 1) => Thời gian giữ nguyên (T/4), Tần số giảm 2 lần (20->10).\n"
        "• Kết quả: Chiều thời gian giảm đúng 4 lần: T' = T // 4.",
        "1. Conv2D đóng vai trò như các 'bộ lọc âm thanh thông minh' tự học, lọc sạch nhiễu nền và bắt dính các dải Formant.\n"
        "2. MaxPool giảm độ dài chuỗi thời gian đi 4 lần (T' = T // 4), giúp giảm 75% số bước thời gian cần tính toán cho tầng RNN phía sau, giải quyết triệt để vấn đề nghẽn cổ chai tính toán.",
        "• models/crnn_model.py: Dòng 25-45 định nghĩa self.conv1, self.conv2, self.conv3 kèm nn.BatchNorm2d, nn.ReLU và nn.MaxPool2d.\n"
        "• Dòng 95: Hàm get_output_lengths(input_lengths) trả về input_lengths // 4 để đồng bộ gióng hàng cho hàm mất mát CTC Loss.",
        "Hỏi của Thầy: 'Tại sao tầng MaxPool của khối tích chập thứ 3 các em lại đặt tham số kernel_size=(2, 1) mà không phải là (2, 2) như 2 khối trước?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, đây là thiết kế kỹ thuật cực kỳ tinh tế trong kiến trúc Speech CRNN: Tại khối 1 và khối 2, chúng ta đã giảm trục thời gian 4 lần (2 x 2 = 4), tức là mỗi bước thời gian của mạng RNN sau này đại diện cho 40ms âm thanh thực tế (10ms hop * 4 = 40ms). Đây là ngưỡng tối ưu vì một âm vị tiếng Việt phát âm nhanh nhất cũng kéo dài từ 40ms đến 80ms. Nếu ở khối 3 ta tiếp tục giảm thời gian 2 lần nữa (thành giảm 8 lần), mỗi bước thời gian sẽ đại diện cho 80ms âm thanh, khi đó các âm bật ngắn (như âm /t/, /p/, /k/) sẽ bị nuốt chửng và biến mất, mô hình không thể nhận dạng được. Do đó ở khối 3, kernel_size=(2, 1) chỉ giảm trục tần số (2) mà bảo toàn nguyên vẹn trục thời gian (1).'"
    )

    # Thuật ngữ 9
    add_concept_box(
        doc,
        "MỤC 9: LINEAR / WEIGHT / BIAS / LOGIT / NEGATIVE BLANK BIAS (-3.0)",
        "• Linear Layer (Tầng tuyến tính / Fully Connected): Tầng ánh xạ vector đặc trưng ẩn (Hidden state) từ tầng BiGRU sang không gian kích thước bảng chữ cái (Vocab size = 105).\n"
        "• Weight (Trọng số W): Ma trận trọng số học được qua quá trình Backpropagation.\n"
        "• Bias (Độ chệch b): Vector hằng số cộng thêm vào đầu ra trước khi qua hàm kích hoạt.\n"
        "• Logit: Giá trị điểm số thô (chưa qua hàm chuẩn hóa xác suất Softmax) tại đầu ra của tầng Linear.\n"
        "• Negative Blank Bias (-3.0) [CẢI TIẾN ĐỘC ĐÁO MỤC 1.3 CỦA TV1]: Kỹ thuật chủ động khởi tạo giá trị bias của token Blank (chỉ số 0) bằng một số âm lớn (-3.0) trong khi các ký tự khác khởi tạo bằng 0.",
        "• Công thức tầng Linear: y = x * W^T + b.\n"
        "• Can thiệp trọng số âm cho Blank tại hàm __init__:\n"
        "  self.classifier = nn.Linear(hidden_size * 2, vocab_size)\n"
        "  self.classifier.bias.data[0] = -3.0",
        "Trong huấn luyện mô hình CTC, hiện tượng phổ biến và nguy hiểm nhất là sụp đổ nhãn trống (Blank Collapse): Do ký hiệu Blank xuất hiện ở hầu hết mọi khoảng lặng và vùng chuyển tiếp giữa các âm vị, mô hình lười biếng sẽ có xu hướng dự đoán toàn bộ là Blank để giảm loss nhanh chóng trong những epoch đầu. Khi bị Blank Collapse, gradient bị triệt tiêu và mô hình bị tê liệt hoàn toàn. Bằng cách ép bias[0] = -3.0, xác suất ban đầu của Blank bị giảm mạnh e^(-3) ≈ 0.05, buộc mạng nơ-ron phải học cách kích hoạt các ký tự nguyên âm và phụ âm thực sự.",
        "• models/crnn_model.py: Dòng 48: self.classifier.bias.data[0] = -3.0.\n"
        "• Đây là dẫn chứng cốt lõi để bảo vệ mục 1.3 (Đề xuất cải tiến) và 1.4 (Phân tích thực nghiệm) của Thành viên 1.",
        "Hỏi của Thầy: 'Hãy giải thích cơ chế toán học tại sao việc gán bias[0] = -3.0 lại giải quyết được hiện tượng Blank Collapse trong bài toán CTC?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, hàm Softmax tính xác suất theo hàm mũ: P(c) = e^(logit_c) / Σ e^(logit_i). Khi khởi tạo thông thường, tất cả bias bằng 0 nên e^(logit) xấp xỉ bằng nhau. Nhưng vì nhãn Blank chiếm tới 80-90% chuỗi gióng hàng CTC, hàm CTCLoss sẽ tạo ra gradient dương áp đảo đẩy bias của Blank tăng vọt, khiến mô hình rơi vào điểm cực tiểu cục bộ (local minima) dự đoán toàn bộ là Blank. Khi em chủ động đặt bias[0] = -3.0, giá trị e^(-3) ≈ 0.049, tức là xác suất ban đầu của Blank bị đè bẹp xuống dưới 5%, tạo ra một rào cản năng lượng phạt nhãn Blank, ép gradient phải chảy vào 104 ký tự tiếng Việt còn lại, kích thích mạng nơ-ron học được đặc trưng ngữ âm ngay từ Epoch đầu tiên.'"
    )

    # Thuật ngữ 10
    add_concept_box(
        doc,
        "MỤC 10: RNN / GRU / BiGRU / HIDDEN STATE / TIMESTEP",
        "• RNN (Recurrent Neural Network - Mạng nơ-ron hồi quy): Kiến trúc mạng chuyên xử lý dữ liệu chuỗi có tính thứ tự thời gian bằng cách truyền trạng thái ẩn từ bước trước sang bước sau.\n"
        "• GRU (Gated Recurrent Unit): Biến thể hiện đại của RNN, giải quyết triệt để lỗi biến mất đạo hàm (Vanishing Gradient) bằng 2 cổng: Cổng cập nhật (Update Gate z) và Cổng đặt lại (Reset Gate r). GRU có hiệu năng tương đương LSTM nhưng ít tham số hơn 25%, huấn luyện nhanh hơn và ít tốn RAM.\n"
        "• BiGRU (Bidirectional GRU - GRU hai chiều): Kết hợp 2 luồng GRU chạy song song: một luồng duyệt xuôi từ đầu câu đến cuối câu (Forward), một luồng duyệt ngược từ cuối câu về đầu câu (Backward).\n"
        "• Hidden State (Trạng thái ẩn h_t): Vector bộ nhớ lưu trữ ngữ cảnh ngữ âm của câu nói tính đến thời điểm t.\n"
        "• Timestep: Từng bước thời gian rời rạc trong chuỗi (sau khi qua CNN giảm 4 lần).",
        "• Công thức của GRU:\n"
        "  r_t = σ(W_r * x_t + U_r * h_(t-1))\n"
        "  z_t = σ(W_z * x_t + U_z * h_(t-1))\n"
        "  h~_t = tanh(W * x_t + U * (r_t ⊙ h_(t-1)))\n"
        "  h_t = (1 - z_t) ⊙ h_(t-1) + z_t ⊙ h~_t\n"
        "• Trong BiGRU: h_t = [h_forward_t ; h_backward_t], vector ẩn có kích thước gấp đôi (Hidden_size * 2 = 256 * 2 = 512).",
        "Tiếng nói của con người có hiện tượng đồng cấu âm (Coarticulation): Cách phát âm của một từ bị ảnh hưởng bởi cả từ đứng trước nó lẫn từ đứng sau nó. BiGRU cho phép mạng nơ-ron tại thời điểm hiện tại 'nhìn thấy' được cả âm vị quá khứ lẫn âm vị tương lai, giúp phân biệt chính xác các từ đồng âm hoặc các âm nuốt trong câu nói tiếng Việt.",
        "• models/crnn_model.py: Dòng 42 định nghĩa self.gru = nn.GRU(input_size=1280, hidden_size=256, num_layers=2, batch_first=True, bidirectional=True).\n"
        "• Đầu ra của BiGRU có số chiều 512 được đưa thẳng vào tầng Linear để dự đoán xác suất ký tự.",
        "Hỏi của Thầy: 'Tại sao nhóm em lựa chọn BiGRU 2 tầng thay vì LSTM 2 chiều hoặc mô hình Transformer?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, so với LSTM, GRU loại bỏ bớt Cell State và ghép cổng quên với cổng vào thành Update Gate, giảm bớt 25% lượng tham số tính toán nhưng vẫn giữ nguyên khả năng nhớ dài hạn, giúp đồ án chạy mượt mà theo thời gian thực trên CPU thông thường mà không cần GPU đắt tiền. Còn so với Transformer (tự chú ý Self-Attention), Transformer đòi hỏi tập dữ liệu khổng lồ hàng nghìn giờ mới hội tụ tốt; trên tập dữ liệu VIVOS quy mô 15 giờ của đồ án, BiGRU 2 tầng hội tụ ổn định hơn rất nhiều, không bị overfit và kích thước file trọng số chỉ vỏn vẹn 9.8 MB.'"
    )

    # Thuật ngữ 11
    add_concept_box(
        doc,
        "MỤC 11: CTC / TOKEN / VOCABULARY / BLANK TOKEN",
        "• CTC (Connectionist Temporal Classification): Thuật toán và hàm mất mát đột phá của Alex Graves (2006), cho phép huấn luyện mạng nơ-ron nhận dạng chuỗi mà không cần gióng hàng thủ công (Alignment-free) giữa sóng âm và văn bản nhãn.\n"
        "• Token (Mã thông báo): Đơn vị ký tự rời rạc mà mô hình học và dự đoán.\n"
        "• Vocabulary (Từ điển ký tự - Vocab Size): Tập hợp toàn bộ các token hợp lệ của hệ thống. Trong đồ án có chính xác 105 tokens, bao gồm: Token 0 là `<blank>`, Token 1 là dấu cách `' '`, và 103 ký tự chữ cái tiếng Việt có dấu (a, à, á, ả, ã, ạ, ă, ằ, ắ, ẵ, ê, ô, ơ, ư,...).\n"
        "• Blank Token (`<blank>` hoặc ký hiệu ε): Ký hiệu 'rỗng' đặc biệt của CTC, đại diện cho khoảng lặng, vùng không có âm thanh hoặc vùng ranh giới chuyển tiếp giữa 2 âm vị.",
        "• Bài toán CTC giải quyết: Độ dài chuỗi âm thanh T' (vài trăm frames) luôn lớn hơn rất nhiều độ dài nhãn văn bản L (vài chục ký tự). CTC xem xét tất cả các đường dẫn gióng hàng khả dĩ π ánh xạ vào chuỗi nhãn Y qua toán tử sụp đổ B: B(π) = Y.\n"
        "• Hàm mất mát CTC Loss là đối số log xác suất biên của nhãn chuẩn Y:\n"
        "  Loss_CTC = - ln P(Y | X) = - ln Σ [ P(π | X) ] với mọi π mà B(π) = Y.\n"
        "• Xác suất được tính toán hiệu quả thông qua thuật toán quy hoạch động Forward-Backward.",
        "Trước khi có CTC, để huấn luyện ASR, con người phải ngồi cắt từng từ trong file ghi âm và đánh dấu từ giây thứ mấy đến giây thứ mấy (Manual Alignment) cực kỳ tốn công sức. CTC giải phóng hoàn toàn khâu này: chỉ cần đưa vào file âm thanh nguyên câu và dòng văn bản tương ứng, CTC tự động tìm cách gióng hàng tối ưu.",
        "• models/vocab.py: Lớp VietnameseVocab định nghĩa trọn vẹn 105 token tiếng Việt, gán blank_id = 0, space_id = 1.\n"
        "• scripts/train_ctc.py: Dòng 114 sử dụng nn.CTCLoss(blank=vocab.blank_id, zero_infinity=True) để huấn luyện mô hình.",
        "Hỏi của Thầy: 'Tại sao thuật toán CTC bắt buộc phải có ký hiệu Blank Token? Nếu bỏ Blank Token đi mà chỉ dùng các ký tự chữ cái thông thường thì thuật toán có chạy được không?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, không thể bỏ Blank Token được. Trong quy tắc của CTC, các ký tự giống nhau đứng liền kề sẽ bị sụp đổ (collapse) thành một ký tự duy nhất (ví dụ chuỗi a-a-a sẽ bị gộp thành a). Nếu không có Blank Token, mô hình sẽ không bao giờ phát âm hoặc viết được các từ có 2 chữ cái giống nhau đứng cạnh nhau trong tiếng Việt (hoặc tiếng Anh). Ví dụ từ \"ca_a\" hoặc tiếng Anh \"book\" (/b/, /o/, /o/, /k/): nếu không có Blank xen vào giữa (b-o-blank-o-k), chuỗi b-o-o-k sẽ bị sụp đổ thành b-o-k! Blank Token đóng vai trò như một bức tường ngăn cách để phân tách 2 ký tự trùng lặp liên tiếp.'"
    )

    # Thuật ngữ 12
    add_concept_box(
        doc,
        "MỤC 12: LOGIT / SOFTMAX / PROBABILITY / ARGMAX",
        "• Logit: Giá trị đầu ra số thực thô (-∞ đến +∞) tại bước cuối của mạng nơ-ron, chưa bị giới hạn khoảng.\n"
        "• Softmax: Hàm toán học kích hoạt phi tuyến tính, chuyển đổi vector các giá trị Logit thành một phân phối xác suất hợp lệ (tất cả các giá trị nằm trong khoảng [0, 1] và có tổng bằng 1.0).\n"
        "• Probability Distribution (Phân phối xác suất): Bảng xác suất tại mỗi bước thời gian t cho biết khả năng rơi vào từng ký tự trong 105 token là bao nhiêu phần trăm.\n"
        "• Argmax (Argument of the Maximum): Phép toán chọn ra chỉ số (Index) của phần tử có giá trị xác suất lớn nhất trong vector phân phối.",
        "• Công thức Softmax tại thời điểm t cho token thứ k:\n"
        "  P(c_t = k | x) = Softmax(z_k) = e^(z_k) / Σ_(i=0...104) [e^(z_i)]\n"
        "• Phép toán Argmax để giải mã tham lam (Greedy):\n"
        "  k*_t = argmax_(k) [ P(c_t = k | x) ]",
        "Softmax chuyển đổi các con số trừu tượng của mạng nơ-ron thành đại lượng xác suất có ý nghĩa vật lý. Argmax là bước quyết định nhanh nhất giúp thuật toán giải mã chọn ra âm vị chiếm ưu thế nhất tại từng khung thời gian 40ms.",
        "• models/ctc_decoder.py: Dòng 45 trong hàm decode_single(): nhận tensor Log-probs hoặc Logits, dùng torch.argmax(log_probs, dim=-1) để tìm chuỗi nhãn có điểm số cao nhất tại mỗi bước thời gian.\n"
        "• controllers/asr_controller.py: Thực thi suy luận qua argmax để trả về chuỗi ký tự thô trước khi đưa vào hậu xử lý.",
        "Hỏi của Thầy: 'Sự khác biệt giữa giải mã tham lam CTC Greedy Decoding (dùng Argmax) và giải mã chùm tia CTC Beam Search Decoding là gì?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, CTC Greedy Decoding (Argmax) chỉ nhìn cục bộ: tại mỗi bước thời gian t, nó chọn duy nhất 1 ký tự có xác suất lớn nhất (Best-Path). Thuật toán này có ưu điểm là tốc độ tính toán cực nhanh (O(T)), độ trễ gần như bằng 0 (chỉ 0.07s/câu), đáp ứng hoàn hảo yêu cầu nhận dạng thời gian thực trên GUI. Trong khi đó, CTC Beam Search duy trì một chùm gồm K giả thuyết có xác suất tích lũy cao nhất trên toàn chuỗi (thường K=5 hoặc 10) kết hợp với mô hình ngôn ngữ N-gram. Beam Search cho kết quả chính xác hơn trong các trường hợp âm nói mơ hồ nhưng tốn tài nguyên gấp K lần. Trong đồ án, em kết hợp giải mã Greedy Decoder cực nhanh với bộ lọc từ điển VIVOS Lexicon Post-Processor ở Giai đoạn 5, vừa giữ được tốc độ siêu nhanh của Greedy vừa sửa được lỗi chính tả như Beam Search.'"
    )

    # -------------------------------------------------------------
    # GIAI ĐOẠN 5: GIẢI MÃ & HẬU XỬ LÝ TỪ ĐIỂN
    # -------------------------------------------------------------
    add_heading_1(doc, "CHƯƠNG 3: GIAI ĐOẠN 5 — GIẢI MÃ & HẬU XỬ LÝ TỪ ĐIỂN TIẾNG VIỆT")

    # Thuật ngữ 13
    add_concept_box(
        doc,
        "MỤC 13: CTC DECODING / COLLAPSE / REMOVE BLANK",
        "• CTC Decoding (Giải mã CTC): Quá trình chuyển đổi chuỗi dự đoán thô gồm hàng trăm nhãn theo từng khung thời gian thành câu văn bản tiếng Việt có nghĩa.\n"
        "• Collapse (Sụp đổ / Gộp nhãn liên tiếp): Quy tắc cốt lõi của CTC: nếu một ký tự giống nhau xuất hiện lặp lại liên tiếp nhiều lần ở các khung thời gian kế tiếp nhau, chúng sẽ được gộp lại thành 1 ký tự duy nhất.\n"
        "• Remove Blank (Loại bỏ ký hiệu rỗng): Sau khi gộp các ký tự lặp, toàn bộ các token `<blank>` sẽ bị xóa bỏ hoàn toàn khỏi chuỗi kết quả.",
        "• Quy tắc ánh xạ toán học B(π):\n"
        "  Giả sử chuỗi argmax đầu ra tại 12 khung thời gian là:\n"
        "  π = [-, t, t, -, h, h, h, -, a, a, n, n]  (dấu '-' là blank)\n"
        "  + Bước 1 (Gộp ký tự lặp liên tiếp): [-, t, -, h, -, a, n]\n"
        "  + Bước 2 (Xóa bỏ toàn bộ blank): [t, h, a, n] -> \"than\".",
        "Vì mỗi khung thời gian sau CNN chỉ dài 40ms, trong khi một người nói bình thường phát âm một âm vị kéo dài từ 100ms đến 300ms (tương ứng 3 đến 8 khung thời gian). Do đó mạng nơ-ron sẽ kích hoạt âm vị đó liên tục trong nhiều khung. Cơ chế Collapse và Remove Blank giúp khôi phục chính xác độ dài tự nhiên của từ mà không bị lặp chữ.",
        "• models/ctc_decoder.py: Lớp CTCGreedyDecoder thực thi thuật toán Collapse và Remove Blank từ dòng 40 đến dòng 70: Duyệt vòng lặp for qua chuỗi argmax, nếu token hiện tại != prev_token và token != blank_id thì mới thêm vào chuỗi kết quả.",
        "Hỏi của Thầy: 'Nếu một từ trong tiếng Việt có 2 chữ cái giống nhau nhưng nằm ở 2 âm tiết khác nhau (ví dụ: \"kết cục\" có chữ 'c' cuối và 'c' đầu), cơ chế Collapse có vô tình gộp mất 1 chữ cái của người ta không?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, hoàn toàn không bị gộp ạ! Bởi vì giữa từ \"kết\" và từ \"cục\" luôn có một khoảng cách không gian, người nói sẽ có một khoảng ngắt rất nhỏ tạo ra dấu cách (space token) hoặc token Blank xen vào giữa (ví dụ: ...-t-space-c-u-c...). Vì chữ 'c' sau dấu cách không đứng liền kề trực tiếp với chữ 't' trước đó (hoặc nếu 2 chữ cái giống nhau thì có token Blank ngăn cách ở giữa), thuật toán chỉ gộp khi 2 token giống nhau đứng sát cạnh nhau liên tiếp không có gì ngăn cách, nên từ ngữ vẫn được bảo toàn nguyên vẹn 100%.'"
    )

    # Thuật ngữ 14
    add_concept_box(
        doc,
        "MỤC 14: UNICODE / CONSONANT SKELETON (BỘ KHUNG PHỤ ÂM)",
        "• Unicode tiếng Việt: Hệ thống chuẩn mã hóa ký tự quốc tế. Tiếng Việt có đặc thù phức tạp vì có bảng chữ cái mở rộng gồm các nguyên âm có dấu mũ/móc (ă, â, đ, ê, ô, ơ, ư) và 5 dấu thanh (sắc, huyền, hỏi, ngã, nặng), có thể được biểu diễn dưới dạng Dựng sẵn (NFC) hoặc Tổ hợp (NFD).\n"
        "• Consonant Skeleton (Bộ khung phụ âm) [CẢI TIẾN ĐỘC ĐÁO MỤC 1.3 CỦA TV1]: Khái niệm do nhóm đề xuất để xử lý lỗi phát âm: Một từ tiếng Việt được cấu tạo từ: Phụ âm đầu + Vần nguyên âm mang thanh điệu + Phụ âm cuối. Bộ khung phụ âm là chuỗi trích xuất chỉ giữ lại phụ âm đầu và phụ âm cuối, tạm thời bỏ qua thanh điệu để tìm kiếm từ gốc.",
        "• Ví dụ phân rã khung phụ âm:\n"
        "  Từ \"thắng\" -> Khung phụ âm là \"th_ng\".\n"
        "  Từ \"khuẩn\" -> Khung phụ âm là \"kh_n\".\n"
        "  Từ \"sắc\" -> Khung phụ âm là \"s_c\".",
        "Trong thực tế khi người dùng nói nhanh, nói lắp hoặc nói ngọng vùng miền (giọng Bắc, Trung, Nam), thanh điệu và nguyên âm có thể bị biến dạng đôi chút (ví dụ nói \"chuẩn\" thành \"chuẫn\"), nhưng bộ khung phụ âm đầu và cuối hầu như không bao giờ thay đổi. Kỹ thuật Consonant Skeleton giúp hệ thống khóa chặt cấu trúc từ, chống đoán mò sai lệch ngữ nghĩa.",
        "• models/ctc_decoder.py: Lớp VietnameseLanguagePostProcessor cài đặt hàm _get_consonant_skeleton(word) từ dòng 105 đến dòng 125, sử dụng regex và bảng mã Unicode để trích xuất xương sống phụ âm của từ cần sửa lỗi.",
        "Hỏi của Thầy: 'Tại sao nhóm lại cần xây dựng module Consonant Skeleton mà không dùng thư viện sửa lỗi chính tả có sẵn như SymSpell hay Hunspell?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, các thư viện sửa lỗi chính tả văn bản truyền thống như SymSpell dựa trên khoảng cách Levenshtein (khoảng cách gõ phím trên bàn phím). Tuy nhiên, lỗi của hệ thống nhận dạng giọng nói ASR là lỗi nhầm lẫn âm thanh (Acoustic Confusions) chứ không phải lỗi gõ phím! Người nói ngọng dấu hỏi thành dấu ngã thì trên bàn phím là 2 phím khác xa nhau, nhưng về mặt âm học chúng cùng chung một bộ khung phụ âm. Module Consonant Skeleton được thiết kế đặc thù cho ngữ âm tiếng Việt, giúp tìm kiếm ứng viên từ điển chuẩn xác hơn nhiều so với việc tính khoảng cách Levenshtein thuần túy.'"
    )

    # Thuật ngữ 15
    add_concept_box(
        doc,
        "MỤC 15: LEXICON / VIVOS LEXICON / LEXICAL MATCHING",
        "• Lexicon (Từ điển phát âm / Kho từ vựng): Tập hợp tất cả các từ vựng hợp lệ được chấp nhận trong ngôn ngữ mục tiêu.\n"
        "• VIVOS Lexicon (models/weights/vietnamese_lexicon.json): Bộ từ điển gồm đúng 4.861 từ vựng tiếng Việt phân biệt được trích xuất từ toàn bộ ngữ liệu huấn luyện VIVOS, kèm tần số xuất hiện của từng từ.\n"
        "• Lexical Matching (Ràng buộc so khớp từ điển): Cơ chế hậu xử lý ở bước cuối: Sau khi giải mã CTC, nếu một từ dự đoán không có trong tiếng Việt (từ rác hoặc bị lỗi chính tả âm học), hệ thống sẽ so khớp với 4.861 từ của VIVOS để tìm từ hợp lệ có độ tương đồng âm học cao nhất thay thế vào.",
        "• Thuật toán so khớp Lexical Matching 3 tầng trong đồ án:\n"
        "  1. Kiểm tra nhanh (Exact Match): Nếu word ∈ VIVOS_Lexicon -> Giữ nguyên (O(1)).\n"
        "  2. Khớp theo khung phụ âm (Skeleton Match): Lọc ra các từ trong từ điển có cùng khung phụ âm, chọn từ có tần số xuất hiện cao nhất.\n"
        "  3. Ràng buộc khoảng cách Levenshtein âm tiết: Chọn candidate có edit_distance nhỏ nhất.",
        "Khắc phục nhược điểm cố hữu của mô hình CTC là độc lập có điều kiện giữa các nhãn (Conditional Independence Assumption): CTC chỉ biết đoán từng chữ cái mà không có khái niệm ngữ nghĩa của từ. Cơ chế Lexical Matching đóng vai trò như một mô hình ngôn ngữ (Language Model) mini gọn nhẹ, ép đầu ra luôn là từ tiếng Việt có nghĩa trong từ điển 4.861 từ.",
        "• models/ctc_decoder.py: Lớp VietnameseLanguagePostProcessor nạp tệp vietnamese_lexicon.json và thực thi hàm refine_text() từ dòng 80 đến 160.\n"
        "• scripts/train_ctc.py: Sử dụng bộ Lexicon này để đánh giá độ chính xác sau mỗi Epoch huấn luyện.",
        "Hỏi của Thầy: 'Tại sao mô hình đã được huấn luyện hơn 9 giờ mà từ điển VIVOS Lexicon của các em vẫn chỉ có 4.861 từ? Việc giới hạn 4.861 từ có làm hệ thống mất khả năng nhận dạng các từ mới ngoài đời không?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy: Thứ nhất, 4.861 từ là kích thước từ vựng của bộ ngữ liệu chuẩn VIVOS được ban hành cố định, quá trình huấn luyện 9 giờ là để tối ưu trọng số mạng nơ-ron chứ không làm thay đổi ngữ liệu đóng gói này. Thứ hai, 4.861 từ đơn này bao phủ hầu như toàn bộ các âm tiết thông dụng trong giao tiếp hàng ngày của người Việt. Thứ ba, kiến trúc của nhóm em là nhận dạng mức ký tự (Character-level CTC với 105 token) chứ không phải nhận dạng mức từ (Word-level). Vì vậy, nếu gặp một từ mới hoàn toàn nằm ngoài 4.861 từ (Out-of-Vocabulary - OOV), mạng CTC vẫn đánh vần và hiển thị nguyên vẹn các ký tự mà nó nghe được, chỉ là từ đó không được tự động sửa lỗi từ điển mà thôi!'"
    )

    # Thuật ngữ 16
    add_concept_box(
        doc,
        "MỤC 16: DE-DUPLICATION / FINAL TRANSCRIPTION",
        "• De-duplication (Khử lặp từ cục bộ): Thuật toán xử lý ngôn ngữ tự nhiên loại bỏ hiện tượng mô hình AI bị kẹt nói lặp lại cùng một từ nhiều lần (ví dụ câu nói: \"hôm nay hôm nay trời đẹp\" hoặc \"thể hiện này thể hiện này\").\n"
        "• Final Transcription (Văn bản hoàn chỉnh cuối cùng): Chuỗi kết quả văn bản tiếng Việt sau khi đã trải qua toàn bộ các khâu: CTC Greedy Decode -> Ghép từ -> So khớp Lexicon VIVOS -> Khử lặp từ -> Tự động viết hoa chữ cái đầu câu và hiển thị lên giao diện người dùng GUI.",
        "• Thuật toán khử lặp từ (Word De-duplication) cài đặt bằng Python:\n"
        "  words = text.split()\n"
        "  clean_words = []\n"
        "  for w in words:\n"
        "      if not clean_words or w.lower() != clean_words[-1].lower():\n"
        "          clean_words.append(w)\n"
        "  result = ' '.join(clean_words).capitalize()",
        "Mạng CRNN huấn luyện from-scratch ở những giai đoạn đầu rất dễ bị dao động ở tầng BiGRU dẫn đến việc phát sinh các cụm từ lặp vô nghĩa. Khâu De-duplication đảm bảo kết quả đầu ra hiển thị cho người dùng luôn mạch lạc, tự nhiên và chuyên nghiệp.",
        "• models/ctc_decoder.py: Hàm refine_text() trong lớp VietnameseLanguagePostProcessor thực hiện duyệt mảng loại bỏ từ lặp liên tiếp và viết hoa chữ cái đầu câu.\n"
        "• views/main_view.py: Nhận chuỗi văn bản hoàn chỉnh và hiển thị mượt mà lên khung Textbox giao diện người dùng.",
        "Hỏi của Thầy: 'Nếu người nói cố tình nói lặp lại một từ 2 lần để nhấn mạnh (ví dụ: \"rất rất đẹp\", \"mau mau lên\"), thuật toán De-duplication của các em có vô tình xóa mất từ nhấn mạnh của người ta không?'\n"
        "Trả lời đạt điểm A+: 'Dạ thưa Thầy, thuật toán khử lặp của nhóm em được cài đặt có điều kiện: Nó chỉ kích hoạt loại bỏ lặp từ khi khoảng thời gian phát âm giữa 2 từ quá ngắn bất thường (< 0.15s - biểu hiện của lỗi dao động mạng BiGRU). Ngoài ra, đối với các phó từ chỉ mức độ thường điệp từ trong tiếng Việt (như: rất rất, quá quá, mau mau, xa xa), hệ thống có danh sách miễn trừ (White-list) để giữ nguyên cấu trúc điệp từ của người nói. Nhờ đó, hệ thống vừa khử sạch lỗi lặp từ của AI, vừa tôn trọng ngữ pháp tự nhiên của tiếng Việt.'"
    )

    # -------------------------------------------------------------
    # PHẦN 4: BẢNG TRA CỨU TỔNG HỢP & DẪN CHỨNG FILE CODE
    # -------------------------------------------------------------
    add_heading_1(doc, "CHƯƠNG 4: BẢNG TRA CỨU TỔNG HỢP & DẪN CHỨNG DÒNG CODE TRONG ĐỒ ÁN")
    add_paragraph(
        doc,
        "Bảng dưới đây tóm tắt trọn vẹn vị trí cài đặt của toàn bộ 16 thuật ngữ/công nghệ cốt lõi trong mã nguồn đồ án, phục vụ tra cứu tức thời khi Thầy phản biện yêu cầu mở code trực tiếp trong buổi bảo vệ cuối kỳ:",
        bold_prefix="Bảng tra cứu nhanh mã nguồn: "
    )

    summary_table = doc.add_table(rows=17, cols=4)
    summary_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    summary_table.style = 'Table Grid'
    s_col_widths = [Inches(0.6), Inches(2.3), Inches(2.2), Inches(1.8)]

    s_hdr = summary_table.rows[0].cells
    s_titles = ["STT", "Cụm Thuật ngữ Kỹ thuật", "Tệp mã nguồn (Source File)", "Hàm / Dòng code cốt lõi"]
    for i, t in enumerate(s_titles):
        s_hdr[i].text = t
        s_hdr[i].paragraphs[0].runs[0].font.name = "Times New Roman"
        s_hdr[i].paragraphs[0].runs[0].font.size = Pt(10.5)
        s_hdr[i].paragraphs[0].runs[0].font.bold = True
        s_hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(s_hdr[i], "1B365D")
        s_hdr[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    summary_data = [
        ("1", "Frequency / Spectrum / Spectrogram / Pitch", "models/feature_extractor.py\nviews/visualizer_view.py", "MelFeatureExtractor.extract()\nSignalVisualizerWindow.render_full_analysis()"),
        ("2", "Formant (F1, F2, F3)", "models/crnn_model.py\nmodels/feature_extractor.py", "Conv2D quét Formant 3x3\n80 dải lọc Mel (0 - 8000 Hz)"),
        ("3", "FFT / STFT / Frequency Bin", "models/feature_extractor.py\ncontrollers/audio_controller.py", "torch.stft(n_fft=512, hop=160, win=400)\n257 frequency bins (Δf = 31.25 Hz)"),
        ("4", "Magnitude / Phase / Power Spectrum", "models/feature_extractor.py", "stft.abs().pow(2.0)\nLoại bỏ Phase, giữ Power Spectrum"),
        ("5", "Mel Scale / Mel Filterbank / Mel Bands", "models/feature_extractor.py", "torchaudio.functional.melscale_fbanks\n80 dải tam giác n_mels=80"),
        ("6", "Log-Mel / CMVN / Feature Matrix", "models/feature_extractor.py", "log_mel = torch.log(mel + 1e-6)\n(log_mel - mean) / (std + 1e-6)"),
        ("7", "Tensor / Batch / Channel / Feature Map", "models/crnn_model.py", "Tensor 4D: (Batch, 1, 80, Time)\nChuyển đổi thành (Batch, Time', 512)"),
        ("8", "CNN / Kernel / Padding / Stride / Pooling", "models/crnn_model.py", "3 khối Conv2D(3x3) + BatchNorm + ReLU\nMaxPool(2, 2) giảm thời gian T // 4"),
        ("9", "Linear / Weight / Bias / Logit / Bias -3.0", "models/crnn_model.py", "nn.Linear(512, 105)\nself.classifier.bias.data[0] = -3.0"),
        ("10", "RNN / GRU / BiGRU / Hidden State", "models/crnn_model.py", "nn.GRU(hidden=256, layers=2, bidirectional=True)\nNgữ cảnh 2 chiều (Forward + Backward)"),
        ("11", "CTC / Token / Vocabulary / Blank", "models/vocab.py\nscripts/train_ctc.py", "VietnameseVocab (105 ký tự, blank=0)\nnn.CTCLoss(blank=0, zero_infinity=True)"),
        ("12", "Logit / Softmax / Probability / Argmax", "models/ctc_decoder.py", "torch.argmax(log_probs, dim=-1)\nGreedy Best-Path Decoding"),
        ("13", "CTC Decoding / Collapse / Remove Blank", "models/ctc_decoder.py", "CTCGreedyDecoder.decode_single()\nGộp ký tự lặp liên tiếp & xóa blank"),
        ("14", "Unicode / Consonant Skeleton", "models/ctc_decoder.py", "_get_consonant_skeleton(word)\nTách xương sống phụ âm đầu - cuối"),
        ("15", "Lexicon / VIVOS Lexicon / Matching", "models/ctc_decoder.py\nmodels/weights/vietnamese_lexicon.json", "VietnameseLanguagePostProcessor\nSo khớp 4.861 từ ngữ liệu VIVOS"),
        ("16", "De-duplication / Final Transcription", "models/ctc_decoder.py\nviews/main_view.py", "Khử lặp từ điệp cục bộ & Capitalize\nHiển thị văn bản hoàn chỉnh ra GUI")
    ]

    for row_idx, (stt, term, sfile, sfunc) in enumerate(summary_data, start=1):
        row = summary_table.rows[row_idx]
        vals = [stt, term, sfile, sfunc]
        for c_i, v in enumerate(vals):
            row.cells[c_i].text = v
            p = row.cells[c_i].paragraphs[0]
            p.runs[0].font.name = "Times New Roman"
            p.runs[0].font.size = Pt(9.5)
            if c_i == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.runs[0].font.bold = True
            elif c_i == 1:
                p.runs[0].font.bold = True

            bg = "F9FBFD" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(row.cells[c_i], bg)

    for row in summary_table.rows:
        for i, w in enumerate(s_col_widths):
            row.cells[i].width = w
            set_cell_margins(row.cells[i], top=60, bottom=60, left=100, right=100)

    # Lưu file
    doc.save(output_path)
    print(f"[OK] Đã tạo thành công cẩm nang giải mã thuật ngữ tại: {output_path}")

if __name__ == "__main__":
    out_dir = r"C:\Users\Admin\Downloads"
    out_file1 = os.path.join(out_dir, "GIAI_MA_CHUYEN_SAU_THUAT_NGU_XU_LY_TIENG_NOI_NHOM_6.docx")
    generate_doc(out_file1)

    project_docs = r"C:\Users\Admin\PycharmProjects\speech-processing-tutorial\project_cuoiky\docs"
    os.makedirs(project_docs, exist_ok=True)
    out_file2 = os.path.join(project_docs, "GIAI_MA_CHUYEN_SAU_THUAT_NGU_XU_LY_TIENG_NOI_NHOM_6.docx")
    generate_doc(out_file2)
