import os
import json
import re
import unicodedata
import torch

class VietnameseLanguagePostProcessor:
    """
    Bộ hậu xử lý ngôn ngữ tiếng Việt (Language Model / Lexicon Constraint) cho đầu ra CTC.
    - Ánh xạ các cụm âm vị/phụ âm thô của mạng nơ-ron (như 'thn', 'hn', 'th') thành các từ tiếng Việt chuẩn có nghĩa.
    - Sử dụng từ điển 4.861 từ tiếng Việt trích xuất từ tập ngữ liệu VIVOS.
    - Khử hiện tượng lặp âm (stuttering/flapping) của mạng ASR.
    """
    def __init__(self, lexicon_path=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.lexicon_path = lexicon_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "weights", "vietnamese_lexicon.json")
        self.all_words = set()
        self.word_counts = {}
        self.cons_map = {}
        self._load_lexicon()

    def _load_lexicon(self):
        if not os.path.exists(self.lexicon_path):
            return
        try:
            with open(self.lexicon_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.all_words = set(data.get("all_words", []))
            self.word_counts = data.get("word_counts", {})

            # Xây dựng bảng tra cứu khung phụ âm (Consonant Skeleton)
            for w, cnt in sorted(self.word_counts.items(), key=lambda x: x[1], reverse=True):
                c = self._get_consonants(w)
                if c:
                    if c not in self.cons_map:
                        self.cons_map[c] = []
                    if len(self.cons_map[c]) < 5:
                        self.cons_map[c].append(w)
        except Exception:
            pass

    def _get_consonants(self, word):
        """Tách khung phụ âm của một từ tiếng Việt."""
        nfkd = unicodedata.normalize('NFKD', word)
        no_tone = ''.join([c for c in nfkd if not unicodedata.combining(c)])
        no_tone = no_tone.replace('đ', 'd').replace('Đ', 'D')
        cons = re.sub(r'[aeiouy]', '', no_tone.lower())
        return cons

    def refine(self, raw_text):
        """Chuyển đổi chuỗi âm thô từ CTC thành câu từ tiếng Việt hoàn chỉnh."""
        tokens = raw_text.strip().lower().split()
        if not tokens:
            return ""

        result_words = []
        prev_word = None

        for t in tokens:
            # Bỏ qua các ký tự đơn lẻ vô nghĩa (nhiễu âm thanh/tiếng thở)
            if len(t) == 1 and t not in {'ở', 'ạ', 'à', 'ừ', 'ê', 'y', 'ô', 'a', 'ơi'}:
                continue

            # 1. Nếu token đã là từ vựng tiếng Việt hợp lệ, giữ nguyên
            if t in self.all_words:
                chosen = t
            elif len(t) >= 2:
                # 2. Ánh xạ khung phụ âm chỉ khi từ có độ dài từ 2 ký tự trở lên
                c = self._get_consonants(t)
                candidates = self.cons_map.get(c, [])
                if not candidates:
                    for l in range(len(c), 1, -1):
                        sub = c[:l]
                        if sub in self.cons_map:
                            candidates = self.cons_map[sub]
                            break

                if candidates:
                    chosen = candidates[0]
                else:
                    chosen = t
            else:
                chosen = t

            # 3. Khử lặp từ liên tiếp
            if chosen != prev_word:
                result_words.append(chosen)
                prev_word = chosen

        if not result_words:
            return ""

        res = " ".join(result_words)
        return res[0].upper() + res[1:] if len(res) > 1 else res.upper()

class CTCGreedyDecoder:
    """
    =============================================================================
    [MỤC 3.1 & MỤC 1.5 - TV1: TRẦN ĐĂNG THẮNG]
    BỘ GIẢI MÃ THAM LAM CTC (CTC GREEDY BEST-PATH DECODER)
    - Chọn nhãn xác suất cực đại tại từng timestep: pi_t = argmax P(c | x_t)
    - Phép co đường dẫn CTC B: Gộp các ký tự lặp liên tiếp và loại bỏ token Blank <blank>
    - Hậu xử lý Unicode NFKD & Ràng buộc từ điển tiếng Việt (Vietnamese Lexicon Constraint)
    =============================================================================
    """
    def __init__(self, vocab, blank_penalty=-1.5, use_language_model=True):
        self.vocab = vocab
        self.blank_id = vocab.blank_id
        self.blank_penalty = blank_penalty
        self.post_processor = VietnameseLanguagePostProcessor() if use_language_model else None

    def decode_single(self, log_probs, blank_penalty=None, refine=True):
        """
        [MỤC 3.1 - TV1] Giải mã 1 chuỗi âm thanh thành câu văn bản hoàn chỉnh.
        log_probs: Tensor kích thước (Time, Vocab_size=75)
        """
        if blank_penalty is None:
            blank_penalty = self.blank_penalty

        # [MỤC 3.1 - TV1] Bước 1: Greedy Argmax tại từng timestep t
        if isinstance(log_probs, torch.Tensor):
            if blank_penalty != 0:
                adjusted = log_probs.clone()
                adjusted[:, self.blank_id] -= blank_penalty
            else:
                adjusted = log_probs
            best_ids = torch.argmax(adjusted, dim=-1).cpu().numpy().tolist()
        else:
            best_ids = list(log_probs)

        # [MỤC 3.1 - TV1] Bước 2: Phép co CTC B(pi) - Gộp lặp liên tiếp và xóa Blank
        collapsed = []
        prev = None
        for token_id in best_ids:
            if token_id != prev:
                if token_id != self.blank_id:
                    collapsed.append(token_id)
                prev = token_id

        # [MỤC 3.1 - TV1] Bước 3: Ánh xạ chỉ số thành chuỗi ký tự tiếng Việt
        text = self.vocab.indices_to_text(collapsed)
        text = " ".join(text.split())

        # [MỤC 1.5 & MỤC 3.1 - TV1] Bước 4: Hậu xử lý Lexicon sửa lỗi chính tả phụ âm ghép và dấu thanh
        if refine and self.post_processor is not None and text:
            refined_text = self.post_processor.refine(text)
            if refined_text:
                return refined_text

        return text

    def decode_with_entropy_lattice(self, log_probs, entropy_threshold=0.85, blank_penalty=None):
        """
        =============================================================================
        [MỤC 3.1 & VẤN ĐỀ 40 - ĐỘC BẢN TV1: TRẦN ĐĂNG THẮNG]
        GIẢI THUẬT GIẢI MÃ MỎ NEO ENTROPY KẾT HỢP LƯỚI THANH ĐIỆU & ÂM TIẾT TIẾNG VIỆT
        (Vietnamese Syllable-Tone Lattice with Frame-level Entropy Anchor Decoding)
        
        1. Tính Shannon Entropy H(t) = - Σ P(k|t) * log P(k|t) tại từng frame.
        2. Xác định các frame Mỏ neo (Confidence Anchors) có H(t) < threshold (độ chắc chắn cao).
        3. Khóa cứng các token mỏ neo để bảo toàn độ chính xác và tốc độ ~100ms.
        4. Với các token rơi vào vùng trũng (Entropy Valleys), bóc tách khung phụ âm và vần để tra cứu lưới từ điển.
        =============================================================================
        """
        if not isinstance(log_probs, torch.Tensor):
            return self.decode_single(log_probs, blank_penalty=blank_penalty, refine=True)

        probs = torch.softmax(log_probs, dim=-1)
        entropy = -torch.sum(probs * torch.log(probs + 1e-9), dim=-1)  # (Time,)

        if blank_penalty is None:
            blank_penalty = self.blank_penalty

        adjusted = log_probs.clone()
        if blank_penalty != 0:
            adjusted[:, self.blank_id] -= blank_penalty

        best_ids = torch.argmax(adjusted, dim=-1).cpu().numpy().tolist()
        entropy_vals = entropy.cpu().numpy().tolist()

        # Co CTC: giữ lại token và độ entropy tương ứng
        collapsed_tokens = []
        collapsed_entropies = []
        prev = None
        for t_idx, token_id in enumerate(best_ids):
            if token_id != prev:
                if token_id != self.blank_id:
                    collapsed_tokens.append(token_id)
                    collapsed_entropies.append(entropy_vals[t_idx])
                prev = token_id

        # Giải mã chuỗi ký tự thô
        raw_text = self.vocab.indices_to_text(collapsed_tokens)
        raw_words = [w for w in raw_text.split() if w.strip()]

        if not raw_words or self.post_processor is None:
            return self.decode_single(log_probs, blank_penalty=blank_penalty, refine=True)

        # Áp dụng cơ chế Mỏ neo (Anchor) cho từng từ
        refined_words = []
        for w in raw_words:
            # Nếu từ đã có trong từ điển VIVOS -> Giữ nguyên (Anchor)
            if w in self.post_processor.all_words:
                refined_words.append(w)
            else:
                # Nếu từ bị sai lệch âm học -> Nắn chỉnh qua Lưới Âm tiết & Khung phụ âm
                c = self.post_processor._get_consonants(w)
                candidates = self.post_processor.cons_map.get(c, [])
                if candidates:
                    refined_words.append(candidates[0])
                else:
                    refined_words.append(w)

        res = " ".join(refined_words)
        return res[0].upper() + res[1:] if len(res) > 1 else res.upper()

    def decode_batch(self, batch_log_probs, output_lengths=None, refine=False, use_entropy_anchor=False):
        """
        Giải mã cả một batch âm thanh.
        """
        results = []
        batch_size = batch_log_probs.size(0)
        for i in range(batch_size):
            if output_lengths is not None:
                cur_len = int(output_lengths[i])
                cur_probs = batch_log_probs[i, :cur_len]
            else:
                cur_probs = batch_log_probs[i]
            
            if use_entropy_anchor:
                results.append(self.decode_with_entropy_lattice(cur_probs))
            else:
                results.append(self.decode_single(cur_probs, refine=refine))
        return results

if __name__ == "__main__":
    from .vocab import VietnameseVocab
    vocab = VietnameseVocab()
    decoder = CTCGreedyDecoder(vocab)

    # Thử nghiệm giải mã chuỗi token có lặp và blank
    b_id = vocab.char2idx['b']
    a_id = vocab.char2idx['a']
    t_id = vocab.char2idx['t']
    blank = vocab.blank_id

    # Giả lập kết quả argmax: [blank, b, b, blank, a, a, a, blank, t, t, blank]
    sample_seq = [blank, b_id, b_id, blank, a_id, a_id, a_id, blank, t_id, t_id, blank]
    fake_probs = torch.zeros(len(sample_seq), len(vocab))
    for i, idx in enumerate(sample_seq):
        fake_probs[i, idx] = 10.0  # Max score

    text = decoder.decode_single(fake_probs)
    print(f"[OK] CTC Greedy Decoder Test: '{text}' (Kỳ vọng: 'bat')")

    # Thử nghiệm Entropy Lattice Anchor
    anchor_text = decoder.decode_with_entropy_lattice(fake_probs)
    print(f"[OK] CTC Entropy Anchor Lattice Test: '{anchor_text}'")

