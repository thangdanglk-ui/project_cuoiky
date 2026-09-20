import os
import sys
import threading

# Đảm bảo python luôn tìm thấy các module nội bộ bất kể được khởi chạy từ đâu
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import customtkinter as ctk
from controllers.audio_controller import (
    AudioEngine,
    AudioController,
    AUDIO_MODES,
    MODE_LAPTOP_MIC,
    MODE_HEADSET_MIC,
    MODE_FILE
)
from tkinter import filedialog
from views.visualizer_view import SignalVisualizerWindow, VisualizerWindow


# Cấu hình giao diện tối hiện đại
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SpeechAIGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HỆ THỐNG NHẬN DẠNG TIẾNG NÓI AI (ASR PIPELINE)")
        self.geometry("980x670")
        self.minsize(880, 600)

        # Khởi tạo engine xử lý âm thanh (Backend)
        self.engine = AudioEngine(
            model_size="small",
            on_model_status_change=self.on_model_status_update
        )

        # Quản lý cửa sổ phân tích biểu đồ tín hiệu
        self.visualizer_window = None

        # Tự động ánh xạ mỗi chế độ với 1 thiết bị chuẩn duy nhất
        self.mode_device_map = self.engine.get_mode_device_mapping()
        self.all_input_devices = self.engine.get_all_input_devices()
        self.current_mode = AUDIO_MODES[0]
        self.current_device_index, self.current_device_name = self.mode_device_map[self.current_mode]

        self._build_ui()
        self._update_device_info(self.current_mode)

    def on_model_status_update(self, message, color):
        """Callback khi trạng thái mô hình AI thay đổi."""
        self.after(0, lambda: self.lbl_status.configure(text=message, text_color=color))

    def _build_ui(self):
        # ---------------- TIÊU ĐỀ ----------------
        self.lbl_title = ctk.CTkLabel(
            self,
            text="HỆ THỐNG XỬ LÝ TIẾNG NÓI & NHẬN DẠNG AI",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00FFFF"
        )
        self.lbl_title.pack(pady=(10, 2))

        theory_banner = "Pipeline: Sóng âm -> Lấy mẫu (16kHz) -> Lọc VAD -> Đặc trưng MFCC -> Mạng nơ-ron CRNN -> gTTS"
        self.lbl_theory = ctk.CTkLabel(
            self,
            text=theory_banner,
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#39FF14"
        )
        self.lbl_theory.pack(pady=(0, 4))

        # Khung trạng thái mô hình và nút Retry
        self.frame_model_status = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_model_status.pack(pady=(0, 6))

        self.lbl_status = ctk.CTkLabel(
            self.frame_model_status,
            text=self.engine.model_status,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFA500"
        )
        self.lbl_status.pack(side="left", padx=8)

        self.btn_retry_model = ctk.CTkButton(
            self.frame_model_status,
            text="🔄 Nạp lại Model",
            width=110,
            height=24,
            command=self.retry_load_model,
            fg_color="#4A4A4A",
            hover_color="#616161",
            font=ctk.CTkFont(size=11)
        )
        self.btn_retry_model.pack(side="left", padx=5)

        # =========================================================================
        # KHU VỰC 1: SPEECH TO TEXT (THU ÂM 1 CHẠM THEO CHẾ ĐỘ)
        # =========================================================================
        self.frame_stt = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color="#18191A",
            border_width=2,
            border_color="#00BFFF"
        )
        self.frame_stt.pack(padx=15, pady=4, fill="x")

        self.lbl_stt_title = ctk.CTkLabel(
            self.frame_stt,
            text="1. BỘ THU ÂM & NHẬN DẠNG GIỌNG NÓI (SPEECH-TO-TEXT)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00E5FF"
        )
        self.lbl_stt_title.pack(pady=(6, 4))

        # Thanh chọn 4 chế độ âm thanh
        self.seg_mode = ctk.CTkSegmentedButton(
            self.frame_stt,
            values=AUDIO_MODES,
            command=self.on_mode_change,
            selected_color="#1E90FF",
            selected_hover_color="#0066CC",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.seg_mode.set(AUDIO_MODES[0])
        self.seg_mode.pack(padx=15, pady=(0, 4), fill="x")

        # Hàng chứa thông tin thiết bị kết nối & Checkbox VAD
        self.frame_dev_badge = ctk.CTkFrame(self.frame_stt, fg_color="transparent")
        self.frame_dev_badge.pack(padx=15, pady=(0, 4), fill="x")

        self.lbl_dev_title = ctk.CTkLabel(
            self.frame_dev_badge,
            text="🔌 Thiết bị thu:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#00FFAA"
        )
        self.lbl_dev_title.pack(side="left", padx=(5, 2))

        dev_values = [d[1] for d in self.all_input_devices] if self.all_input_devices else ["Không có thiết bị"]
        self.opt_devices = ctk.CTkOptionMenu(
            self.frame_dev_badge,
            values=dev_values,
            command=self.on_device_selected,
            width=360,
            height=26,
            font=ctk.CTkFont(size=11)
        )
        self.opt_devices.pack(side="left", padx=5)

        self.btn_refresh_dev = ctk.CTkButton(
            self.frame_dev_badge,
            text="🔄",
            width=28,
            height=26,
            command=self.refresh_devices,
            fg_color="#333333",
            hover_color="#555555"
        )
        self.btn_refresh_dev.pack(side="left", padx=2)

        # Checkbox VAD
        self.use_vad = ctk.BooleanVar(value=True)
        self.chk_vad = ctk.CTkCheckBox(
            self.frame_dev_badge,
            text="Màng lọc VAD (Lọc khoảng lặng & ồn)",
            variable=self.use_vad,
            font=ctk.CTkFont(size=11)
        )
        self.chk_vad.pack(side="right", padx=10)

        # Hàng chọn Động cơ AI Nhận dạng (ASR Engine Selector)
        self.frame_engine = ctk.CTkFrame(self.frame_stt, fg_color="transparent")
        self.frame_engine.pack(padx=15, pady=(0, 4), fill="x")

        self.lbl_engine_title = ctk.CTkLabel(
            self.frame_engine,
            text="🧠 Động cơ AI:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#FF9100"
        )
        self.lbl_engine_title.pack(side="left", padx=(5, 4))

        self.seg_engine = ctk.CTkSegmentedButton(
            self.frame_engine,
            values=[
                "🧠 CRNN-CTC",
                "⚡ Wav2Vec2-CTC (Nâng cao)",
                "⚖️ So sánh cả 2 mô hình"
            ],
            command=self.on_engine_change,
            selected_color="#E65100",
            selected_hover_color="#BF360C",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.seg_engine.set("🧠 CRNN-CTC")
        self.seg_engine.pack(side="left", padx=5, fill="x", expand=True)

        # Hàng nút Bắt đầu thu âm + NÚT MỞ CỬA SỔ PHÂN TÍCH TÍN HIỆU
        self.frame_rec_action = ctk.CTkFrame(self.frame_stt, fg_color="transparent")
        self.frame_rec_action.pack(pady=(2, 6))

        self.btn_record = ctk.CTkButton(
            self.frame_rec_action,
            text="🎙️ Bắt đầu Thu âm",
            command=self.toggle_recording,
            fg_color="#E50914",
            hover_color="#B20710",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=34,
            width=200
        )
        self.btn_record.pack(side="left", padx=(5, 8))

        # NÚT PHÁT LẠI ÂM THANH (CHO FILE HOẶC BẢN THU TỪ MIC)
        self.btn_play_audio = ctk.CTkButton(
            self.frame_rec_action,
            text="🔊 Nghe lại",
            command=self.play_current_audio,
            fg_color="#1E88E5",
            hover_color="#1565C0",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=34,
            width=110
        )
        self.btn_play_audio.pack(side="left", padx=5)

        # NÚT MỞ/TẮT CỬA SỔ BIỂU ĐỒ TÍN HIỆU
        self.btn_visualize = ctk.CTkButton(
            self.frame_rec_action,
            text="📊 Biểu đồ Tín hiệu (Waveform & Phổ)",
            command=self.toggle_visualizer_window,
            fg_color="#20B2AA",
            hover_color="#008B8B",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=34,
            width=230
        )
        self.btn_visualize.pack(side="left", padx=8)

        self.lbl_record_state = ctk.CTkLabel(
            self.frame_rec_action,
            text="[Sẵn sàng thu âm]",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#A9A9A9"
        )
        self.lbl_record_state.pack(side="left", padx=5)

        # =========================================================================
        # KHU VỰC 2: VÙNG VĂN BẢN (KẾT QUẢ NHẬN DẠNG ASR & SOẠN THẢO)
        # =========================================================================
        self.frame_bottom = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color="#18191A",
            border_width=2,
            border_color="#9932CC"
        )
        self.frame_bottom.pack(padx=15, pady=(4, 10), fill="both", expand=True)

        self.lbl_bottom_title = ctk.CTkLabel(
            self.frame_bottom,
            text="2. KẾT QUẢ NHẬN DẠNG VĂN BẢN (STT):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#DA70D6"
        )
        self.lbl_bottom_title.pack(anchor="w", padx=15, pady=(8, 2))

        # HÀNG NÚT THAO TÁC ĐẶT TRÊN Ô TEXT
        self.frame_tts_actions = ctk.CTkFrame(self.frame_bottom, fg_color="#232425", corner_radius=8)
        self.frame_tts_actions.pack(padx=15, pady=(4, 6), fill="x")

        # Nút reset xóa trắng ô text
        self.btn_reset = ctk.CTkButton(
            self.frame_tts_actions,
            text="🔄 Reset (Xóa trắng ô text)",
            command=self.reset_content_text,
            fg_color="#E65100",
            hover_color="#BF360C",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=34,
            width=190
        )
        self.btn_reset.pack(side="left", padx=(10, 8), pady=6)

        # Nút sao chép văn bản
        self.btn_copy = ctk.CTkButton(
            self.frame_tts_actions,
            text="📋 Sao chép text",
            command=self.copy_content_text,
            fg_color="#2E8B57",
            hover_color="#1E5C39",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=34,
            width=130
        )
        self.btn_copy.pack(side="left", padx=8, pady=6)

        # Dòng trạng thái phát giọng nói TTS
        self.lbl_tts_status = ctk.CTkLabel(
            self.frame_tts_actions,
            text="",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#00FFAA"
        )
        self.lbl_tts_status.pack(side="left", padx=10, pady=6)

        # HỘP VĂN BẢN (TEXTBOX)
        self.txt_content = ctk.CTkTextbox(
            self.frame_bottom,
            font=ctk.CTkFont(size=14),
            wrap="word",
            border_width=1,
            border_color="#3A3B3C"
        )
        self.txt_content.pack(padx=15, pady=(0, 10), fill="both", expand=True)
        self.txt_content.insert(
            "0.0",
            "Xin chào! Khi bạn thu âm bằng 1 trong 4 chế độ ở trên, văn bản nhận diện sẽ tự động xuất hiện tại đây.\n\n"
            "• Bạn có thể TỰ DO GÕ / SỬA / VIẾT THÊM chữ vào ô này bất kỳ lúc nào.\n"
            "• Nhấn nút [🔊 Chuyển text thành âm thanh (AI đọc)] ở trên để nghe giọng đọc AI.\n"
            "• Nhấn nút [🔄 Reset (Xóa trắng ô text)] ở trên để làm trống ô này và viết nội dung mới.\n"
            "• Bấm nút [📊 Biểu đồ Tín hiệu] ở trên để mở cửa sổ xem Waveform, Spectrogram và STE chạy thời gian thực!"
        )

    # ---------------- QUẢN LÝ CỬA SỔ PHÂN TÍCH TÍN HIỆU (TOPLEVEL) ----------------
    def toggle_visualizer_window(self):
        """Bật / tắt hoặc kích hoạt cửa sổ phân tích tín hiệu âm thanh."""
        if self.visualizer_window is None or not self.visualizer_window.winfo_exists():
            self.visualizer_window = SignalVisualizerWindow(self, self.engine)
        else:
            self.visualizer_window.lift()
            self.visualizer_window.focus()
            if self.engine.is_recording:
                self.visualizer_window.start_live_updates()
            elif self.engine.last_recorded_audio is not None:
                self.visualizer_window.render_full_analysis()
            else:
                self.visualizer_window.clear_plots()

    # ---------------- QUẢN LÝ CHẾ ĐỘ & THIẾT BỊ ----------------
    def retry_load_model(self):
        """Thử nạp lại mô hình AI Tự Huấn Luyện nếu cần."""
        self.engine.custom_classifier._load_model()
        if self.engine.is_model_ready():
            self.lbl_status.configure(text=self.engine.model_status, text_color="#00FF00")
        else:
            self.lbl_status.configure(text=self.engine.model_status, text_color="#FFA500")

    def on_mode_change(self, selected_mode):
        self.current_mode = selected_mode
        if selected_mode == MODE_FILE:
            self.lbl_dev_title.configure(text="📁 Nguồn File: [Bấm nút bên dưới để chọn file âm thanh chuẩn]")
            self.opt_devices.pack_forget()
            self.btn_refresh_dev.pack_forget()
            self.btn_record.configure(
                text="📁 Chọn File Âm Thanh & Nhận Dạng",
                fg_color="#007ACC",
                hover_color="#005999",
                command=self.choose_and_recognize_file
            )
            self.lbl_record_state.configure(text="[Sẵn sàng nạp file âm thanh .wav]", text_color="#00FFAA")
        else:
            self.lbl_dev_title.configure(text="🔌 Thiết bị thu:")
            self.opt_devices.pack(side="left", padx=5)
            self.btn_refresh_dev.pack(side="left", padx=2)
            self.btn_record.configure(
                text="🎙️ Bắt đầu Thu âm",
                fg_color="#E50914",
                hover_color="#B20710",
                command=self.toggle_recording
            )
            self.mode_device_map = self.engine.get_mode_device_mapping()
            self._update_device_info(selected_mode)

            if selected_mode == MODE_LAPTOP_MIC:
                self.lbl_record_state.configure(text="[Đang dùng Micro Laptop - Hãy nói to rõ, cách màn hình ~15cm]", text_color="#00FFAA")
            else:
                self.lbl_record_state.configure(text="[Đang dùng Micro Tai phone - Hãy nói vào đầu thu mic trên tai nghe]", text_color="#00E5FF")

    def _update_device_info(self, mode):
        """Cập nhật thiết bị tối ưu được gán sẵn cho chế độ đã chọn lên Dropdown."""
        dev_info = self.mode_device_map.get(mode)
        if dev_info:
            self.current_device_index, self.current_device_name = dev_info
            for opt in self.opt_devices._values:
                if (mode == MODE_LAPTOP_MIC and "Laptop" in opt) or (mode == MODE_HEADSET_MIC and "Tai phone" in opt):
                    self.opt_devices.set(opt)
                    break
        else:
            self.current_device_index = None

    def on_device_selected(self, selected_text):
        """Khi người dùng chủ động chọn thiết bị khác từ dropdown."""
        try:
            idx_str = selected_text.split(']')[0].replace('[', '').split()[-1].strip()
            self.current_device_index = int(idx_str)
            self.current_device_name = selected_text

            if "Laptop" in selected_text:
                self.current_mode = MODE_LAPTOP_MIC
                self.seg_mode.set(MODE_LAPTOP_MIC)
                self.lbl_record_state.configure(text="[Đang dùng Micro Laptop - Hãy nói to rõ, cách màn hình ~15cm]", text_color="#00FFAA")
            elif "Tai phone" in selected_text:
                self.current_mode = MODE_HEADSET_MIC
                self.seg_mode.set(MODE_HEADSET_MIC)
                self.lbl_record_state.configure(text="[Đang dùng Micro Tai phone - Hãy nói vào đầu thu mic trên tai nghe]", text_color="#00E5FF")
        except Exception:
            pass

    def refresh_devices(self):
        """Quét lại toàn bộ danh sách thiết bị khi vừa cắm hoặc rút tai nghe."""
        self.all_input_devices = self.engine.get_all_input_devices()
        dev_values = [d[1] for d in self.all_input_devices] if self.all_input_devices else ["Không có thiết bị"]
        self.opt_devices.configure(values=dev_values)
        self.mode_device_map = self.engine.get_mode_device_mapping()
        self._update_device_info(self.current_mode)

    def on_engine_change(self, selected_label):
        """Khi người dùng chuyển đổi giữa CRNN-CTC, Wav2Vec2 hoặc chế độ So sánh."""
        if "CRNN" in selected_label:
            engine = "crnn"
            self.lbl_record_state.configure(text="[Đã chọn: CRNN-CTC]", text_color="#00FFAA")
        elif "So sánh" in selected_label:
            engine = "both"
            self.lbl_record_state.configure(text="[Đã chọn: Chế độ So sánh Đối chiếu cả 2 mô hình]", text_color="#FFD700")
        else:
            engine = "wav2vec2"
            self.lbl_record_state.configure(text="[Đã chọn: Wav2Vec2-CTC Nâng cao (250h)]", text_color="#00E5FF")
        self.engine.set_asr_engine(engine)

    # ---------------- THAO TÁC THU ÂM & DỊCH (STT) ----------------
    def toggle_recording(self):
        if not self.engine.is_model_ready():
            self.lbl_record_state.configure(
                text="⚠️ Vui lòng chờ mô hình AI nạp xong (hoặc bấm 'Nạp lại Model' ở trên)!",
                text_color="#FF4500"
            )
            return

        if not self.engine.is_recording:
            # Luôn đọc chính xác thiết bị đang hiển thị trên dropdown
            try:
                selected_dev = self.opt_devices.get()
                self.current_device_index = int(selected_dev.split(']')[0].replace('[', '').strip())
            except Exception:
                pass

            if self.current_device_index is None:
                self.lbl_record_state.configure(
                    text="❌ Lỗi: Chưa tìm thấy thiết bị âm thanh phù hợp!",
                    text_color="#FF4500"
                )
                return

            self.engine.stop_audio_playback()
            success, msg = self.engine.start_recording(self.current_device_index)
            if not success:
                self.lbl_record_state.configure(text=f"❌ {msg}", text_color="#FF4500")
                return

            self.btn_record.configure(text="🛑 Dừng Thu âm & Dịch", fg_color="#FF4500")
            self.lbl_record_state.configure(
                text=f"🎙️ Đang thu âm... Hãy nói hoặc phát âm thanh",
                text_color="#00FF7F"
            )

            # BẬT CHẾ ĐỘ CẬP NHẬT REALTIME TRÊN CỬA SỔ BIỂU ĐỒ NẾU ĐANG MỞ
            if self.visualizer_window and self.visualizer_window.winfo_exists():
                self.visualizer_window.start_live_updates()

            threading.Thread(target=self._record_worker, daemon=True).start()

        else:
            selected_engine = self.seg_engine.get() if hasattr(self, 'seg_engine') else ""
            if "CRNN" in selected_engine:
                engine_msg = "[Đang nhận dạng bằng Mạng Nơ-ron CRNN-CTC Tự làm (Slide 2b)...]"
            elif "So sánh" in selected_engine:
                engine_msg = "[Đang chạy đối chiếu song song cả 2 mô hình CRNN & Wav2Vec2...]"
            else:
                engine_msg = "[Đang nhận dạng bằng Mạng Wav2Vec2-CTC Nâng cao...]"

            self.btn_record.configure(state="disabled", text="⏳ Đang xử lý AI...", fg_color="#696969")
            self.lbl_record_state.configure(text=engine_msg, text_color="#FFA500")
            self.engine.is_recording = False

    def _record_worker(self):
        self.engine.record_loop()
        audio_np = self.engine.stop_recording()

        if audio_np is None or len(audio_np) == 0:
            self.after(0, lambda: self._on_transcribe_done("⚠️ Không thu được tín hiệu âm thanh nào!"))
            return

        # KHI DỪNG THU ÂM: VẼ ĐẦY ĐỦ TOÀN BỘ 3 ĐỒ THỊ TRÊN CỬA SỔ BIỂU ĐỒ
        if self.visualizer_window and self.visualizer_window.winfo_exists():
            self.after(0, self.visualizer_window.render_full_analysis)

        use_vad = self.use_vad.get()
        try:
            transcription = self.engine.transcribe(audio_np, use_vad=use_vad, language="vi")
            if not transcription:
                if use_vad:
                    msg = "🤫 [Chỉ nghe thấy khoảng lặng hoặc tiếng ồn - VAD đã lọc bỏ]"
                else:
                    msg = "❌ [Không thể nhận dạng câu nói]"
            else:
                msg = transcription
        except Exception as e:
            msg = f"❌ Lỗi nhận dạng AI: {e}"

        self.after(0, lambda: self._on_transcribe_done(msg))

    def _on_transcribe_done(self, text):
        """Hiển thị kết quả ra vùng dưới và phục hồi nút bấm."""
        current_content = self.txt_content.get("0.0", "end").strip()
        
        if "Xin chào! Khi bạn thu âm" in current_content:
            self.txt_content.delete("0.0", "end")
            self.txt_content.insert("0.0", text + "\n")
        else:
            self.txt_content.insert("end", "\n" + text)

        self.txt_content.see("end")
        if self.current_mode in (MODE_LAPTOP_MIC, MODE_HEADSET_MIC):
            self.btn_record.configure(state="normal", text="🎙️ Bắt đầu Thu âm", fg_color="#E50914")
        else:
            self.btn_record.configure(state="normal", text="📁 Chọn File Âm Thanh & Nhận Dạng", fg_color="#007ACC")
        self.lbl_record_state.configure(text="[Hoàn thành! Bạn có thể xem biểu đồ hoặc nghe lại]", text_color="#39FF14")

    # ---------------- THAO TÁC NẠP FILE ÂM THANH TRỰC TIẾP (.WAV) ----------------
    def choose_and_recognize_file(self):
        """Mở hộp thoại chọn file âm thanh chuẩn (.wav, .flac, .mp3) và nhận diện."""
        if not self.engine.is_model_ready():
            self.lbl_record_state.configure(
                text="⚠️ Vui lòng chờ mô hình AI nạp xong trước khi chọn file!",
                text_color="#FF4500"
            )
            return

        initial_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dataset", "vivos", "test", "waves")
        if not os.path.exists(initial_dir):
            initial_dir = os.path.dirname(os.path.abspath(__file__))

        file_path = filedialog.askopenfilename(
            title="Chọn file âm thanh để nhận dạng tiếng nói (Khuyên dùng VIVOS)",
            initialdir=initial_dir,
            filetypes=[
                ("Tệp âm thanh WAV", "*.wav"),
                ("Tệp FLAC", "*.flac"),
                ("Tệp MP3", "*.mp3"),
                ("Tất cả tập tin", "*.*")
            ]
        )

        if not file_path:
            return

        # PHÁT ÂM THANH NGAY LẬP TỨC RA LOA (0ms delay) ĐỂ NGƯỜI NGHE BIẾT FILE NÓI GÌ
        self.engine.play_file(file_path)

        filename = os.path.basename(file_path)
        selected_engine = self.seg_engine.get() if hasattr(self, 'seg_engine') else ""
        if "CRNN" in selected_engine:
            engine_desc = "CRNN-CTC"
        elif "So sánh" in selected_engine:
            engine_desc = "So sánh 2 mô hình"
        else:
            engine_desc = "Wav2Vec2-CTC"

        self.btn_record.configure(state="disabled", text="⏳ Đang giải mã...", fg_color="#696969")
        self.lbl_record_state.configure(text=f"🔊 Đang phát & AI nhận dạng [{filename}]...", text_color="#00FFAA")

        def _worker():
            try:
                audio_np = self.engine.load_audio_file(file_path)

                if self.visualizer_window and self.visualizer_window.winfo_exists():
                    self.after(0, self.visualizer_window.render_full_analysis)

                use_vad = self.use_vad.get()
                transcription = self.engine.transcribe(audio_np, use_vad=use_vad, language="vi")
                msg = f"📁 [File: {filename}]\n{transcription}"
            except Exception as e:
                msg = f"❌ Lỗi nạp/nhận dạng file: {e}"

            self.after(0, lambda: self._on_file_transcribe_done(msg, filename))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_file_transcribe_done(self, text, filename):
        current_content = self.txt_content.get("0.0", "end").strip()
        if "Xin chào! Khi bạn thu âm" in current_content:
            self.txt_content.delete("0.0", "end")
            self.txt_content.insert("0.0", text + "\n")
        else:
            self.txt_content.insert("end", "\n" + text + "\n")

        self.txt_content.see("end")
        self.btn_record.configure(state="normal", text="📁 Chọn File Âm Thanh & Nhận Dạng", fg_color="#007ACC")
        self.lbl_record_state.configure(text=f"[Đã nhận dạng xong: {filename}]", text_color="#39FF14")

    def play_current_audio(self):
        """Phát lại âm thanh vừa nạp từ file hoặc vừa thu từ Micro qua loa máy tính."""
        if self.engine.last_recorded_audio is None or len(self.engine.last_recorded_audio) == 0:
            self.lbl_record_state.configure(text="⚠️ Chưa có âm thanh (hãy thu âm hoặc chọn file trước)!", text_color="#FFA500")
            return

        success, msg = self.engine.play_audio()
        if success:
            self.lbl_record_state.configure(text="🔊 Đang phát âm thanh ra loa...", text_color="#00FFAA")
        else:
            self.lbl_record_state.configure(text=f"❌ {msg}", text_color="#FF4500")

    # ---------------- THAO TÁC VÙNG DƯỚI (RESET & SAO CHÉP VĂN BẢN) ----------------
    def reset_content_text(self):
        """Xóa trắng hoàn toàn ô text khi người dùng muốn làm mới."""
        self.txt_content.delete("0.0", "end")
        self.lbl_tts_status.configure(text="[Đã làm trống ô text!]", text_color="#A9A9A9")

    def copy_content_text(self):
        """Sao chép nội dung vào Clipboard."""
        text = self.txt_content.get("0.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.lbl_tts_status.configure(text="[Đã sao chép vào Clipboard!]", text_color="#00FFFF")

if __name__ == "__main__":
    app = SpeechAIGUI()
    app.mainloop()


def main():
    app = SpeechAIGUI()
    app.mainloop()
