"""
Module Đo lường và Đánh giá Hiệu năng Nhận dạng Tiếng nói (ASR Metrics)
Cung cấp các hàm tính toán chuẩn quốc tế:
- CER (Character Error Rate - Tỉ lệ lỗi cấp độ ký tự)
- WER (Word Error Rate - Tỉ lệ lỗi cấp độ từ vựng)
- Thuật toán khoảng cách Levenshtein (Quy hoạch động) thuần Python, không phụ thuộc thư viện ngoài.
"""

import unicodedata
import re

def normalize_text(text: str) -> str:
    """
    Chuẩn hóa văn bản trước khi so khớp:
    - Đưa về chữ thường
    - Chuẩn hóa dạng biểu diễn Unicode NFC
    - Loại bỏ dấu câu không cần thiết (, . ? ! : ; " ' -)
    - Xóa khoảng trắng thừa
    """
    if not text:
        return ""
    # Chuẩn hóa Unicode NFC
    text = unicodedata.normalize("NFC", str(text).lower().strip())
    # Loại bỏ dấu câu thông thường
    text = re.sub(r'[,.?!\":;\-_—()\[\]{}…`~*+=\\/<>@#$%^&]', ' ', text)
    # Gộp khoảng trắng liên tiếp
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def levenshtein_alignment(ref_seq, hyp_seq):
    """
    Tính khoảng cách Levenshtein giữa 2 chuỗi (danh sách ký tự hoặc từ)
    bằng thuật toán Quy hoạch động (Dynamic Programming).
    
    Trả về:
    - distance: Tổng số thao tác sửa đổi tối thiểu (S + D + I)
    - substitutions (S): Số phép thay thế
    - deletions (D): Số phép xóa (có trong ref nhưng thiếu trong hyp)
    - insertions (I): Số phép chèn (thừa trong hyp mà không có trong ref)
    """
    m, n = len(ref_seq), len(hyp_seq)
    # dp[i][j] lưu khoảng cách chỉnh sửa nhỏ nhất giữa ref_seq[:i] và hyp_seq[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref_seq[i - 1] == hyp_seq[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # Deletion (xóa từ/ký tự trong ref)
                    dp[i][j - 1],      # Insertion (chèn thêm vào hyp)
                    dp[i - 1][j - 1]   # Substitution (thay thế)
                )

    # Truy vết ngược (Backtracking) để bóc tách chi tiết S, D, I
    i, j = m, n
    s, d, ins = 0, 0, 0
    while i > 0 or j > 0:
        if i > 0 and j > 0 and ref_seq[i - 1] == hyp_seq[j - 1]:
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            s += 1
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            d += 1
            i -= 1
        elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
            ins += 1
            j -= 1
        else:
            # Phòng ngừa trường hợp biên
            if i > 0:
                d += 1
                i -= 1
            elif j > 0:
                ins += 1
                j -= 1

    return dp[m][n], s, d, ins

def calculate_cer(reference: str, hypothesis: str, normalize: bool = True):
    """
    Tính Tỉ lệ Lỗi Ký tự (Character Error Rate - CER):
    CER = (S + D + I) / N_chars
    
    Trả về dict gồm:
    - cer: Tỉ lệ lỗi ký tự (0.0 đến 1.0+)
    - distance: Tổng số lỗi (S + D + I)
    - s: Số phép thay thế
    - d: Số phép xóa
    - i: Số phép chèn
    - ref_len: Tổng số ký tự trong câu chuẩn (N_chars)
    """
    if normalize:
        ref_clean = normalize_text(reference)
        hyp_clean = normalize_text(hypothesis)
    else:
        ref_clean = str(reference)
        hyp_clean = str(hypothesis)

    ref_chars = list(ref_clean)
    hyp_chars = list(hyp_clean)
    n = len(ref_chars)

    if n == 0:
        dist = len(hyp_chars)
        return {
            "cer": 1.0 if dist > 0 else 0.0,
            "distance": dist,
            "s": 0,
            "d": 0,
            "i": dist,
            "ref_len": 0
        }

    dist, s, d, ins = levenshtein_alignment(ref_chars, hyp_chars)
    cer = dist / n
    return {
        "cer": cer,
        "distance": dist,
        "s": s,
        "d": d,
        "i": ins,
        "ref_len": n
    }

def calculate_wer(reference: str, hypothesis: str, normalize: bool = True):
    """
    Tính Tỉ lệ Lỗi Từ vựng (Word Error Rate - WER):
    WER = (S + D + I) / N_words
    
    Trả về dict gồm:
    - wer: Tỉ lệ lỗi từ vựng (0.0 đến 1.0+)
    - distance: Tổng số lỗi (S + D + I)
    - s: Số phép thay thế
    - d: Số phép xóa
    - i: Số phép chèn
    - ref_len: Tổng số từ trong câu chuẩn (N_words)
    """
    if normalize:
        ref_clean = normalize_text(reference)
        hyp_clean = normalize_text(hypothesis)
    else:
        ref_clean = str(reference)
        hyp_clean = str(hypothesis)

    ref_words = ref_clean.split()
    hyp_words = hyp_clean.split()
    n = len(ref_words)

    if n == 0:
        dist = len(hyp_words)
        return {
            "wer": 1.0 if dist > 0 else 0.0,
            "distance": dist,
            "s": 0,
            "d": 0,
            "i": dist,
            "ref_len": 0
        }

    dist, s, d, ins = levenshtein_alignment(ref_words, hyp_words)
    wer = dist / n
    return {
        "wer": wer,
        "distance": dist,
        "s": s,
        "d": d,
        "i": ins,
        "ref_len": n
    }

def calculate_corpus_metrics(references, hypotheses, normalize: bool = True):
    """
    Tính toán chỉ số WER và CER trung bình toàn tập ngữ liệu (Corpus-level):
    Corpus_WER = sum(S + D + I) / sum(N_words)
    Corpus_CER = sum(S + D + I) / sum(N_chars)
    
    Đảm bảo tính chuẩn xác toán học (Micro-average), không bị thiên lệch bởi câu ngắn/dài.
    """
    total_w_dist, total_w_ref = 0, 0
    total_w_s, total_w_d, total_w_i = 0, 0, 0

    total_c_dist, total_c_ref = 0, 0
    total_c_s, total_c_d, total_c_i = 0, 0, 0

    num_samples = len(references)
    for ref, hyp in zip(references, hypotheses):
        w_res = calculate_wer(ref, hyp, normalize=normalize)
        total_w_dist += w_res["distance"]
        total_w_s += w_res["s"]
        total_w_d += w_res["d"]
        total_w_i += w_res["i"]
        total_w_ref += w_res["ref_len"]

        c_res = calculate_cer(ref, hyp, normalize=normalize)
        total_c_dist += c_res["distance"]
        total_c_s += c_res["s"]
        total_c_d += c_res["d"]
        total_c_i += c_res["i"]
        total_c_ref += c_res["ref_len"]

    corpus_wer = (total_w_dist / total_w_ref) if total_w_ref > 0 else 0.0
    corpus_cer = (total_c_dist / total_c_ref) if total_c_ref > 0 else 0.0

    return {
        "num_samples": num_samples,
        "wer": corpus_wer,
        "cer": corpus_cer,
        "wer_breakdown": {
            "total_errors": total_w_dist,
            "substitutions": total_w_s,
            "deletions": total_w_d,
            "insertions": total_w_i,
            "total_ref_words": total_w_ref
        },
        "cer_breakdown": {
            "total_errors": total_c_dist,
            "substitutions": total_c_s,
            "deletions": total_c_d,
            "insertions": total_c_i,
            "total_ref_chars": total_c_ref
        }
    }
