#!/usr/bin/env python3
import sys
sys.stdout.reconfigure(line_buffering=True)
"""
Wizard Card Controller
Monitors a reed switch (GPIO 26) and plays random wizard animations
on the ILI9341 SPI LCD via framebuffer when the lid opens.
"""

import os
import glob
import random
import signal
import subprocess
import time
import struct
import lgpio

# === Configuration ===
REED_SWITCH_PIN = 26        # GPIO 26 (physical pin 37)
ANIMATIONS_DIR = '/home/pi/animations'
FRAMEBUFFER = '/dev/fb0'
FB_WIDTH = 240
FB_HEIGHT = 320

# === Globals ===
ffmpeg_process = None
last_video = None
current_video = None
running = True


def clear_screen():
    """Fill framebuffer with black."""
    try:
        black = struct.pack('<H', 0x0000) * (FB_WIDTH * FB_HEIGHT)
        with open(FRAMEBUFFER, 'wb') as fb:
            fb.write(black)
    except Exception as e:
        print(f'[WARN] Could not clear screen: {e}')


def show_last_frame(video_path):
    """Extract and display the last frame of the video on the framebuffer."""
    try:
        cmd = [
            'ffmpeg', '-sseof', '-0.1', '-i', video_path,
            '-vframes', '1', '-vf', 'format=rgb565le',
            '-f', 'fbdev', '-y', FRAMEBUFFER
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
    except Exception as e:
        print(f'[WARN] Could not show last frame: {e}')


def get_random_video():
    """Pick a random video, avoiding the same one twice in a row."""
    global last_video
    videos = glob.glob(os.path.join(ANIMATIONS_DIR, '*.mp4'))
    if not videos:
        print('[ERROR] No .mp4 files found in', ANIMATIONS_DIR)
        return None
    if len(videos) == 1:
        last_video = videos[0]
        return videos[0]
    available = [v for v in videos if v != last_video]
    choice = random.choice(available)
    last_video = choice
    return choice


def stop_video():
    """Stop any running ffmpeg playback immediately."""
    global ffmpeg_process, current_video
    if ffmpeg_process and ffmpeg_process.poll() is None:
        ffmpeg_process.kill()  # Use kill instead of terminate for instant stop
        ffmpeg_process.wait()
    ffmpeg_process = None
    current_video = None


def play_video(video_path):
    """Start playing a video to the framebuffer (non-blocking)."""
    global ffmpeg_process, current_video
    stop_video()
    print(f'[PLAY] {os.path.basename(video_path)}')
    cmd = [
        'ffmpeg', '-re', '-i', video_path,
        '-vf', 'format=rgb565le',
        '-f', 'fbdev', '-y', FRAMEBUFFER
    ]
    ffmpeg_process = subprocess.Popen(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    current_video = video_path


def hide_cursor():
    """Hide the console cursor on tty1."""
    try:
        subprocess.run(['bash', '-c',
            'echo 0 > /sys/class/graphics/fbcon/cursor_blink 2>/dev/null; '
            'echo -e "\033[?25l" > /dev/tty1'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass


def signal_handler(sig, frame):
    """Clean shutdown on SIGTERM/SIGINT."""
    global running
    print('[SHUTDOWN] Cleaning up...')
    running = False
    stop_video()
    clear_screen()
    sys.exit(0)


def main():
    global running, ffmpeg_process, current_video
    global running

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    hide_cursor()
    clear_screen()

    print(f'[INIT] Wizard Card Controller started')
    print(f'[INIT] Reed switch on GPIO {REED_SWITCH_PIN}')
    print(f'[INIT] Animations dir: {ANIMATIONS_DIR}')

    videos = glob.glob(os.path.join(ANIMATIONS_DIR, '*.mp4'))
    print(f'[INIT] Found {len(videos)} animation(s)')

    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_input(h, REED_SWITCH_PIN, lgpio.SET_PULL_UP)

    lid_was_open = False
    video_finished = False

    print('[READY] Waiting for lid events...')

    while running:
        state = lgpio.gpio_read(h, REED_SWITCH_PIN)
        lid_is_open = (state == 1)  # HIGH = open (no magnet / wire disconnected)

        # --- Lid just opened ---
        if lid_is_open and not lid_was_open:
            print('[EVENT] Lid opened')
            video_finished = False
            video = get_random_video()
            if video:
                play_video(video)

        # --- Lid just closed ---
        elif not lid_is_open and lid_was_open:
            print('[EVENT] Lid closed')
            stop_video()
            clear_screen()
            video_finished = False

        # --- Lid is open and video just finished naturally ---
        elif lid_is_open and not video_finished:
            if ffmpeg_process and ffmpeg_process.poll() is not None:
                print('[EVENT] Video finished, showing last frame')
                if current_video:
                    show_last_frame(current_video)
                video_finished = True
                ffmpeg_process = None

        lid_was_open = lid_is_open
        time.sleep(0.1)


if __name__ == '__main__':
    main()
