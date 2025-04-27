"""
Audio Recorder module for capturing system audio using WASAPI loopback devices.
Based on official PyAudioWPatch examples.
"""

from queue import Queue
import pyaudiowpatch as pyaudio
import wave
import sys
import time
import io # 确保导入 io 模块
import datetime # 导入 datetime
import os
import atexit
import locale

# --- 控制台编码设置 ---
# 在文件顶部尽早设置
try:
    # 确保控制台可以显示中文字符
    if sys.platform == 'win32':
        # 在 Windows 上，尝试设置控制台代码页为 UTF-8
        os.system('chcp 65001 > nul')
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    # 打印当前控制台编码信息，便于调试
    print(f"当前控制台编码: {sys.stdout.encoding}")
    print(f"当前系统默认编码: {sys.getdefaultencoding()}")
    print(f"当前区域设置: {locale.getpreferredencoding()}")
except Exception as e:
    print(f"Warning: 设置控制台编码时出错: {e}")

# --- 锁文件机制 ---
LOCK_FILE = "audio_recorder.lock"

# 检查锁文件
if os.path.exists(LOCK_FILE):
    print(f"Found lock file {LOCK_FILE}, another recording process may be running.")
    print("If no other process is running, please delete the file and retry.")
    sys.exit(1)

# 创建锁文件
with open(LOCK_FILE, "w", encoding="utf-8") as f:
    f.write(str(os.getpid()))

# 注册退出时清理锁文件
def cleanup_lock():
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
            print("Lock file has been removed.")
        except Exception as e:
            print(f"Error when cleaning up lock file: {e}")

atexit.register(cleanup_lock)

# --- Force stdout and stderr to use UTF-8 ---
# 这对于在 Windows 上运行 subprocess 并打印非 ASCII 字符至关重要
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        print("Successfully set sys.stdout to UTF-8")
    except Exception as e:
        print(f"Warning: Failed to set sys.stdout to UTF-8: {e}", file=sys.stderr)

if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        print("Successfully set sys.stderr to UTF-8", file=sys.stderr) # 打印到 stderr
    except Exception as e:
        # 如果设置 stderr 失败，我们只能尝试用默认编码打印错误
        print(f"Warning: Failed to set sys.stderr to UTF-8: {e}")
# --- End UTF-8 setup ---

class AudioRecorderException(Exception):
    """Base class for AudioRecorder's exceptions"""
    pass


class WASAPINotFound(AudioRecorderException):
    """WASAPI is not available on the system"""
    pass


class InvalidDevice(AudioRecorderException):
    """Requested audio device is not valid or not found"""
    pass


class AudioRecorder:
    """
    Audio recorder class for capturing system audio using WASAPI loopback.
    Supports recording, pausing, and saving to WAV files.
    """
    
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16
    
    def __init__(self):
        """Initialize the audio recorder"""
        self.p = pyaudio.PyAudio()
        self.output_queue = Queue()
        self.stream = None
        self.recording = False
        self.default_device = None
        self.current_device = None
    
    def __enter__(self):
        """Context manager entry method"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit method - ensures proper cleanup"""
        self.close()
        
    def callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio processing"""
        if len(in_data) > 0:
            self.output_queue.put(in_data)
            # 如果是第一次收到数据或每100帧打印一次
            if hasattr(self, 'frame_counter'):
                self.frame_counter += 1
                if self.frame_counter % 100 == 0:
                    print(f"Received {self.frame_counter} audio frames")
            else:
                self.frame_counter = 1
                print("First audio frame received")
        else:
            print("Warning: Received empty audio frame")
        return (in_data, pyaudio.paContinue)
    
    def find_loopback_device(self):
        """Find the default WASAPI loopback device"""
        try:
            # Get WASAPI info
            wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            raise WASAPINotFound("WASAPI is not available on this system")
        
        # Try to get the default WASAPI loopback device
        try:
            default_loopback = self.p.get_default_wasapi_loopback()
            print(f"Found default WASAPI loopback device: {default_loopback['name']}")
            return default_loopback
        except Exception as e:
            print(f"Couldn't find default loopback device: {e}")
            print("Searching for alternative loopback devices...")
            
            # Get default WASAPI speakers
            default_speakers = self.p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            
            # Look for a loopback device matching the default speakers
            for loopback in self.p.get_loopback_device_info_generator():
                if default_speakers["name"] in loopback["name"]:
                    print(f"Found matching loopback device: {loopback['name']}")
                    return loopback
            
            # If we get here, no suitable device was found
            raise InvalidDevice("No suitable loopback device found")
    
    def list_devices(self):
        """List all audio devices with details"""
        self.p.print_detailed_system_info()
    
    def start_recording(self, device_index=None):
        """
        Start recording from the specified device or find a default one
        
        Args:
            device_index: Optional index of the device to record from
        """
        # Close any existing stream
        self.stop_recording()
        
        # Determine which device to use
        if device_index is not None:
            try:
                self.current_device = self.p.get_device_info_by_index(device_index)
                print(f"Using specified device: {self.current_device['name']}")
            except Exception as e:
                print(f"Error using specified device {device_index}: {e}")
                print("Falling back to default device")
                self.current_device = self.find_loopback_device()
        else:
            # Use default device
            self.current_device = self.find_loopback_device()
        
        # Store recording start time
        self.recording_start_time = datetime.datetime.now()
        
        # Open the stream
        try:
            self.stream = self.p.open(
                format=self.FORMAT,
                channels=self.current_device["maxInputChannels"],
                rate=int(self.current_device["defaultSampleRate"]),
                frames_per_buffer=self.CHUNK_SIZE,
                input=True,
                input_device_index=self.current_device["index"],
                stream_callback=self.callback
            )
            
            self.recording = True
            print(f"Recording started from device: {self.current_device['name']}")
            print("Press Ctrl+C to stop recording...")
            
        except Exception as e:
            raise AudioRecorderException(f"Failed to start recording: {e}")
    
    def pause_recording(self):
        """Pause the recording stream"""
        if self.stream and not self.stream.is_stopped():
            self.stream.stop_stream()
            print("Recording paused")
    
    def resume_recording(self):
        """Resume a paused recording stream"""
        if self.stream and self.stream.is_stopped():
            self.stream.start_stream()
            print("Recording resumed")
    
    def stop_recording(self):
        """Stop recording and close the stream"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.recording = False
            print("Recording stopped")
    
    def save_recording(self, filename=None):
        """
        Save the recorded audio to a WAV file
        
        Args:
            filename: Optional filename to save to. If None, generates a timestamped filename.
        
        Returns:
            The filename the recording was saved to
        """
        if not filename:
            # Generate a filename based on timestamp
            timestamp = self.recording_start_time.strftime("%Y%m%d_%H%M%S")
            filename = f"output_{timestamp}.wav"
        
        if not self.output_queue.empty():
            print(f"Saving recording to {filename}...")
            
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.current_device["maxInputChannels"])
                wf.setsampwidth(pyaudio.get_sample_size(self.FORMAT))
                wf.setframerate(int(self.current_device["defaultSampleRate"]))
                
                # Write all audio data from the queue
                while not self.output_queue.empty():
                    wf.writeframes(self.output_queue.get())
            
            print(f"Recording saved to {filename}")
            return filename
        else:
            print("No audio data to save")
            return None
    
    def close(self):
        """Close the recorder and release resources"""
        self.stop_recording()
        self.p.terminate()
        print("Audio recorder closed")


def record_audio(duration=None):
    """
    Simple function to record audio for a specified duration
    
    Args:
        duration: Recording duration in seconds. If None, records until Ctrl+C.
    
    Returns:
        Filename of the saved recording
    """
    with AudioRecorder() as recorder:
        try:
            # Start recording
            recorder.start_recording()
            
            if duration:
                # Record for specified duration
                print(f"Recording for {duration} seconds...")
                time.sleep(duration)
            else:
                # Record until interrupted
                try:
                    while True:
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    print("\nRecording interrupted by user")
            
            # Stop recording and save
            recorder.stop_recording()
            return recorder.save_recording()
            
        except AudioRecorderException as e:
            print(f"Recording error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None


if __name__ == "__main__":
    # When run directly, record until Ctrl+C is pressed
    try:
        filename = record_audio()
        if filename:
            print(f"Recording file path: {filename}")
        else:
            print("Recording failed")
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error: {e}")