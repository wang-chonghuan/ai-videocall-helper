"""
Test script for audio_recorder.py. Provides a simple interactive interface
to test recording capabilities.
"""

import sys
import os
import time
from queue import Queue

# Add the src directory to the path so we can import the AudioRecorder class
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from audio_recorder import AudioRecorder, AudioRecorderException


def print_header():
    """Print a header for the test application"""
    print("\n" + "="*60)
    print("WASAPI Audio Recorder Test Application")
    print("="*60)


def print_help():
    """Print available commands"""
    print("\nAvailable commands:")
    print("  list          - List all audio devices")
    print("  record [idx]  - Start recording (optionally from device with index idx)")
    print("  pause         - Pause current recording")
    print("  resume        - Resume paused recording")
    print("  stop          - Stop recording and save to file")
    print("  auto [sec]    - Automatically record for sec seconds (default: 5)")
    print("  exit/quit     - Exit the application")
    print("  help          - Show this help message")


def run_interactive_test():
    """Run an interactive test of the AudioRecorder class"""
    recorder = None
    current_recording = None
    
    print_header()
    print("This test application allows you to test the WASAPI loopback recording")
    print("functionality. You can record system audio and save it to a WAV file.")
    print_help()
    
    try:
        recorder = AudioRecorder()
        
        while True:
            try:
                command = input("\nEnter command: ").strip().lower().split()
                if not command:
                    continue
                
                cmd = command[0]
                args = command[1:] if len(command) > 1 else []
                
                if cmd in ["exit", "quit"]:
                    print("Exiting...")
                    break
                
                elif cmd == "help":
                    print_help()
                
                elif cmd == "list":
                    print("\nListing all audio devices:")
                    recorder.list_devices()
                
                elif cmd == "record":
                    if current_recording:
                        print("Already recording. Stop the current recording first.")
                    else:
                        try:
                            device_index = int(args[0]) if args else None
                            recorder.start_recording(device_index)
                            current_recording = True
                        except ValueError:
                            print(f"Invalid device index: {args[0]}")
                        except AudioRecorderException as e:
                            print(f"Recording error: {e}")
                
                elif cmd == "pause":
                    if current_recording:
                        recorder.pause_recording()
                    else:
                        print("Not currently recording.")
                
                elif cmd == "resume":
                    if current_recording:
                        recorder.resume_recording()
                    else:
                        print("No recording to resume.")
                
                elif cmd == "stop":
                    if current_recording:
                        recorder.stop_recording()
                        filename = recorder.save_recording()
                        if filename:
                            print(f"Recording saved to: {filename}")
                        current_recording = None
                    else:
                        print("Not currently recording.")
                
                elif cmd == "auto":
                    if current_recording:
                        print("Already recording. Stop the current recording first.")
                    else:
                        try:
                            duration = int(args[0]) if args else 5
                            print(f"Automatic recording for {duration} seconds...")
                            recorder.start_recording()
                            current_recording = True
                            
                            # Count down
                            for i in range(duration, 0, -1):
                                print(f"Recording... {i} seconds remaining", end="\r")
                                time.sleep(1)
                            print("\nFinished recording.                      ")
                            
                            recorder.stop_recording()
                            filename = recorder.save_recording()
                            if filename:
                                print(f"Recording saved to: {filename}")
                            current_recording = None
                        except ValueError:
                            print(f"Invalid duration: {args[0]}")
                        except AudioRecorderException as e:
                            print(f"Recording error: {e}")
                            current_recording = None
                
                else:
                    print(f"Unknown command: {cmd}")
                    print_help()
            
            except KeyboardInterrupt:
                if current_recording:
                    print("\nRecording interrupted.")
                    recorder.stop_recording()
                    filename = recorder.save_recording()
                    if filename:
                        print(f"Recording saved to: {filename}")
                    current_recording = None
                else:
                    print("\nInterrupted. Enter 'exit' to quit.")
            
            except Exception as e:
                print(f"Error: {e}")
                if current_recording:
                    try:
                        recorder.stop_recording()
                        current_recording = None
                    except:
                        pass
    
    except Exception as e:
        print(f"Fatal error: {e}")
    
    finally:
        if recorder:
            recorder.close()
        print("Test completed.")


if __name__ == "__main__":
    run_interactive_test()