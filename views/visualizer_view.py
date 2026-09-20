import os
import sys
import customtkinter as ctk
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SignalVisualizerWindow(ctk.CTkToplevel):
    def __init__(self, master, engine):
        super().__init__(master)

        self.engine = engine
        self.title("PHÂN TÍCH TÍN HIỆU ÂM THANH (DSP & SPEECH VISUALIZER)")
        self.geometry("940x740")
        self.minsize(820, 620)

        # Đặt nền tối công nghệ
        self.configure(fg_color="#121212")

        # Biến trạng thái live
        self._is_live_active = False

        self._build_ui()

        # Kiểm tra: nếu đang thu âm thì chạy ngay chế độ realtime, nếu đã có âm thanh cũ thì hiển thị, còn không thì để trống
        if self.engine.is_recording:
            self.start_live_updates()
        elif self.engine.last_recorded_audio is not None:
            self.render_full_analysis()
        else:
            self.clear_plots()

        # Xử lý khi người dùng đóng cửa sổ
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        # ---------------- KHUNG TIÊU ĐỀ & THÔNG SỐ ----------------
        self.frame_top = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=10)
        self.frame_top.pack(padx=15, pady=(10, 4), fill="x")

        self.lbl_header = ctk.CTkLabel(
            self.frame_top,
            text="📊 BIỂU ĐỒ TÍN HIỆU: WAVEFORM - STFT SPECTROGRAM - NĂNG LƯỢNG STE",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00FFFF"
        )
        self.lbl_header.pack(anchor="w", padx=15, pady=(8, 2))

        # Dòng thông số kỹ thuật & Nút làm mới
        self.frame_metrics = ctk.CTkFrame(self.frame_top, fg_color="transparent")
        self.frame_metrics.pack(padx=15, pady=(0, 6), fill="x")

        self.lbl_duration = ctk.CTkLabel(
            self.frame_metrics,
            text="⏱️ Thời lượng: -- s",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFFFFF"
        )
        self.lbl_duration.pack(side="left", padx=(0, 15))

        self.lbl_sr = ctk.CTkLabel(
            self.frame_metrics,
            text="🎚️ Lấy mẫu: 16000 Hz",
            font=ctk.CTkFont(size=12),
            text_color="#AAAAAA"
        )
        self.lbl_sr.pack(side="left", padx=10)

        self.lbl_peak = ctk.CTkLabel(
            self.frame_metrics,
            text="📈 Biên độ đỉnh: --",
            font=ctk.CTkFont(size=12),
            text_color="#AAAAAA"
        )
        self.lbl_peak.pack(side="left", padx=10)

        # Trạng thái phản hồi trực quan
        self.lbl_action_feedback = ctk.CTkLabel(
            self.frame_metrics,
            text="[Sẵn sàng thu âm]",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#00FF7F"
        )
        self.lbl_action_feedback.pack(side="left", padx=15)

        # Nút Làm mới biểu đồ (Click sẽ xóa trắng biểu đồ theo yêu cầu)
        self.btn_refresh = ctk.CTkButton(
            self.frame_metrics,
            text="🔄 Làm mới biểu đồ (Xóa trắng)",
            width=190,
            height=28,
            command=self.clear_plots,
            fg_color="#D2691E",
            hover_color="#A0522D",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.btn_refresh.pack(side="right", padx=5)

        # ---------------- KHUNG CHỨA CANVAS ĐỒ THỊ ----------------
        self.frame_canvas = ctk.CTkFrame(self, fg_color="#18191A", corner_radius=10)
        self.frame_canvas.pack(padx=15, pady=(4, 10), fill="both", expand=True)

        # Khởi tạo Figure Matplotlib nền đen
        self.fig, (self.ax_wave, self.ax_spec, self.ax_ste) = plt.subplots(
            nrows=3,
            ncols=1,
            figsize=(9, 6.2),
            dpi=100,
            sharex=False,
            facecolor="#18191A"
        )
        self.fig.subplots_adjust(left=0.08, right=0.96, top=0.95, bottom=0.08, hspace=0.38)

        for ax in (self.ax_wave, self.ax_spec, self.ax_ste):
            ax.set_facecolor("#121212")
            ax.tick_params(colors="#CCCCCC", labelsize=9)
            for spine in ax.spines.values():
                spine.set_color("#444444")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_canvas)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    # ---------------- YÊU CẦU 3: KHI ẤN "LÀM MỚI BIỂU ĐỒ" THÌ CÁC BIỂU ĐỒ PHẢI TRỐNG ----------------
    def clear_plots(self):
        """Xóa trắng toàn bộ 3 biểu đồ theo đúng yêu cầu của người dùng."""
        self._is_live_active = False
        self.engine.last_recorded_audio = None

        self.lbl_duration.configure(text="⏱️ Thời lượng: 0.00 s")
        self.lbl_peak.configure(text="📈 Biên độ đỉnh: 0.000")
        self.lbl_action_feedback.configure(
            text="[Đã làm mới: Biểu đồ hiện đang trống, sẵn sàng thu âm mới!]",
            text_color="#00FFAA"
        )

        for ax in (self.ax_wave, self.ax_spec, self.ax_ste):
            ax.clear()
            ax.set_facecolor("#121212")
            ax.tick_params(colors="#CCCCCC", labelsize=9)
            for spine in ax.spines.values():
                spine.set_color("#444444")

        # 1. Trục Waveform trống
        self.ax_wave.set_title("1. Dạng sóng thời gian (Waveform - Trống, bấm 'Bắt đầu Thu âm' để chạy)", color="#00FFFF", fontsize=10, weight="bold")
        self.ax_wave.set_ylabel("Biên độ", color="#CCCCCC", fontsize=9)
        self.ax_wave.set_ylim(-1.05, 1.05)
        self.ax_wave.set_xlim(0, 5)
        self.ax_wave.grid(True, linestyle="--", alpha=0.2, color="#555555")

        # 2. Trục Spectrogram trống
        self.ax_spec.set_title("2. Phổ tần số thời gian thực STFT Spectrogram (Trống)", color="#FF8C00", fontsize=10, weight="bold")
        self.ax_spec.set_ylabel("Tần số (Hz)", color="#CCCCCC", fontsize=9)
        self.ax_spec.set_ylim(0, 8000)
        self.ax_spec.set_xlim(0, 5)
        self.ax_spec.grid(True, linestyle="--", alpha=0.2, color="#555555")

        # 3. Trục STE trống
        self.ax_ste.set_title("3. Năng lượng ngắn hạn (STE) & Phân vùng VAD (Trống)", color="#39FF14", fontsize=10, weight="bold")
        self.ax_ste.set_xlabel("Thời gian (giây)", color="#CCCCCC", fontsize=9)
        self.ax_ste.set_ylabel("Mức năng lượng", color="#CCCCCC", fontsize=9)
        self.ax_ste.set_ylim(-0.05, 1.1)
        self.ax_ste.set_xlim(0, 5)
        self.ax_ste.grid(True, linestyle="--", alpha=0.2, color="#555555")

        self.canvas.draw()
        self.canvas.flush_events()

    # ---------------- YÊU CẦU 1: THAY ĐỔI THEO THỜI GIAN THỰC (REALTIME) KHI THU ÂM ----------------
    def start_live_updates(self):
        """Bắt đầu vòng lặp cập nhật biểu đồ thời gian thực khi bấm thu âm."""
        self._is_live_active = True
        self.lbl_action_feedback.configure(
            text="🔴 Đang thu âm... 3 biểu đồ đang chạy thời gian thực!",
            text_color="#FF3333"
        )
        self._live_tick()

    def _live_tick(self):
        """Vòng lặp lấy audio realtime từ microphone và cập nhật 3 biểu đồ."""
        if not self.winfo_exists() or not self._is_live_active:
            return

        if self.engine.is_recording:
            live_audio = self.engine.get_current_live_audio()
            if live_audio is not None and len(live_audio) >= 512:
                self._draw_live_graphs(live_audio)

            # Lên lịch cập nhật khung tiếp theo sau 120ms
            self.after(120, self._live_tick)
        else:
            self._is_live_active = False

    def _draw_live_graphs(self, live_audio):
        """Vẽ nhanh 3 biểu đồ từ luồng âm thanh thời gian thực."""
        data = self.engine.compute_signal_analysis(live_audio, fast_mode=True)
        if data is None:
            return

        self.lbl_duration.configure(text=f"⏱️ Đang thu: {data['duration']:.2f} s")
        self.lbl_peak.configure(text=f"📈 Biên độ: {data['max_amplitude']:.3f}")

        t_wave = data["t_wave"]
        waveform = data["waveform"]

        # 1. Waveform realtime
        self.ax_wave.clear()
        self.ax_wave.set_facecolor("#121212")
        self.ax_wave.plot(t_wave, waveform, color="#00FFFF", linewidth=1.0)
        self.ax_wave.set_title(f"1. Dạng sóng thời gian thực (Waveform Live - {data['duration']:.2f}s)", color="#00FFFF", fontsize=10, weight="bold")
        self.ax_wave.set_ylabel("Biên độ", color="#CCCCCC", fontsize=9)
        self.ax_wave.set_ylim(-1.05, 1.05)
        self.ax_wave.tick_params(colors="#CCCCCC", labelsize=9)
        self.ax_wave.grid(True, linestyle="--", alpha=0.3, color="#555555")

        # 2. Spectrogram realtime
        self.ax_spec.clear()
        self.ax_spec.set_facecolor("#121212")
        self.ax_spec.pcolormesh(
            data["t_spec"], data["freqs"], data["spectrogram_db"],
            shading='gouraud', cmap='inferno', vmin=-60, vmax=0
        )
        self.ax_spec.set_title("2. Phổ tần số thời gian thực (STFT Spectrogram Live - 0-8000 Hz)", color="#FF8C00", fontsize=10, weight="bold")
        self.ax_spec.set_ylabel("Tần số (Hz)", color="#CCCCCC", fontsize=9)
        self.ax_spec.set_ylim(0, 8000)
        self.ax_spec.tick_params(colors="#CCCCCC", labelsize=9)

        # 3. STE & VAD realtime
        self.ax_ste.clear()
        self.ax_ste.set_facecolor("#121212")
        t_ste = data["t_ste"]
        ste_norm = data["ste_norm"]
        threshold = data["vad_threshold"]

        self.ax_ste.plot(t_ste, ste_norm, color="#39FF14", linewidth=1.2, label="Năng lượng STE")
        self.ax_ste.axhline(threshold, color="#FF4500", linestyle="--", linewidth=1.0, label="Ngưỡng VAD")
        self.ax_ste.fill_between(t_ste, 0, ste_norm, where=(ste_norm >= threshold), color="#39FF14", alpha=0.3)
        self.ax_ste.set_title("3. Năng lượng ngắn hạn STE & VAD thời gian thực", color="#39FF14", fontsize=10, weight="bold")
        self.ax_ste.set_xlabel("Thời gian gần nhất (giây)", color="#CCCCCC", fontsize=9)
        self.ax_ste.set_ylabel("Mức năng lượng", color="#CCCCCC", fontsize=9)
        self.ax_ste.set_ylim(-0.05, 1.1)
        self.ax_ste.tick_params(colors="#CCCCCC", labelsize=9)
        self.ax_ste.grid(True, linestyle="--", alpha=0.3, color="#555555")

        self.canvas.draw_idle()

    # ---------------- YÊU CẦU 2: KHI DỪNG THU ÂM THÌ BIỂU ĐỒ XUẤT HIỆN ĐẦY ĐỦ ----------------
    def render_full_analysis(self):
        """Vẽ toàn bộ âm thanh đầy đủ từ t=0 đến hết sau khi bấm dừng thu âm."""
        self._is_live_active = False
        data = self.engine.compute_signal_analysis(fast_mode=False)

        if data is None:
            self.clear_plots()
            return

        self.lbl_duration.configure(text=f"⏱️ Tổng thời lượng: {data['duration']:.2f} s")
        self.lbl_peak.configure(text=f"📈 Biên độ đỉnh: {data['max_amplitude']:.3f}")
        self.lbl_action_feedback.configure(
            text="✅ Đã thu âm xong! Hiển thị toàn bộ biểu đồ đầy đủ.",
            text_color="#00FF7F"
        )

        for ax in (self.ax_wave, self.ax_spec, self.ax_ste):
            ax.clear()
            ax.set_facecolor("#121212")
            ax.tick_params(colors="#CCCCCC", labelsize=9)
            for spine in ax.spines.values():
                spine.set_color("#444444")

        t_wave = data["t_wave"]
        waveform = data["waveform"]

        # 1. Toàn bộ Waveform
        self.ax_wave.plot(t_wave, waveform, color="#00FFFF", linewidth=0.8)
        self.ax_wave.set_title(f"1. Toàn bộ Dạng sóng thời gian (Waveform Đầy đủ - {data['duration']:.2f}s - Slide 01a)", color="#00FFFF", fontsize=10, weight="bold")
        self.ax_wave.set_ylabel("Biên độ", color="#CCCCCC", fontsize=9)
        self.ax_wave.set_ylim(-1.05, 1.05)
        self.ax_wave.set_xlim(0, data["duration"])
        self.ax_wave.grid(True, linestyle="--", alpha=0.3, color="#555555")

        # 2. Toàn bộ STFT Spectrogram
        self.ax_spec.pcolormesh(
            data["t_spec"], data["freqs"], data["spectrogram_db"],
            shading='gouraud', cmap='inferno', vmin=-60, vmax=0
        )
        self.ax_spec.set_title("2. Toàn bộ Phổ tần số STFT Spectrogram (0 - 8000 Hz - Slide 01c)", color="#FF8C00", fontsize=10, weight="bold")
        self.ax_spec.set_ylabel("Tần số (Hz)", color="#CCCCCC", fontsize=9)
        self.ax_spec.set_ylim(0, 8000)
        self.ax_spec.set_xlim(0, data["duration"])

        # 3. Toàn bộ STE & VAD
        t_ste = data["t_ste"]
        ste_norm = data["ste_norm"]
        threshold = data["vad_threshold"]

        self.ax_ste.plot(t_ste, ste_norm, color="#39FF14", linewidth=1.2, label="Năng lượng STE")
        self.ax_ste.axhline(threshold, color="#FF4500", linestyle="--", linewidth=1.0, label=f"Ngưỡng VAD ({threshold})")
        self.ax_ste.fill_between(t_ste, 0, ste_norm, where=(ste_norm >= threshold), color="#39FF14", alpha=0.3, label="Vùng giọng nói (Speech)")
        self.ax_ste.fill_between(t_ste, 0, ste_norm, where=(ste_norm < threshold), color="#777777", alpha=0.15, label="Khoảng lặng (Silence)")

        self.ax_ste.set_title("3. Toàn bộ Năng lượng ngắn hạn (STE) & Phân vùng VAD hoàn chỉnh (Slide 01b)", color="#39FF14", fontsize=10, weight="bold")
        self.ax_ste.set_xlabel("Thời gian (giây)", color="#CCCCCC", fontsize=9)
        self.ax_ste.set_ylabel("Mức năng lượng", color="#CCCCCC", fontsize=9)
        self.ax_ste.set_ylim(-0.05, 1.1)
        self.ax_ste.set_xlim(0, data["duration"])
        self.ax_ste.legend(loc="upper right", facecolor="#242526", edgecolor="#444444", labelcolor="#CCCCCC", fontsize=8)
        self.ax_ste.grid(True, linestyle="--", alpha=0.3, color="#555555")

        self.canvas.draw()
        self.canvas.flush_events()

    def on_close(self):
        """Đóng cửa sổ an toàn."""
        self._is_live_active = False
        self.destroy()
        if hasattr(self.master, "visualizer_window"):
            self.master.visualizer_window = None


# Bi danh tuong thich MVC
VisualizerWindow = SignalVisualizerWindow
