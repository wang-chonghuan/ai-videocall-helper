import subprocess
import sys
import os
import time
import signal

# 假定此测试脚本是在 python/ 目录下，并且虚拟环境已激活
# 所以我们可以直接使用 'python' 命令，它会指向虚拟环境中的解释器
# 并指定要运行的脚本路径相对于当前工作目录 (python/)
AUDIO_RECORDER_SCRIPT_PATH = os.path.join("src", "audio_recorder.py")

def run_audio_recorder_interactive():
    """
    使用 Popen 启动 audio_recorder.py 脚本，允许用户交互式停止，
    并捕获其输出。
    """
    print(f"--- 启动脚本: {AUDIO_RECORDER_SCRIPT_PATH} ---")
    print("录音程序将在后台运行。请在此窗口按 Ctrl+C 来停止录音和测试。")
    print("----------------------------------------------------------")

    process = None
    try:
        # 使用 subprocess.Popen 启动脚本，不阻塞父进程
        # stdout=subprocess.PIPE 和 stderr=subprocess.PIPE 用于捕获输出
        # text=True 和 encoding='utf-8' 用于解码输出
        process = subprocess.Popen(
            [sys.executable, AUDIO_RECORDER_SCRIPT_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            bufsize=1,  # 行缓冲，可能有助于实时获取 print 输出
            universal_newlines=True # 确保换行符被正确处理
        )

        # 等待子进程结束 (例如用户按 Ctrl+C 终止了子进程，或者子进程自己出错退出)
        # 同时实时打印子进程的输出
        stdout_lines = []
        stderr_lines = []

        print("--- 子进程实时输出 (按 Ctrl+C 停止录音) ---")
        while True:
            # 尝试非阻塞地读取 stdout
            stdout_line = process.stdout.readline()
            if stdout_line:
                print(f"[RECORDER STDOUT] {stdout_line.strip()}")
                stdout_lines.append(stdout_line)

            # 尝试非阻塞地读取 stderr
            stderr_line = process.stderr.readline()
            if stderr_line:
                print(f"[RECORDER STDERR] {stderr_line.strip()}", file=sys.stderr)
                stderr_lines.append(stderr_line)

            # 检查子进程是否已结束
            return_code = process.poll()
            if return_code is not None:
                print(f"\n--- 子进程已结束，退出码: {return_code} ---")
                # 读取剩余的输出
                for remaining_line in process.stdout.readlines():
                     print(f"[RECORDER STDOUT] {remaining_line.strip()}")
                     stdout_lines.append(remaining_line)
                for remaining_line in process.stderr.readlines():
                     print(f"[RECORDER STDERR] {remaining_line.strip()}", file=sys.stderr)
                     stderr_lines.append(remaining_line)
                break # 退出循环

            # 短暂休眠避免 CPU 占用过高
            time.sleep(0.1)


        # --- 处理结果 ---
        final_stdout = "".join(stdout_lines)
        final_stderr = "".join(stderr_lines)

        if return_code != 0 and not final_stderr: # 如果有错误码但stderr为空，可能被Ctrl+C终止
             print("\n--- 脚本可能被手动终止 (Ctrl+C) ---")

        if final_stderr:
             print("\n--- 脚本执行过程中出现错误 ---")
        # else: # 如果 return_code 为 0 且 stderr 为空
        #      print("\n--- 脚本似乎已成功完成 (如果被正常停止) ---")


        # 解析 stdout 来获取录音文件的路径
        if final_stdout:
             file_path_line = [line for line in final_stdout.splitlines() if "录音文件路径:" in line]
             if file_path_line:
                 parts = file_path_line[-1].split(":", 1) # 取最后一行匹配的
                 if len(parts) > 1:
                     recorded_file = parts[1].strip()
                     print(f"录音文件应保存在: {recorded_file}")
                 else:
                     print("警告: 在标准输出中找到 '录音文件路径:' 但无法解析路径。", file=sys.stderr)
             else:
                  # 如果没有找到路径，检查是否是因为没有录制数据
                  if "没有录制到任何音频数据" not in final_stdout:
                       print("警告: 未在标准输出中找到 '录音文件路径:' 行。", file=sys.stderr)

    except KeyboardInterrupt:
        print("\n--- 在测试脚本中检测到 Ctrl+C，正在尝试终止录音脚本... ---")
        if process and process.poll() is None: # 检查子进程是否仍在运行
            try:
                # 尝试优雅地发送 SIGINT (Ctrl+C 信号)
                # 注意：在 Windows 上，这可能不会像 Linux/macOS 那样直接触发 KeyboardInterrupt
                # 它更可能直接终止进程
                process.send_signal(signal.SIGINT)
                print("已发送 SIGINT 信号。等待子进程退出...")
                process.wait(timeout=5) # 等待最多5秒
            except subprocess.TimeoutExpired:
                print("子进程在 SIGINT 后未能在 5 秒内退出，强制终止...")
                process.terminate() # 更强制的终止
                process.wait() # 等待终止完成
            except Exception as sig_e:
                 print(f"发送信号时出错: {sig_e}。尝试强制终止...")
                 process.terminate()
                 process.wait()

        print("--- 测试脚本已停止 ---")

    except FileNotFoundError:
        print(f"错误: 找不到 Python 解释器或脚本文件 '{AUDIO_RECORDER_SCRIPT_PATH}'。", file=sys.stderr)
    except Exception as e:
        print(f"执行测试脚本时发生意外错误: {e}", file=sys.stderr)
        # 确保即使出错也尝试终止子进程
        if process and process.poll() is None:
            print("发生错误，尝试终止子进程...")
            process.terminate()
            process.wait()


if __name__ == "__main__":
    print("请确保您已激活 Python 虚拟环境...")
    print("----------------------------------------------------------")
    run_audio_recorder_interactive()