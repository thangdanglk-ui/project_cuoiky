import json
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Danh sách đầy đủ bảng chữ cái tiếng Việt cho bài toán CTC ASR
# Token 0 LUÔN LUÔN là <blank> theo chuẩn PyTorch CTCLoss
BLANK_TOKEN = "<blank>"
SPACE_TOKEN = " "

BASE_CHARS = [
    BLANK_TOKEN,
    SPACE_TOKEN,
    # Chữ cái Latin cơ bản
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    # Chữ đ
    'đ',
    # Nguyên âm có dấu tiếng Việt
    'à', 'á', 'ả', 'ã', 'ạ',
    'ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ',
    'â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ',
    'è', 'é', 'ẻ', 'ẽ', 'ẹ',
    'ê', 'ề', 'ế', 'ể', 'ễ', 'ệ',
    'ì', 'í', 'ỉ', 'ĩ', 'ị',
    'ò', 'ó', 'ỏ', 'õ', 'ọ',
    'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ',
    'ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ',
    'ù', 'ú', 'ủ', 'ũ', 'ụ',
    'ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự',
    'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ',
    # Chữ số nếu có
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
]

class VietnameseVocab:
    def __init__(self, char_list=None):
        if char_list is None:
            self.chars = list(BASE_CHARS)
        else:
            self.chars = list(char_list)
            if BLANK_TOKEN not in self.chars:
                self.chars.insert(0, BLANK_TOKEN)
            if SPACE_TOKEN not in self.chars:
                self.chars.insert(1, SPACE_TOKEN)

        self.char2idx = {c: i for i, c in enumerate(self.chars)}
        self.idx2char = {i: c for i, c in enumerate(self.chars)}
        self.blank_id = self.char2idx[BLANK_TOKEN]
        self.space_id = self.char2idx[SPACE_TOKEN]

    def __len__(self):
        return len(self.chars)

    def text_to_indices(self, text):
        """Chuyển chuỗi văn bản thành danh sách chỉ số (indices)."""
        text = text.strip().lower()
        indices = []
        for char in text:
            if char in self.char2idx:
                indices.append(self.char2idx[char])
            elif char == '\t' or char == '\n':
                indices.append(self.space_id)
            # Bỏ qua các ký tự lạ hoặc dấu chấm câu đặc biệt
        return indices

    def indices_to_text(self, indices):
        """Chuyển danh sách chỉ số thành chuỗi văn bản."""
        chars = []
        for idx in indices:
            if idx in self.idx2char:
                c = self.idx2char[idx]
                if c != BLANK_TOKEN:
                    chars.append(c)
        return "".join(chars)

    def save(self, filepath):
        """Lưu từ điển ra tệp json."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.chars, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath):
        """Nạp từ điển từ tệp json."""
        with open(filepath, "r", encoding="utf-8") as f:
            chars = json.load(f)
        return cls(chars)

if __name__ == "__main__":
    vocab = VietnameseVocab()
    print("[OK] Khởi tạo Từ điển Ký tự Tiếng Việt thành công!")
    print(f"[Vocab] Tổng số token (Vocab Size): {len(vocab)}")
    print(f"[Vocab] Token blank ID: {vocab.blank_id}")
    sample_text = "xin chào việt nam"
    encoded = vocab.text_to_indices(sample_text)
    decoded = vocab.indices_to_text(encoded)
    print(f"Mẫu: '{sample_text}' -> Encoded: {encoded} -> Decoded: '{decoded}'")
