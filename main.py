"""
MAIN ENTRY POINT CHO HỆ THỐNG XỬ LÝ TIẾNG NÓI & NHẬN DẠNG AI (MVC ARCHITECTURE)
Khởi động ứng dụng giao diện chính từ tầng View.
"""
import os
import sys

# Đảm bảo thư mục gốc dự án luôn nằm trong sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from views.main_view import main

if __name__ == "__main__":
    main()
