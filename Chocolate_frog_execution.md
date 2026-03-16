---
title: "Chocolate Frog Tin - Execution Guide"
created: 2026-03-15
modified: 2026-03-15
version: 1.0
author: Claude Opus 4.6 (claude-opus-4-6)
tags:
---

# Chocolate Frog Tin - Execution Guide

This is the working file. It contains every step needed to build the animated wizard card, organized into sessions you can complete in one sitting. Check off tasks as you go. Refer to `Chocolate_frog_wizard_card_project.md` for specs, measurements, and shopping links.


## Session 1: Order Parts

**Goal:** Purchase Phase 1 components from Amazon.

- [x] Order Raspberry Pi Zero 2 WH (pre-soldered headers) - [Amazon link](https://www.amazon.com/Zero-Pre-Soldered-Color-Coded-Quad-Core-Bluetooth/dp/B0DS68NPGF)
- [x] Order Waveshare 2.4" SPI TFT LCD (ILI9341) - [Amazon link](https://www.amazon.com/Waveshare-2-4inch-Display-Resolution-Interface/dp/B08H24H7KX)
- [x] Order Samsung EVO Plus 32GB MicroSD - [Amazon link](https://www.amazon.com/Samsung-Class-Micro-Adapter-MB-MC32GA-AM/dp/B0749KG1JK)
- [x] Order Female-to-Female Dupont Jumper Wires (10cm, 40-pack) - [Amazon link](https://www.amazon.com/Female-Dupont-Jumper-Wires-Cable/dp/B00RLQE3E0)
- [x] Confirm you have a 5V micro-USB charger for desk testing (any old phone charger works)
- [x] Download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your MacBook


## Session 2: Flash SD Card and First Boot

**Goal:** Get the Pi booting headlessly and accessible over SSH from your Mac.

**What you do:**

- [x] Insert the MicroSD card into your Mac (use the SD adapter that comes with the Samsung card)
- [x] Open Raspberry Pi Imager
- [x] Select device: Raspberry Pi Zero 2 W
- [x] Select OS: Raspberry Pi OS Lite (32-bit) - found under "Raspberry Pi OS (other)"
- [x] Click the gear icon (or "Edit Settings") before writing and configure:
  - Set hostname: `wizardcard`
  - Enable SSH (use password authentication)
  - Set username: `pi`
  - Set a password you'll remember `harrypotter`
  - Configure your home Wi-Fi network (SSID and password)
  - Set locale/timezone
  - Skip "Raspberry Pi Connect" (not needed)
- [x] Write the image to the SD card
- [x] Eject the SD card from your Mac
- [x] Insert the SD card into the Pi Zero 2 WH
- [x] Plug in the micro-USB power cable (use the port labeled "PWR", not "USB")
- [x] Wait 60-90 seconds for first boot
- [x] From your Mac terminal, connect: `ssh pi@wizardcard.local`
- [x] Once connected, run `sudo apt update && sudo apt upgrade -y` to update the system

**Notes:**
- Pi IP address: 192.168.7.163
- OS installed: Raspbian Trixie (Debian 13), kernel 6.12, armv7l
- Imager version used: v2.0.6

**You're done when:** You can SSH into the Pi from your Mac terminal. ✅ COMPLETE


## Session 3: Wire and Configure the Display

**Goal:** Get the Waveshare 2.4" LCD showing an image driven by the Pi.

**What you do (wiring):**

Connect the LCD to the Pi using 8 dupont wires. The Pi WH has color-coded headers which makes this easier. Match these pins:

| LCD Pin | Pi Pin Name | Pi Physical Pin |
|---------|-------------|-----------------|
| VCC | 3.3V | Pin 1 |
| GND | GND | Pin 6 |
| DIN | SPI0 MOSI | Pin 19 |
| CLK | SPI0 SCLK | Pin 23 |
| CS | SPI0 CE0 | Pin 24 |
| DC | GPIO 25 | Pin 22 |
| RST | GPIO 27 | Pin 13 |
| BL | GPIO 18 | Pin 12 |

- [x] Power off the Pi (`sudo shutdown -h now`, then unplug)
- [x] Connect all 8 wires between the LCD and Pi
- [x] Double-check each connection against the table above
- [x] Plug the Pi back in and wait for it to boot
- [x] SSH in from your Mac
- [x] Claude Code enabled SPI, configured fbtft kernel driver, tested display

**What was actually done (by Claude Code via SSH):**

1. Enabled SPI: `sudo raspi-config nonint do_spi 0` + reboot
2. **Could NOT use fbcp-ili9341** — Raspbian Trixie removed legacy VideoCore libraries (`bcm_host.h` missing). This is a known issue with newer Pi OS.
3. Used **fbtft kernel module** instead (built into the kernel). Added to `/boot/firmware/config.txt`:
   ```
   dtoverlay=fbtft,spi0-0,ili9341,bgr,reset_pin=27,dc_pin=25,led_pin=18,rotate=0,speed=32000000,fps=60,width=240,height=320
   ```
4. After reboot, display registered as `/dev/fb0` (240x320, 16-bit RGB565)
5. Tested with random pixels and solid red — both displayed correctly

**Key lesson:** On Raspbian Trixie (Debian 13), use the `fbtft` dtoverlay instead of fbcp-ili9341. The framebuffer is `/dev/fb0`.

- [x] Confirm the LCD lights up and shows something (test pattern, console text, or a color)

**You're done when:** The LCD is displaying output from the Pi. ✅ COMPLETE


## Session 4: Test Video Playback

**Goal:** Play a video file on the small LCD and confirm smooth playback.

**What you do:**

- [x] Used existing wizard animation videos (from Session 5) as test videos
- [x] Installed ffmpeg on Pi: `sudo apt install -y ffmpeg`
- [x] Tested playback directly to framebuffer — smooth at ~25fps, real-time speed

**Playback tool that worked:** `ffmpeg` direct to framebuffer
**Settings/flags used:** `ffmpeg -re -i <video> -vf 'format=rgb565le' -f fbdev /dev/fb0`
**Performance:** 25 fps, 1.03-1.07x speed (smooth real-time playback)

**Fix applied:** Console cursor was blinking on top of video. Fixed by:
- Runtime: `echo 0 | tee /sys/class/graphics/fbcon/cursor_blink` + escape codes to tty1
- Permanent: Added `vt.global_cursor_default=0 consoleblank=0 logo.nologo` to `/boot/firmware/cmdline.txt`

**You're done when:** A video loops smoothly on the LCD. ✅ COMPLETE


## Session 5: Create Wizard Animations

**Goal:** Generate animated wizard portrait videos using Google Gemini VEO 3.1.

**What you do:**

This session is repeated for each wizard character. Start with Dumbledore as the test case.

- [x] Find or create a high-quality portrait still of the wizard character
- [x] Open Google Gemini and attach the reference image
- [x] Use the prompt below (customize the character name and details for each wizard)
- [x] Generate at 9:16 aspect ratio, 720p or 1080p, 8 seconds duration
- [x] Review the output - re-generate if needed

**Kling Video Prompt:**

```
Animate this reference image as a magical moving portrait. The camera is completely static and never moves - this is a portrait that has come to life. The background is a dark, richly detailed study with warm candlelight. The character stands in a medium shot from the waist up, centered 

in frame and looking at the camera. He begins still, then continues to look at the camera with a warm, knowing expression. He gives a gentle nod of acknowledgment, then raises one hand in a subtle, dignified wave. After the greeting, he turns and walks calmly out of frame to the right. The portrait background remains visible after he exits. The lighting is warm. The motion is slow, graceful, and deliberate. No camera movement at all.
```


**Huffelpuff** 
Animate this reference image as a magical moving portrait. The camera is completely static and never moves - this is a portrait that has come to life. The character stands in a medium shot centered in frame. She begins still, then looks at the camera with a warm, knowing expression. She gives a gentle nod of acknowledgment and a smile, then raises one hand in a subtle, dignified wave. After the greeting, she turns and walks calmly out of frame to the right. The portrait background remains visible after she exits. The lighting is warm. The motion is slow, graceful, and deliberate. No camera movement at all.

**Slythern** 
Animate this reference image as a magical moving portrait. The camera is completely static and never moves - this is a portrait that has come to life. The character stands in a medium shot centered in frame. He begins still, then looks at the camera with a cold, knowing expression. He gives a subtle, sinister tightening of the eyes and a small nod of acknowledgment. After he turns and walks calmly out of frame to the right. The portrait background remains visible after he exits. The lighting is cold. The motion is slow, graceful, and deliberate. No camera movement at all.

**Tips:**

- If the character doesn't walk out cleanly in 8 seconds, drop the hand wave and keep just the nod. That frees up more time for the exit.
- Try "walks out to the left" if right doesn't compose well.
- For female characters (Rowena Ravenclaw, Helga Hufflepuff), change "He/his" to "She/her" and "robes trailing" as needed.
- The style note "Renaissance oil painting" helps keep the painterly look. If VEO goes too photorealistic, try adding "painted texture, visible brushstrokes, oil on canvas" to the prompt.

**Character checklist:**

- [x] Godric Gryffindor
- [x] Salazar Slytherin
- [x] Rowena Ravenclaw
- [x] Helga Hufflepuff
- [x] Albus Dumbledore

**You're done when:** You have at least 2-3 finished animation files to test with.


## Session 6: Format Videos for the Display

**Goal:** Crop and resize the 9:16 Gemini output to 3:4 (240x320) for the LCD.

**What you do:**

- [x] All 5 videos gathered in Videos/ folder

**What Claude Code did:**

1. Cropped each video to 3:4 aspect ratio (trimming more from bottom, 25% top / 75% bottom split)
2. Resized to 240x320 pixels
3. Re-encoded with libx264, preset slow, CRF 23, no audio (`-an`)
4. Saved to Videos/formatted/

**Source video specs (from Kling):**
- dumbledore: 852x1076 (already near 3:4, cropped width instead)
- gryffindor: 752x1224
- hufflepuff: 752x1220
- ravenclaw: 736x1248
- slytherin: 752x1224
- All 24fps, 8 seconds, H.264

**Formatted file sizes:** 115-283 KB each (very small, perfect for Pi)

- [x] Reviewed cropped videos
- [x] Copied all formatted videos to Pi: `~/animations/`

**You're done when:** Formatted videos are on the Pi in `~/animations/` and play correctly. ✅ COMPLETE


## Session 7: Build the Control Script

**Goal:** Write the Python script that monitors the reed switch, picks a random video, and controls playback.

**What you do:**

- [x] Tested with jumper wire between GPIO 26 (pin 37) and GND (pin 39)

**What Claude Code did:**

1. Wrote `~/wizard-card.py` — Python script using gpiozero/lgpio that:
   - Monitors GPIO 26 with internal pull-up resistor
   - Wire disconnected (HIGH) = lid open → plays random video via ffmpeg to framebuffer
   - Wire connected to GND (LOW) = lid closed → stops video, clears screen to black
   - Avoids repeating the same video twice in a row
   - Shows last frame of video after playback finishes (stays on screen until lid closes)
   - Hides console cursor on startup
   - Handles SIGTERM/SIGINT for clean shutdown
2. Created systemd service at `/etc/systemd/system/wizard-card.service`
   - Runs as root (needed for GPIO and framebuffer access)
   - Auto-starts on boot, restarts on failure
3. Fixed: animations path hardcoded to `/home/pi/animations` (not `~/` which resolves to `/root/` when running as root)
4. Fixed: Added stdout line buffering so logs appear in `journalctl`

**Test results:**
- [x] Jumper wire disconnect → random wizard video plays ✅
- [x] Jumper wire reconnect → video stops, screen goes black ✅
- [x] Different video plays each time ✅
- [x] Auto-starts after reboot ✅

**Reed switch GPIO pin used:** GPIO 26 (physical pin 37), GND on physical pin 39

**You're done when:** The full open/close/random-select cycle works from a jumper wire, and it auto-starts on boot. ✅ COMPLETE


## Session 8: Order Phase 2 Parts

**Goal:** Purchase remaining components for the full wireless build.

**Change from original plan:** Replaced TP4056 + MT3608 + LiPo battery with **PiSugar 3** — an all-in-one battery module that attaches via pogo pins on the back of the Pi. No soldering required.

- [x] ~~Order JLJLUP 3.7V 2000mAh LiPo battery~~ → NOT NEEDED (PiSugar 3 has built-in battery)
- [x] ~~Order HiLetgo TP4056 USB-C charging module~~ → NOT NEEDED (PiSugar 3 has built-in charging)
- [x] ~~Order MT3608 boost converter~~ → NOT NEEDED (PiSugar 3 has built-in 5V boost)
- [x] PiSugar 3 (already owned) — replaces all three above
- [x] Order Gebildet reed switch 30-pack - [Amazon link](https://www.amazon.com/Gebildet-Normally-Magnetic-Induction-Miniature/dp/B07YDH998K)
- [ ] Check if the reed switch kit includes small magnets. If not, order 5x2mm neodymium magnets.
- [ ] Order 3M VHB 5952 tape (1/2" x 15ft, black) - [Amazon link](https://www.amazon.com/3M-Scotch-5952-VHB-Tape/dp/B01BT0A6MG)
- [ ] Order IIT double-sided foam tape 3-pack (3mm thick) - [Amazon link](https://www.amazon.com/IIT-Pack-Double-Sided-Thick/dp/B00534ES4W)


## Session 9: Wire the Reed Switch

**Goal:** Replace the jumper wire simulation with a real reed switch and magnet.

**What you do:**

- [ ] Take one reed switch from the kit
- [ ] Connect one leg to the GPIO pin used in Session 7
- [ ] Connect the other leg to GND (any GND pin on the Pi)
- [ ] Use dupont wires - no soldering needed
- [ ] Hold a magnet near the reed switch to simulate "lid closed"
- [ ] Move the magnet away to simulate "lid open"
- [ ] Confirm the video plays/stops just like the jumper wire test

**You're done when:** The reed switch + magnet triggers the same behavior as the jumper wire.


## Session 10: Battery Power (PiSugar 3)

**Goal:** Power the Pi from the PiSugar 3 battery instead of USB.

**Change from original plan:** Using PiSugar 3 instead of TP4056 + MT3608 + LiPo. No soldering, no wiring — just attach to the back of the Pi.

**What you do:**

- [x] Unplug the Pi from USB power
- [x] Attach the PiSugar 3 to the back of the Pi Zero 2 WH — screws go through Pi's corner holes into PiSugar's threaded standoffs
- [x] Power on using PiSugar button: **short press, then long press**
- [x] Wait for Pi to boot (~30-45 seconds)
- [x] Tested jumper wire — video plays/stops correctly on battery power ✅
- [ ] Test charging: plug USB-C cable into the PiSugar while system runs
- [ ] Check PiSugar web UI at http://wizardcard.local:8421 in your browser

**What Claude Code already did:**

1. Installed PiSugar Power Manager software (pisugar-server, pisugar-poweroff, pisugar-programmer)
2. Service auto-starts on boot
3. Web UI available at port 8421 for battery monitoring
4. Battery level check via: `echo get battery | nc -q 1 127.0.0.1 8423`
5. Also fixed boot cleanup:
   - Disabled getty@tty1 (removes "wizardcard login:" from LCD)
   - Added `quiet` to cmdline.txt (suppresses boot messages on LCD)
   - Pi now boots to black screen → wizard-card service starts
6. Fixed wizard-card.py to be non-blocking — lid close immediately kills video

**Battery at first test:** 88%

**You're done when:** The Pi runs entirely on PiSugar 3 battery and charges via USB-C. ✅ COMPLETE


## Session 11: Cut the Cardboard Mat

**Goal:** Create the printed card overlay that frames the LCD.

**What you do:**

- [ ] Design or find a Chocolate Frog card template (pentagon shaped, with the architectural frame, castle background, and character name banner)
- [ ] Print on heavy cardstock (300-350 gsm) or matte photo paper
- [ ] Measure your LCD's active display area (~49 x 37 mm)
- [ ] Mark the portrait window cutout on the printed mat, centered over where the LCD will sit
- [ ] Cut the portrait window with a precision knife (X-Acto)
- [ ] Leave a 1-2 mm black border around the cutout to hide LCD edges
- [ ] Hold the mat over the running LCD to check alignment

**You're done when:** The mat frames the LCD cleanly with no visible screen edges.


## Session 12: Final Assembly

**Goal:** Put everything inside the tin.

**What you do:**

- [ ] Lay out all components on a table and do a dry fit inside the tin (no tape yet)
- [ ] Plan placement: Pi diagonal in the base, battery alongside, power boards tucked in gaps
- [ ] Mount the Pi to the tin base with VHB tape
- [ ] Mount the battery with VHB tape
- [ ] Mount the TP4056 and MT3608 with VHB tape
- [ ] Attach foam tape spacers on top of the Pi/battery to create a platform for the LCD
- [ ] Mount the LCD face-up on the foam tape spacers
- [ ] Wire the reed switch and mount it near the lid edge with VHB tape
- [ ] Attach the magnet to the inside of the lid (align it with the reed switch position)
- [ ] Place the cardboard mat on top
- [ ] Close the lid and open it - does the animation play?

**You're done when:** The tin opens, a random wizard appears, and closing the lid turns it off.


## Session 13: Polish and Optimize

**Goal:** Fine-tune the experience.

**What Claude Code does:**

```
I have the wizard card tin fully assembled and working. The Pi is at
pi@wizardcard.local. Please help me:
1. Optimize boot time - disable unnecessary services so the Pi is ready faster
2. Add debouncing to the reed switch if it's triggering multiple times on open/close
3. Check that video transitions are clean (no flicker between stop and start)
4. Set up a clean shutdown mechanism (e.g., hold lid closed for 10 seconds = safe shutdown)
5. Test and report estimated battery life
```

- [ ] Boot time is acceptable (target: under 15 seconds to ready state)
- [ ] Reed switch doesn't double-trigger
- [ ] Video starts and stops cleanly
- [ ] Safe shutdown works
- [ ] Battery life tested and noted

**Measured boot time:** _______________
**Measured battery life:** _______________

**You're done when:** The tin works reliably every time you open it.
