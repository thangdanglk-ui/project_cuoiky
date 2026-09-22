import os
import queue
import tempfile
import threading
import numpy as np
import sounddevice as sd
import scipy.signal as signal
from gtts import gTTS
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from controllers.asr_controller import CTCSpeechRecognizer
except ImportError:
    from asr_controller import CTCSpeechRecognizer


# Các chế độ đầu vào âm thanh chuẩn đồ án ASR
MODE_LAPTOP_MIC = "Nói trực tiếp vào Laptop"
MODE_HEADSET_MIC = "Nói qua tai phone (Tai nghe)"
MODE_FILE = "Chọn File âm thanh (.wav)"

# Giữ tương thích ngược
MODE_MIC = MODE_LAPTOP_MIC
MODE_SYSTEM_AUDIO = "Phát video hoặc âm nhạc từ một nền tảng"
MODE_HEADPHONE_AUDIO = "Phát video hoặc âm thanh qua tai nghe"

AUDIO_MODES = [
    MODE_LAPTOP_MIC,
    MODE_HEADSET_MIC,
    MODE_FILE
]

class AudioEngine:
    def __init__(self, model_size=None, on_model_status_change=None):
        self.on_model_status_change = on_model_status_change
        self.model_status = "Đang nạp mô hình AI Tự Huấn Luyện (SpeechCRNN + CTC)..."

        # Audio stream variables
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.audio_frames = []
        self.target_samplerate = 16000
        self.record_samplerate = 16000
        self.record_channels = 1
        self.stream = None
        self.active_device_index = None

        # Lưu trữ đoạn âm thanh vừa thu gần nhất để phân tích đồ thị
        self.last_recorded_audio = None

        # Khởi tạo Mô hình Nhận dạng Tiếng nói Chuỗi dài Tự Huấn Luyện (SpeechCRNN + CTC Loss)
        self.ctc_recognizer = CTCSpeechRecognizer()
        self.custom_classifier = self.ctc_recognizer  # Alias tương thích ngược 100% với giao diện GUI

        if self.ctc_recognizer.is_ready:
            self.model_status = "Mô hình AI Tiếng Việt (Fine-tuned CTC - Sẵn sàng)!"
            self._notify_status(self.model_status, "#00FF00")
        else:
            self.model_status = "Đang nạp mô hình AI Tiếng Việt (CTC)..."
            self._notify_status(self.model_status, "#FFA500")

    def _notify_status(self, message, color):
        if self.on_model_status_change:
            self.on_model_status_change(message, color)

    def is_model_ready(self):
        return self.ctc_recognizer is not None and self.ctc_recognizer.is_ready

    # ---------------- TỰ ĐỘNG CHỌN 1 THIẾT BỊ TỐI ƯU DUY NHẤT CHO MỖI CHẾ ĐỘ ----------------
    def get_mode_device_mapping(self):
        """
        Tự động phân tích card âm thanh và gán duy nhất 1 thiết bị chuẩn nhất cho mỗi chế độ.
        Đặc biệt: Loại bỏ hoàn toàn Windows WDM-KS (HostAPI 3) vì PortAudio không hỗ trợ
        stream blocking API trên WDM-KS, ưu tiên chuẩn MME (HostAPI 0) và DirectSound (HostAPI 1).
        """
        devices = sd.query_devices()
        
        def is_device_openable(idx):
            """Kiểm tra thiết bị có thể mở stream thu âm an toàn không."""
            try:
                d = devices[idx]
                if d.get('hostapi', -1) == 3:  # Bỏ qua WDM-KS (gây lỗi PaErrorCode -9999)
                    return False
                if d['max_input_channels'] <= 0:
                    return False
                # Thử kiểm tra định dạng
                sd.check_input_settings(device=idx, samplerate=16000, channels=1, dtype='int16')
                return True
            except Exception:
                try:
                    sr = int(devices[idx].get('default_samplerate', 44100))
                    sd.check_input_settings(device=idx, samplerate=sr, channels=min(2, devices[idx]['max_input_channels']), dtype='int16')
                    return True
                except Exception:
                    return False

        stereo_mix = None
        laptop_mic = None
        external_headset = None

        # Ưu tiên duyệt các thiết bị MME (HostAPI 0) trước, sau đó DirectSound (1) và WASAPI (2)
        safe_devices = []
        for idx, d in enumerate(devices):
            if d.get('hostapi', -1) == 3 or d['max_input_channels'] <= 0:
                continue
            name = d['name'].strip()
            name_lower = name.lower()
            if 'mapper' in name_lower or 'primary' in name_lower:
                continue
            if is_device_openable(idx):
                safe_devices.append((idx, d))

        for idx, d in safe_devices:
            name = d['name'].strip()
            name_lower = name.lower()

            # 1. Âm thanh hệ thống / Stereo Mix
            if 'stereo mix' in name_lower or 'what u hear' in name_lower or 'wave out' in name_lower:
                if stereo_mix is None:
                    stereo_mix = (idx, name)

            # 2. Tai nghe riêng biệt (USB, Bluetooth, Wireless, Hands-Free)
            elif any(k in name_lower for k in ['headset', 'earphone', 'tai nghe', 'bluetooth', 'hands-free', 'airpods', 'wireless']):
                if external_headset is None:
                    external_headset = (idx, name)

            # 3. Mic laptop tích hợp / Micro thu tiếng (TUYỆT ĐỐI không chứa 'mix')
            elif ('array' in name_lower or 'mic' in name_lower) and 'mix' not in name_lower:
                if laptop_mic is None:
                    laptop_mic = (idx, name)

        # Fallback cho laptop mic: tìm bất kỳ thiết bị nào có chữ mic mà không phải stereo mix
        if laptop_mic is None:
            for idx, d in safe_devices:
                if 'mic' in d['name'].lower() and 'mix' not in d['name'].lower():
                    laptop_mic = (idx, d['name'].strip())
                    break

        # Fallback thứ 2: tìm bất kỳ device nào không phải stereo mix
        if laptop_mic is None:
            for idx, d in safe_devices:
                if 'mix' not in d['name'].lower():
                    laptop_mic = (idx, d['name'].strip())
                    break

        if laptop_mic is None:
            laptop_mic = (1, "Microphone Array (Realtek Audio)")

        # Xử lý Mic tai nghe:
        if external_headset is not None:
            headset_mic_choice = (external_headset[0], f"[{external_headset[0]}] Tai phone ngoài ({external_headset[1]})")
        else:
            headset_mic_choice = (laptop_mic[0], f"[{laptop_mic[0]}] Tai phone cắm giắc 3.5mm (Realtek Combo Jack)")

        laptop_mic_choice = (laptop_mic[0], f"[{laptop_mic[0]}] Micro tích hợp trên Laptop")

        return {
            MODE_LAPTOP_MIC: laptop_mic_choice,
            MODE_HEADSET_MIC: headset_mic_choice,
            MODE_FILE: None,
            MODE_MIC: laptop_mic_choice
        }

    def get_all_input_devices(self):
        """
        Lấy danh sách các thiết bị thu âm sạch, phân biệt rõ ràng:
        1. Micro tích hợp trên Laptop
        2. Micro tai phone (cổng 3.5mm hoặc Bluetooth/USB)
        Loại bỏ hoàn toàn các thiết bị ảo như Stereo Mix, Sound Mapper.
        """
        devices = sd.query_devices()
        apis = sd.query_hostapis()
        input_devs = []
        seen = set()

        laptop_mic_idx = 1
        # Tìm device MME chuẩn cho Microphone Array
        for idx, d in enumerate(devices):
            if d['max_input_channels'] <= 0:
                continue
            name = d['name'].strip()
            name_lower = name.lower()
            if any(k in name_lower for k in ['mix', 'mapper', 'primary', 'driver']):
                continue
            api_name = apis[d['hostapi']]['name'].lower()
            if 'wdm-ks' in api_name:
                continue

            if 'array' in name_lower or 'mic' in name_lower:
                if 'mme' in api_name:
                    laptop_mic_idx = idx
                    break

        # Luôn có 2 lựa chọn rõ ràng:
        input_devs.append((laptop_mic_idx, f"[{laptop_mic_idx}] Micro tích hợp trên Laptop"))
        input_devs.append((laptop_mic_idx, f"[{laptop_mic_idx}] Tai phone cắm giắc 3.5mm (Realtek Combo Jack)"))

        # Thêm tai nghe Bluetooth / USB ngoài nếu có kết nối
        for idx, d in enumerate(devices):
            if d['max_input_channels'] <= 0:
                continue
            name = d['name'].strip()
            name_lower = name.lower()
            if any(k in name_lower for k in ['mix', 'mapper', 'primary', 'driver', 'array']):
                continue
            api_name = apis[d['hostapi']]['name'].lower()
            if 'wdm-ks' in api_name:
                continue

            if any(k in name_lower for k in ['headset', 'earphone', 'tai nghe', 'bluetooth', 'hands-free', 'airpods', 'wireless', 'usb']):
                key = f"headset_{name}"
                if key not in seen:
                    seen.add(key)
                    input_devs.append((idx, f"[{idx}] Tai phone ({name})"))

        return input_devs

    # ---------------- XỬ LÝ THU ÂM (RECORDING ĐA TẦN SỐ & ĐA KÊNH) ----------------
    def _find_working_audio_format(self, device_index):
        """Tự động dò tìm tần số mẫu (sample rate) và số kênh mà thiết bị chấp nhận."""
        try:
            info = sd.query_devices(device_index)
            native_sr = int(info.get('default_samplerate', 44100))
            max_ch = info.get('max_input_channels', 1)
        except Exception:
            native_sr = 44100
            max_ch = 1

        candidates = [
            (16000, 1),
            (16000, min(2, max_ch)),
            (native_sr, 1),
            (native_sr, min(2, max_ch)),
            (48000, min(2, max_ch)),
            (44100, min(2, max_ch)),
            (native_sr, max_ch)
        ]

        for sr, ch in candidates:
            try:
                sd.check_input_settings(device=device_index, samplerate=sr, channels=ch, dtype='int16')
                return sr, ch
            except Exception:
                continue

        return native_sr, min(2, max_ch)

    def _audio_callback(self, indata, frames, time, status):
        if status:
            pass
        self.audio_queue.put(bytes(indata))

    def start_recording(self, device_index):
        """Bắt đầu thu âm trên thiết bị được chọn với tần số tương thích phần cứng."""
        if self.is_recording:
            return False, "Đang trong quá trình thu âm!"

        if not self.is_model_ready():
            return False, "Vui lòng đợi mô hình AI Tự Huấn Luyện nạp xong trước khi thu âm!"

        self.active_device_index = device_index
        self.audio_frames = []
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        working_sr, working_ch = self._find_working_audio_format(device_index)
        self.record_samplerate = working_sr
        self.record_channels = working_ch

        try:
            self.stream = sd.RawInputStream(
                samplerate=self.record_samplerate,
                blocksize=int(self.record_samplerate * 0.1),  # 100ms chunks để phản hồi realtime nhanh
                dtype='int16',
                channels=self.record_channels,
                callback=self._audio_callback,
                device=device_index
            )
            self.stream.start()
            self.is_recording = True
            return True, f"Bắt đầu thu âm ({self.record_samplerate}Hz, {self.record_channels}ch)"
        except Exception as e:
            return False, f"Lỗi khởi động thiết bị thu âm: {e}"

    def record_loop(self):
        """Lắng nghe dữ liệu âm thanh trong vòng lặp thu âm."""
        while self.is_recording:
            try:
                data = self.audio_queue.get(timeout=0.1)
                self.audio_frames.append(data)
            except queue.Empty:
                continue

    def get_current_live_audio(self):
        """Trả về mảng float32 của âm thanh gần nhất đang thu thời gian thực (realtime)."""
        if not self.is_recording or not self.audio_frames:
            return None
        try:
            # Lấy tối đa khoảng 2.5 giây âm thanh gần nhất để vẽ sóng realtime siêu mượt
            max_chunks = 25
            recent_frames = self.audio_frames[-max_chunks:]
            raw = b"".join(recent_frames)
            data = np.frombuffer(raw, dtype=np.int16)
            if len(data) == 0:
                return None

            if self.record_channels > 1:
                total = len(data) - (len(data) % self.record_channels)
                reshaped = data[:total].reshape(-1, self.record_channels)
                ch_max = np.max(np.abs(reshaped), axis=0)
                best_ch = int(np.argmax(ch_max))
                if np.min(ch_max) == 0 or ch_max[best_ch] > 1.8 * np.min(ch_max):
                    mono = reshaped[:, best_ch]
                else:
                    mono = np.mean(reshaped, axis=1)
            else:
                mono = data

            audio_float = mono.astype(np.float32) / 32768.0
            if self.record_samplerate != self.target_samplerate:
                audio_float = signal.resample_poly(
                    audio_float,
                    self.target_samplerate,
                    self.record_samplerate
                ).astype(np.float32)
            return audio_float
        except Exception:
            return None

    def stop_recording(self):
        """Dừng thu âm, chuyển đổi kênh và resample về chuẩn 16000Hz."""
        self.is_recording = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        if not self.audio_frames:
            return None

        # Gộp toàn bộ dữ liệu byte và chuyển thành mảng int16
        raw_bytes = b"".join(self.audio_frames)
        audio_data = np.frombuffer(raw_bytes, dtype=np.int16)

        if len(audio_data) == 0:
            return None

        # Chuyển đổi nhiều kênh (Stereo) sang Mono nếu cần
        if self.record_channels > 1:
            total_samples = len(audio_data) - (len(audio_data) % self.record_channels)
            audio_reshaped = audio_data[:total_samples].reshape(-1, self.record_channels)
            ch_max = np.max(np.abs(audio_reshaped), axis=0)
            best_ch = int(np.argmax(ch_max))
            # Nếu 1 kênh có năng lượng áp đảo hoặc kênh kia bị câm/ngược pha, ưu tiên lấy kênh mạnh nhất
            if np.min(ch_max) == 0 or ch_max[best_ch] > 1.8 * np.min(ch_max):
                audio_mono = audio_reshaped[:, best_ch]
            else:
                audio_mono = np.mean(audio_reshaped, axis=1)
        else:
            audio_mono = audio_data

        # Chuẩn hoá sang float32 phạm vi [-1.0, 1.0]
        audio_float = audio_mono.astype(np.float32) / 32768.0

        # Resample về 16000Hz nếu phần cứng thu ở 44100Hz hoặc 48000Hz
        if self.record_samplerate != self.target_samplerate:
            try:
                audio_float = signal.resample_poly(
                    audio_float,
                    self.target_samplerate,
                    self.record_samplerate
                ).astype(np.float32)
            except Exception as e:
                print(f"Lỗi resample: {e}")

        # Lưu lại mảng audio toàn bộ vừa thu để vẽ biểu đồ đầy đủ khi dừng
        self.last_recorded_audio = audio_float
        return audio_float

    # ---------------- PHÂN TÍCH TÍN HIỆU (WAVEFORM, SPECTROGRAM, SHORT-TIME ENERGY) ----------------
    def compute_signal_analysis(self, audio_np=None, fast_mode=False):
        """
        Tính toán đặc trưng tín hiệu âm thanh:
        - Waveform (Miền thời gian)
        - STFT Spectrogram (Biến đổi Fourier ngắn hạn & Cửa sổ Hamming)
        - Short-Time Energy (STE) & Ngưỡng hoạt tính giọng nói (VAD)
        """
        if audio_np is None:
            audio_np = self.last_recorded_audio

        if audio_np is None or len(audio_np) == 0:
            return None

        sr = self.target_samplerate  # 16000 Hz
        duration = len(audio_np) / sr

        # 1. Trục thời gian Waveform
        t_wave = np.linspace(0, duration, len(audio_np), endpoint=False)

        # 2. STFT Spectrogram (Cửa sổ Hamming)
        nperseg = 256 if fast_mode else min(512, len(audio_np))
        noverlap = int(nperseg * 0.5) if fast_mode else (int(nperseg * 0.75) if nperseg > 1 else 0)
        
        freqs, t_spec, Sxx = signal.spectrogram(
            audio_np,
            fs=sr,
            window='hamming',
            nperseg=nperseg,
            noverlap=noverlap
        )
        Sxx_db = 10 * np.log10(Sxx + 1e-10)

        # 3. Năng lượng ngắn hạn (Short-Time Energy - STE)
        frame_len = int(0.025 * sr)
        hop_len = int(0.015 * sr) if fast_mode else int(0.010 * sr)
        if len(audio_np) >= frame_len:
            window = np.hamming(frame_len)
            num_frames = 1 + int((len(audio_np) - frame_len) / hop_len)
            ste = np.zeros(num_frames)
            t_ste = np.zeros(num_frames)
            for i in range(num_frames):
                start = i * hop_len
                frame = audio_np[start:start + frame_len] * window
                ste[i] = np.sum(frame ** 2)
                t_ste[i] = (start + frame_len / 2) / sr

            max_ste = np.max(ste) if np.max(ste) > 0 else 1.0
            ste_norm = ste / max_ste
            vad_threshold = 0.08
            vad_mask = ste_norm >= vad_threshold
        else:
            ste_norm = np.array([0.0])
            t_ste = np.array([0.0])
            vad_threshold = 0.08
            vad_mask = np.array([False])

        return {
            "duration": duration,
            "samplerate": sr,
            "samples": len(audio_np),
            "max_amplitude": float(np.max(np.abs(audio_np))),
            "t_wave": t_wave,
            "waveform": audio_np,
            "t_spec": t_spec,
            "freqs": freqs,
            "spectrogram_db": Sxx_db,
            "t_ste": t_ste,
            "ste_norm": ste_norm,
            "vad_threshold": vad_threshold,
            "vad_mask": vad_mask
        }

    def apply_vad_trimming(self, audio_np, vad_threshold=0.08, padding_ms=200):
        """
        Cắt gọt khoảng lặng (Silence Trimming) dựa trên Năng lượng ngắn hạn (STE):
        - Tìm ranh giới bắt đầu (onset) và kết thúc (offset) của vùng có tiếng nói.
        - Dự trữ padding_ms (mặc định 200ms) ở hai đầu để bảo toàn âm đầu/đuôi.
        - Trả về mảng âm thanh đã cắt gọt, hoặc None nếu toàn bộ tín hiệu là khoảng lặng/tiếng ồn.
        """
        if audio_np is None or len(audio_np) == 0:
            return None

        sr = self.target_samplerate
        frame_len = int(0.025 * sr)  # 400 mẫu (25ms)
        hop_len = int(0.010 * sr)    # 160 mẫu (10ms)

        if len(audio_np) < frame_len:
            return audio_np

        # Kiểm tra sàn năng lượng: Nếu toàn bộ tín hiệu chỉ là tiếng ồn nền cực nhỏ
        max_amp = float(np.max(np.abs(audio_np)))
        if max_amp < 0.005:
            print(f"[VAD] Tín hiệu quá nhỏ (Biên độ đỉnh {max_amp:.5f} < 0.005) -> Xác định là khoảng lặng.")
            return None

        window = np.hamming(frame_len)
        num_frames = 1 + int((len(audio_np) - frame_len) / hop_len)
        ste = np.zeros(num_frames)

        for i in range(num_frames):
            start = i * hop_len
            frame = audio_np[start:start + frame_len] * window
            ste[i] = np.sum(frame ** 2)

        max_ste = np.max(ste) if np.max(ste) > 0 else 1.0
        ste_norm = ste / max_ste
        vad_mask = ste_norm >= vad_threshold

        active_indices = np.where(vad_mask)[0]
        if len(active_indices) == 0:
            print("[VAD] Không phát hiện tiếng nói (Toàn bộ dưới ngưỡng 0.08) -> Bỏ qua nhận dạng.")
            return None

        start_frame = active_indices[0]
        end_frame = active_indices[-1]

        padding_samples = int((padding_ms / 1000.0) * sr)
        start_sample = max(0, start_frame * hop_len - padding_samples)
        end_sample = min(len(audio_np), end_frame * hop_len + frame_len + padding_samples)

        trimmed_audio = audio_np[start_sample:end_sample]
        orig_dur = len(audio_np) / sr
        trim_dur = len(trimmed_audio) / sr
        print(f"[VAD] Đã kích hoạt màng lọc: Cắt từ {orig_dur:.2f}s -> {trim_dur:.2f}s (Đã gọt bỏ {orig_dur - trim_dur:.2f}s im lặng).")
        return trimmed_audio

    def set_asr_engine(self, engine_name):
        """Thay đổi động cơ ASR: 'crnn', 'wav2vec2', hoặc 'both'."""
        if hasattr(self, 'ctc_recognizer') and self.ctc_recognizer is not None:
            return self.ctc_recognizer.set_engine(engine_name)
        return False

    def load_audio_file(self, file_path):
        """
        Nạp file âm thanh từ đĩa (.wav, .flac, .ogg, .mp3...),
        chuyển đổi về mono và tần số 16000Hz chuẩn đồ án.
        """
        import soundfile as sf
        import scipy.signal as signal

        data, sr = sf.read(file_path)
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
        data = data.astype(np.float32)

        if sr != self.target_samplerate:
            # Tái lấy mẫu về 16000 Hz
            data = signal.resample_poly(data, self.target_samplerate, sr).astype(np.float32)

        # Chuẩn hóa biên độ
        max_amp = float(np.max(np.abs(data)))
        if max_amp > 0:
            data = (data / max_amp) * 0.95

        self.last_recorded_audio = data
        return data

    def play_file(self, file_path):
        """Phát trực tiếp file âm thanh ra loa ngay lập tức với độ trễ 0ms."""
        if not file_path or not os.path.exists(file_path):
            return False
        # Với Windows và file WAV, winsound phát tức thì 0ms không qua trung gian
        if os.name == 'nt' and file_path.lower().endswith('.wav'):
            try:
                import winsound
                winsound.PlaySound(file_path, winsound.SND_ASYNC | winsound.SND_FILENAME)
                return True
            except Exception:
                pass

        # Fallback bằng sounddevice cho các định dạng khác
        try:
            import soundfile as sf
            data, sr = sf.read(file_path)
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            sd.stop()
            sd.play(data, samplerate=sr)
            return True
        except Exception:
            return False

    def play_audio(self, audio_np=None, samplerate=None):
        """Phát đoạn âm thanh (từ file hoặc từ mic vừa thu) qua loa máy tính/tai nghe."""
        if audio_np is None:
            audio_np = self.last_recorded_audio
        if audio_np is None or len(audio_np) == 0:
            return False, "Không có dữ liệu âm thanh để phát!"

        sr = samplerate or self.target_samplerate
        try:
            sd.stop()
            sd.play(audio_np, samplerate=sr)
            return True, "Đang phát âm thanh..."
        except Exception as e:
            return False, f"Lỗi phát âm thanh: {e}"

    def stop_audio_playback(self):
        """Dừng phát âm thanh ngay lập tức."""
        try:
            if os.name == 'nt':
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass
        try:
            sd.stop()
            return True
        except Exception:
            return False

    # ---------------- NHẬN DIỆN TIẾNG NÓI CHUỖI DÀI (SpeechCRNN + CTC LOSS) ----------------
    def transcribe(self, audio_np, use_vad=True, language="vi", engine=None):
        """
        Giải mã âm thanh thành chuỗi văn bản tiếng Việt theo động cơ được chọn:
        - 'crnn': Mô hình CRNN-CTC tự xây dựng (Slide 2b)
        - 'wav2vec2': Mô hình Wav2Vec2-CTC nâng cao
        - 'both': So sánh đối chiếu cả 2 mô hình
        """
        if audio_np is None or len(audio_np) == 0:
            return ""

        if not self.is_model_ready():
            return "[Lỗi] Mô hình AI chưa sẵn sàng!"

        # Màng lọc VAD: Cắt gọt khoảng lặng & loại bỏ tạp âm nền
        if use_vad:
            trimmed_audio = self.apply_vad_trimming(audio_np, vad_threshold=0.08, padding_ms=200)
            if trimmed_audio is None:
                # Toàn bộ đoạn âm thanh chỉ là khoảng lặng hoặc tiếng ồn dưới ngưỡng VAD
                return ""
            audio_to_recognize = trimmed_audio
        else:
            audio_to_recognize = audio_np

        return self.ctc_recognizer.recognize(audio_to_recognize, sr=self.target_samplerate, engine=engine)

    # ---------------- PHÁT TIẾNG NÓI (TEXT TO SPEECH) ----------------
    def text_to_speech(self, text, lang="vi", on_complete=None):
        """Chuyển văn bản thành giọng nói qua gTTS và phát trên Windows."""
        text = text.strip()
        if not text:
            if on_complete:
                on_complete(False, "Văn bản rỗng, vui lòng nhập nội dung để phát!")
            return

        def _worker():
            try:
                tts = gTTS(text=text, lang=lang, slow=False)
                temp_file = os.path.join(tempfile.gettempdir(), f"speech_ai_tts_{os.getpid()}.mp3")
                tts.save(temp_file)

                if os.name == 'nt':
                    os.startfile(temp_file)
                
                if on_complete:
                    on_complete(True, "Đã phát âm thanh thành công!")
            except Exception as e:
                if on_complete:
                    on_complete(False, f"Lỗi tổng hợp giọng nói: {e}")

        threading.Thread(target=_worker, daemon=True).start()


# Bi danh tuong thich MVC
AudioController = AudioEngine
