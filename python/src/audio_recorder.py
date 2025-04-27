import pyaudiowpatch as pyaudiow
import wave
import sys
import time
import io # 确保导入 io 模块
import datetime # <--- 导入 datetime

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

# 录制参数
FORMAT = pyaudiow.paInt16  # 格式，例如 paInt16 (16bit)
CHANNELS = 2             # 声道数，通常是 2 (立体声)
RATE = 48000             # 采样率，例如 48000 Hz
CHUNK = 1024             # 每次读取的帧数
# RECORD_SECONDS = 5       # 录制时长 (秒)
# WAVE_OUTPUT_FILENAME = "output.wav" # 输出文件名

print("正在初始化 PyAudio...")

p = pyaudiow.PyAudio()

print("PyAudio 初始化完成。")

# --- 查找 WASAPI Loopback 设备 ---
# PyAudioWPatch 提供了方便的方法来查找 loopback 设备

default_wasapi_info = None # 先初始化为 None
try:
    # --- 查找 WASAPI Host API 信息 ---
    # 使用 get_host_api_info_by_type 获取指定类型的 Host API 信息
    default_wasapi_info = p.get_host_api_info_by_type(pyaudiow.paWASAPI)

except OSError:
    print("错误: 无法获取 WASAPI Host API 信息。您的系统可能不支持 WASAPI。", file=sys.stderr)
    p.terminate()
    sys.exit(1)

if not default_wasapi_info:
    # 这段理论上在 get_host_api_info_by_type 成功后不会执行，除非 PyAudio 内部返回了空
    print("错误: 未找到 WASAPI Host API 信息 (即使 get_host_api_info_by_type 没有抛出错误)。")
    p.terminate()
    sys.exit(1)

print(f"获取到 WASAPI Host API 信息: {default_wasapi_info['name']}")

print("查找默认 WASAPI Loopback 设备...")

try:
    # 使用新的方法获取默认的 WASAPI loopback 设备信息
    default_loopback_device = p.get_default_wasapi_loopback()
    print(f"找到默认 WASAPI Loopback 设备: {default_loopback_device['name']}")
    device_index = default_loopback_device["index"]

except Exception as e:
    print(f"错误: 无法找到默认 WASAPI Loopback 设备，或发生错误: {e}")
    print("尝试列出所有设备并查找 loopback 设备...")

    device_index = None
    # 迭代所有设备，查找是 WASAPI 并且支持 loopback 的设备
    # 注意: Loopback 设备在 PyAudioWPatch 中被标记为输入设备
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        # print(f"设备 {i}: {dev['name']}, Host API: {p.get_host_api_info_by_index(dev['hostApi'])['name']}, 输入通道: {dev['maxInputChannels']}, 输出通道: {dev['maxOutputChannels']}")

        if (dev["hostApi"] == default_wasapi_info["index"] and
            dev["maxInputChannels"] > 0 and # 必须是输入设备 (loopback device is an input)
            'Loopback' in dev['name']): # 一个简单的名称检查，可能需要更精确的判断
            print(f"找到一个 WASAPI Loopback 设备 (索引 {i}): {dev['name']}")
            device_index = i
            break # 找到第一个就用

    if device_index is None:
         print("错误: 未找到 WASAPI Loopback 输入设备。请确保您的音频设备支持 WASAPI Loopback。")
         p.terminate()
         sys.exit(1)


print(f"使用设备索引: {device_index}")

# --- 检查并确定支持的采样率 ---
supported_rate = None

# 1. 尝试初始 RATE (44100 Hz)
print(f"正在检查设备 {device_index} 是否支持 采样率={RATE}Hz, 格式={FORMAT}, 声道数={CHANNELS}...")
try:
    if p.is_format_supported(RATE,
                             input_device=device_index,
                             input_channels=CHANNELS,
                             input_format=FORMAT):
        supported_rate = RATE
        print(f"设备支持 {RATE}Hz。")
    else:
        print(f"设备不支持 {RATE}Hz。将尝试 48000Hz。")

except ValueError as e:
    # 捕获 ValueError，检查是否是关于采样率的错误
    if 'Invalid sample rate' in str(e):
        print(f"设备不支持 {RATE}Hz (检查时引发错误)。将尝试 48000Hz。")
    else:
        # 如果是其他 ValueError (例如无效设备索引)，则重新抛出或退出
        print(f"检查格式支持性时出错 (可能是无效的设备索引 {device_index}?): {e}", file=sys.stderr)
        p.terminate()
        sys.exit(1)
except Exception as e:
    # 捕获其他可能的未知错误
    print(f"检查 {RATE}Hz 支持性时发生未知错误: {e}", file=sys.stderr)
    p.terminate()
    sys.exit(1)

# 2. 如果初始 RATE 不支持，尝试 48000 Hz
if supported_rate is None:
    rate_to_try = 48000
    print(f"正在尝试检查 {rate_to_try}Hz...")
    try:
        if p.is_format_supported(rate_to_try,
                                 input_device=device_index,
                                 input_channels=CHANNELS,
                                 input_format=FORMAT):
            supported_rate = rate_to_try
            RATE = rate_to_try # <--- 更新全局 RATE 变量
            print(f"设备支持 {RATE}Hz。将使用此采样率。")
        else:
            print(f"设备似乎也不支持 {rate_to_try}Hz。")
    except ValueError as e:
        if 'Invalid sample rate' in str(e):
             print(f"设备不支持 {rate_to_try}Hz (检查时引发错误)。")
        else:
             print(f"检查 {rate_to_try}Hz 支持性时出错: {e}", file=sys.stderr)
             # 在这里不立即退出，让最终检查处理
    except Exception as e:
        print(f"检查 {rate_to_try}Hz 支持性时发生未知错误: {e}", file=sys.stderr)
        # 在这里不立即退出，让最终检查处理

# 3. 最终检查是否找到了支持的速率
if supported_rate is None:
     print(f"错误: 设备 {device_index} 既不支持 44100Hz 也不支持 48000Hz (或其他参数)。请检查设备规格或尝试其他采样率。", file=sys.stderr)
     p.terminate()
     sys.exit(1)

# --- 打开音频流进行录制 ---
print("正在打开音频流...")
stream = None
frames = []
recording_start_time = datetime.datetime.now() # <--- 记录开始时间

try:
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=CHUNK)

    print("音频流打开成功。开始录制... (按 Ctrl+C 停止)")

    # --- 无限循环录制 ---
    while True:
        try:
            data = stream.read(CHUNK)
            frames.append(data)
        except KeyboardInterrupt: # <--- 捕获 Ctrl+C
            print("\n检测到 Ctrl+C，停止录制...")
            break
        except IOError as e:
            # 检查是否是输入溢出错误 (常见于长时间录制)
            if e.errno == pyaudiow.paInputOverflowed:
                print("警告: 输入溢出 (Input overflowed)，部分数据可能丢失。", file=sys.stderr)
                # 可以选择继续录制，或者在这里 break
                # frames.append(b'\x00' * CHUNK * CHANNELS * p.get_sample_size(FORMAT)) # 可选：插入静音数据
            else:
                print(f"读取音频流时发生 IO 错误: {e}", file=sys.stderr)
                break # 其他 IO 错误，停止录制
        except Exception as e:
             print(f"录制循环中发生未知错误: {e}", file=sys.stderr)
             break # 未知错误，停止录制


    print("录制循环结束。")

except Exception as e:
    # 这个是 stream.open() 可能发生的错误
    print(f"打开音频流时发生错误: {e}", file=sys.stderr)
    sys.exit(1)

finally:
    # --- 停止和关闭流以及 PyAudio ---
    if stream is not None and stream.is_active(): # 检查流是否还活跃
        print("正在停止和关闭音频流...")
        stream.stop_stream()
        stream.close()
        print("音频流已关闭。")

print("正在终止 PyAudio...")
p.terminate()
print("PyAudio 已终止。")


# --- 将录制的音频保存到 WAV 文件 ---
if not frames:
    print("没有录制到任何音频数据，不保存文件。")
    sys.exit(0) # 正常退出

# --- 生成带时间戳的文件名 ---
timestamp = recording_start_time.strftime("%Y%m%d_%H%M%S")
WAVE_OUTPUT_FILENAME = f"output_{timestamp}.wav"
print(f"准备将录音保存到文件: {WAVE_OUTPUT_FILENAME}")

try:
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"文件 '{WAVE_OUTPUT_FILENAME}' 已成功保存。")
    # 通过标准输出将实际文件名返回给调用者
    print(f"录音文件路径: {WAVE_OUTPUT_FILENAME}")

except Exception as e:
    print(f"保存文件时发生错误: {e}", file=sys.stderr)
    sys.exit(1)

print("脚本执行完毕。")