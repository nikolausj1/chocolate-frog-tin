# Build Guide: Animated Wizard Card in a Chocolate Frog Tin

A step-by-step guide to building a Raspberry Pi-powered animated wizard card that lives inside a Harry Potter Chocolate Frog tin. Open the lid and a randomly selected wizard portrait comes to life on a tiny LCD. Close it and the screen goes dark. Just like magic.

This guide is organized into sessions -- each one is roughly a single sitting's worth of work.

---

## What You're Building

Three visual layers create the illusion:

1. **Printed card overlay** -- a Chocolate Frog card printed on heavy cardstock with a portrait-shaped cutout
2. **Small LCD screen** -- a 2.4" SPI display driven by the Pi, visible through the cutout
3. **Electronics underneath** -- Pi Zero, battery, reed switch, all hidden inside the tin

A reed switch near the lid edge detects a magnet. Lid opens, magnet moves away, video plays. Lid closes, magnet returns, screen goes black.

---

## Parts List

### Phase 1: Core Electronics

| Part | Notes |
|------|-------|
| [Raspberry Pi Zero 2 WH](https://www.amazon.com/Zero-Pre-Soldered-Color-Coded-Quad-Core-Bluetooth/dp/B0DS68NPGF) | Pre-soldered headers -- no soldering needed |
| [Waveshare 2.4" SPI TFT LCD (ILI9341)](https://www.amazon.com/Waveshare-2-4inch-Display-Resolution-Interface/dp/B08H24H7KX) | 240x320, ILI9341 controller |
| [Samsung EVO Plus 32GB MicroSD](https://www.amazon.com/Samsung-Class-Micro-Adapter-MB-MC32GA-AM/dp/B0749KG1JK) | Plenty of space for the OS and videos |
| [Female-to-Female Dupont Jumper Wires (10cm)](https://www.amazon.com/Female-Dupont-Jumper-Wires-Cable/dp/B00RLQE3E0) | 40-pack, you need 10 |
| 5V micro-USB charger | Any old phone charger works for desk testing |

### Phase 2: Battery and Trigger

| Part | Notes |
|------|-------|
| PiSugar 3 | All-in-one battery + charging + 5V boost. Attaches via pogo pins on the back of the Pi. No soldering. Replaces the need for separate LiPo + TP4056 + MT3608. |
| [Gebildet Reed Switch 30-pack](https://www.amazon.com/Gebildet-Normally-Magnetic-Induction-Miniature/dp/B07YDH998K) | You only need one, but they're fragile -- nice to have spares |
| Small neodymium magnets | Check if the reed switch kit includes magnets. If not, get 5x2mm neodymium disc magnets. |

### Phase 2: Mounting

| Part | Notes |
|------|-------|
| 3M VHB 5952 tape | Black, strong permanent bond for mounting Pi and battery |
| Double-sided foam tape (3mm thick) | Creates spacer layer between Pi and LCD |

### Tools

- Raspberry Pi Imager (free download from [raspberrypi.com](https://www.raspberrypi.com/software/))
- A computer with SSH (Mac, Windows, or Linux)
- A laser cutter for the card cutout (optional -- you can cut by hand with a craft knife)
- A color printer and heavy cardstock (300-350 gsm)

---

## Session 1: Flash the SD Card and First Boot

**Goal:** Get the Pi booting headlessly and accessible over SSH.

1. Download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Insert the MicroSD card into your computer (use the SD adapter that comes with the Samsung card)
3. Open Raspberry Pi Imager and configure:
   - **Device:** Raspberry Pi Zero 2 W
   - **OS:** Raspberry Pi OS Lite (32-bit) -- found under "Raspberry Pi OS (other)"
   - Click the gear icon (or "Edit Settings") **before** writing and set:
     - Hostname: `wizardcard`
     - Enable SSH with password authentication
     - Username: `pi`
     - Password: something you'll remember
     - Your Wi-Fi network name and password
     - Your locale and timezone
4. Write the image to the SD card
5. Eject the SD card, insert it into the Pi Zero 2 WH
6. Plug in the micro-USB power cable (use the port labeled **PWR**, not "USB")
7. Wait 60-90 seconds for first boot
8. From your terminal, connect:
   ```
   ssh pi@wizardcard.local
   ```
9. Update the system:
   ```
   sudo apt update && sudo apt upgrade -y
   ```

**You're done when:** You can SSH into the Pi from your terminal.

> **Note:** The OS that installs is Raspbian Trixie (Debian 13). This matters later for the display driver.

---

## Session 2: Wire and Configure the Display

**Goal:** Get the Waveshare 2.4" LCD showing output from the Pi.

### Wiring

Power off the Pi first (`sudo shutdown -h now`, then unplug). Connect the LCD to the Pi using 8 dupont wires:

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

The Pi Zero 2 WH has color-coded headers, which makes it easier to find the right pins. Double-check each connection against the table before powering on.

### Software Configuration

Plug the Pi back in, wait for boot, and SSH in.

1. **Enable SPI:**
   ```
   sudo raspi-config nonint do_spi 0
   sudo reboot
   ```

2. **Configure the display driver.** Add this line to the end of `/boot/firmware/config.txt`:
   ```
   dtoverlay=fbtft,spi0-0,ili9341,bgr,reset_pin=27,dc_pin=25,led_pin=18,rotate=0,speed=32000000,fps=60,width=240,height=320
   ```
   Also make sure `dtparam=spi=on` is present (it should already be there after step 1).

3. **Reboot:**
   ```
   sudo reboot
   ```

4. **Verify the display registered:**
   ```
   ls /dev/fb0
   ```
   You should see `/dev/fb0`. The display should have lit up with a white or garbled screen -- that's normal and means it's working.

5. **Quick test -- fill the screen with red:**
   ```
   python3 -c "
   import struct
   red = struct.pack('<H', 0xF800) * (240 * 320)
   with open('/dev/fb0', 'wb') as f:
       f.write(red)
   "
   ```

**You're done when:** The LCD displays a solid red screen (or any color you choose).

> **Key lesson:** On Raspbian Trixie (Debian 13), the legacy VideoCore libraries are gone, so `fbcp-ili9341` will not compile. Use the built-in `fbtft` kernel dtoverlay instead. It creates a standard framebuffer at `/dev/fb0`.

A reference copy of the full config.txt is in `pi-files/config.txt`.

---

## Session 3: Test Video Playback

**Goal:** Play a video on the LCD and confirm smooth playback.

1. **Install ffmpeg:**
   ```
   sudo apt install -y ffmpeg
   ```

2. **Copy a test video to the Pi.** If you already have formatted videos (see Session 5), use one of those. Otherwise, any short MP4 will do:
   ```
   scp your-video.mp4 pi@wizardcard.local:~/
   ```

3. **Play it directly to the framebuffer:**
   ```
   ffmpeg -re -i ~/your-video.mp4 -vf 'format=rgb565le' -f fbdev /dev/fb0
   ```
   The `-re` flag plays at real-time speed. You should see smooth playback at around 25 fps.

4. **Fix the blinking cursor.** You'll probably see a console cursor blinking on top of the video. Fix it permanently by adding these flags to `/boot/firmware/cmdline.txt` (append to the existing single line -- do **not** create a new line):
   ```
   vt.global_cursor_default=0 consoleblank=0 logo.nologo
   ```
   Also add `quiet` to suppress boot messages on the LCD.

   A reference copy of the full cmdline.txt is in `pi-files/cmdline.txt`.

5. **Disable the login prompt on the LCD:**
   ```
   sudo systemctl disable getty@tty1
   ```

6. Reboot and test again. The Pi should now boot to a clean black screen with no cursor or text.

**You're done when:** A video plays smoothly on the LCD with no cursor or boot text.

---

## Session 4: Create Wizard Animations

**Goal:** Generate animated wizard portrait videos using AI video tools.

You need short (around 8-second) animations of wizard portraits coming to life. The approach: start with a high-quality still portrait of each character, then use [Kling](https://klingai.com/) (or a similar AI video generation tool) to animate it.

### Settings

- Aspect ratio: **9:16** (portrait)
- Resolution: 720p or 1080p
- Duration: **8 seconds**

### Kling Prompts

**Generic male wizard (Godric Gryffindor, Albus Dumbledore):**

```
Animate this reference image as a magical moving portrait. The camera is completely
static and never moves - this is a portrait that has come to life. The background is
a dark, richly detailed study with warm candlelight. The character stands in a medium
shot from the waist up, centered in frame and looking at the camera. He begins still,
then continues to look at the camera with a warm, knowing expression. He gives a
gentle nod of acknowledgment, then raises one hand in a subtle, dignified wave. After
the greeting, he turns and walks calmly out of frame to the right. The portrait
background remains visible after he exits. The lighting is warm. The motion is slow,
graceful, and deliberate. No camera movement at all.
```

**Female wizards (Helga Hufflepuff, Rowena Ravenclaw):**

```
Animate this reference image as a magical moving portrait. The camera is completely
static and never moves - this is a portrait that has come to life. The character
stands in a medium shot centered in frame. She begins still, then looks at the camera
with a warm, knowing expression. She gives a gentle nod of acknowledgment and a smile,
then raises one hand in a subtle, dignified wave. After the greeting, she turns and
walks calmly out of frame to the right. The portrait background remains visible after
she exits. The lighting is warm. The motion is slow, graceful, and deliberate. No
camera movement at all.
```

**Salazar Slytherin (darker tone):**

```
Animate this reference image as a magical moving portrait. The camera is completely
static and never moves - this is a portrait that has come to life. The character
stands in a medium shot centered in frame. He begins still, then looks at the camera
with a cold, knowing expression. He gives a subtle, sinister tightening of the eyes
and a small nod of acknowledgment. After he turns and walks calmly out of frame to
the right. The portrait background remains visible after he exits. The lighting is
cold. The motion is slow, graceful, and deliberate. No camera movement at all.
```

### Tips for Better Results

- If the character doesn't walk out of frame cleanly within 8 seconds, **drop the hand wave** from the prompt. That frees up time for the exit animation.
- Try **"walks out to the left"** if the right-side exit doesn't compose well with your portrait.
- If results look too photorealistic, add **"painted texture, visible brushstrokes, oil on canvas"** to keep the painterly look of the film cards.
- You'll likely need to generate several variations and pick the best one for each character.

### Characters

Generate animations for as many of these as you like:

- Godric Gryffindor
- Salazar Slytherin
- Rowena Ravenclaw
- Helga Hufflepuff
- Albus Dumbledore

**You're done when:** You have at least 2-3 finished animation files.

---

## Session 5: Format Videos for the Display

**Goal:** Crop and resize the 9:16 Kling output to 3:4 (240x320) for the LCD.

The videos from Kling are tall and high-resolution. The LCD is 240x320, so you need to crop to a 3:4 aspect ratio and scale down.

Run this ffmpeg command for each video (on your computer, not the Pi):

```bash
ffmpeg -i input.mp4 \
  -vf "crop=iw:iw*4/3:0:ih*0.25,scale=240:320" \
  -c:v libx264 -preset slow -crf 23 -an \
  output.mp4
```

What this does:
- **crop** -- takes a 3:4 slice from the frame, offset 25% from the top (favoring the upper body over the feet)
- **scale** -- resizes to exactly 240x320
- **libx264 preset slow CRF 23** -- good quality at tiny file sizes
- **-an** -- strips audio (the LCD has no speaker)

Expected file sizes: **115-283 KB per video**. These are tiny files that the Pi handles easily.

### Copy to the Pi

The repo's `pi-files/` folder mirrors the Pi's home directory structure, so a single recursive copy puts everything in the right place:

```bash
scp -r pi-files/* pi@wizardcard.local:~/
```

This copies the animations into `~/animations/` on the Pi (along with the control script and config files).

### Verify on the Pi

```bash
ssh pi@wizardcard.local
ffmpeg -re -i ~/animations/gryffindor.mp4 -vf 'format=rgb565le' -f fbdev /dev/fb0
```

**You're done when:** Formatted videos are on the Pi in `~/animations/` and play correctly on the LCD.

---

## Session 6: Install the Control Script

**Goal:** Set up the Python script that monitors the reed switch, picks a random video, and controls playback.

The control script and systemd service are provided in the `pi-files/` directory of this repo.

### What the Script Does

- Monitors GPIO 26 with an internal pull-up resistor
- **Reed switch open** (HIGH, lid open) -- plays a random video via ffmpeg to the framebuffer
- **Reed switch closed** (LOW, lid closed) -- immediately kills the video and clears the screen to black
- Avoids repeating the same video twice in a row
- Shows the last frame of the video after playback finishes (portrait stays on screen until you close the lid)
- Hides the console cursor on startup
- Handles SIGTERM/SIGINT for clean shutdown

### Deploy to the Pi

If you haven't already copied the repo files over (from Session 5), do it now:

```bash
scp -r pi-files/* pi@wizardcard.local:~/
```

Then SSH in and install the service:

```bash
ssh pi@wizardcard.local
sudo cp ~/wizard-card.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wizard-card
sudo systemctl start wizard-card
```

### Test with a Jumper Wire

Before you have a reed switch, you can simulate one with a jumper wire:

1. Connect a dupont wire from **GPIO 26 (physical pin 37)** to **GND (physical pin 39)**
2. The script sees this as "lid closed" (LOW) -- screen stays black
3. Disconnect the wire -- the script sees "lid open" (HIGH) and plays a video
4. Reconnect the wire -- video stops, screen goes black

### Check the Logs

```bash
ssh pi@wizardcard.local "sudo journalctl -u wizard-card -f"
```

You should see output like:
```
[INIT] Wizard Card Controller started
[INIT] Reed switch on GPIO 26
[INIT] Found 5 animation(s)
[READY] Waiting for lid events...
[EVENT] Lid opened
[PLAY] gryffindor.mp4
[EVENT] Lid closed
```

### Verify Auto-Start on Boot

Reboot the Pi (`sudo reboot`). After it comes back up, the service should start automatically. Disconnect the jumper wire -- a video should play without you needing to SSH in.

**You're done when:** The full open/close/random-select cycle works, and the service auto-starts on boot.

> **Tip:** The script runs as root (needed for GPIO and framebuffer access). The animations path is hardcoded to `/home/pi/animations`, not `~/animations`, because `~` would resolve to `/root/` when running as root.

---

## Session 7: Wire the Reed Switch

**Goal:** Replace the jumper wire with a real reed switch and magnet.

1. Take one reed switch from the Gebildet kit
2. Connect one leg to **GPIO 26 (physical pin 37)** using a dupont wire
3. Connect the other leg to **GND (any GND pin)** using a dupont wire
4. Hold a magnet near the reed switch -- this simulates "lid closed," screen should be black
5. Move the magnet away -- this simulates "lid open," a video should play
6. Confirm the same behavior as the jumper wire test

Reed switches are glass and fragile -- handle them gently.

**You're done when:** The reed switch + magnet triggers the same behavior as the jumper wire.

---

## Session 8: Battery Power (PiSugar 3)

**Goal:** Power the Pi from the PiSugar 3 battery instead of USB.

### Attach the PiSugar

1. Unplug the Pi from USB power
2. Attach the PiSugar 3 to the back of the Pi Zero 2 WH -- the screws go through the Pi's corner mounting holes into the PiSugar's threaded standoffs
3. Power on: **short press the PiSugar button, then long press**
4. Wait 30-45 seconds for boot

### Install PiSugar Software (Optional)

If you want battery monitoring via a web UI:

```bash
curl https://cdn.pisugar.com/release/pisugar-power-manager.sh | sudo bash
```

This gives you:
- A web UI at `http://wizardcard.local:8421`
- Battery level check: `echo get battery | nc -q 1 127.0.0.1 8423`

### Test

- Disconnect from USB -- the Pi should keep running on battery
- Test the reed switch / jumper wire -- video should play and stop as before
- Plug USB-C into the PiSugar to charge while running

**You're done when:** The Pi runs entirely on battery power and charges via USB-C.

> **Tip:** Hot glue the dupont connectors where they meet the GPIO header. This prevents wires from coming loose when everything is packed into the tin.

---

## Session 9: Print and Cut the Card Overlay

**Goal:** Create the printed card that frames the LCD.

### Print the Card

Print `printables/wizard-card-print.pdf` on heavy cardstock (300-350 gsm) or matte photo paper using a color printer. This is the full Chocolate Frog card template with the decorative border, frame, and character name.

### Cut the Portrait Window

The portrait window is the rectangular cutout where the LCD will be visible. You have two options:

**Option A: Laser cutter (recommended)**

Use `printables/wizard-card-cutout.pdf` with a laser cutter (tested with an xTool F1 Ultra, but any similar cutter should work). This gives you a clean, precise cutout.

**Option B: By hand**

Measure the LCD's active display area (approximately 49 x 37 mm). Mark the portrait window on the printed card, centered over where the LCD will sit. Cut carefully with a craft knife and straightedge.

### Check the Fit

Hold the card over the LCD. The printed border should hide the screen edges completely, with only the portrait window showing the display underneath. Adjust if needed.

**You're done when:** The printed card frames the LCD cleanly with no visible screen edges.

---

## Session 10: Final Assembly

**Goal:** Put everything inside the Chocolate Frog tin.

1. **Dry fit first.** Lay all components on a table and arrange them inside the tin without any tape. The Pi Zero 2 WH (65x30mm) fits diagonally in the pentagonal base.

2. **Mount the base layer.** Attach the Pi + PiSugar to the tin base with VHB tape.

3. **Create the spacer layer.** Apply foam tape on top of the Pi/battery assembly to create a level platform for the LCD.

4. **Mount the LCD.** Place the LCD face-up on the foam tape spacers.

5. **Position the reed switch.** Mount it near the lid edge with VHB tape, with dupont wires running to GPIO 26 and GND.

6. **Attach the magnet.** Stick a neodymium magnet to the inside of the tin lid, aligned with the reed switch position. When the lid closes, the magnet should sit directly over the reed switch.

7. **Place the card overlay.** Set the printed cardstock mat on top, portrait window aligned over the LCD.

**You're done when:** You open the tin, a random wizard appears on screen, and closing the lid turns it off.

---

## Session 11: Polish and Optimize

**Goal:** Fine-tune the experience for daily use.

### Boot Time

The Pi should be ready within 15-20 seconds of power-on. To speed things up:

```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable hciuart
sudo systemctl disable avahi-daemon
sudo systemctl disable triggerhappy

# Check what's slow
systemd-analyze blame
```

### Reed Switch Debouncing

If the reed switch triggers multiple times on a single open/close, the script's 100ms polling interval (the `time.sleep(0.1)` in the main loop) usually handles this. If you still see double-triggers, increase the sleep to 0.15 or 0.2.

### Clean Shutdown

To safely shut down the Pi (preserves the SD card):

```bash
ssh pi@wizardcard.local "sudo shutdown -h now"
```

The PiSugar 3 software can also be configured to auto-shutdown at a low battery threshold via its web UI.

### Battery Life

Battery life depends on your PiSugar model and how often the tin is opened. The Pi Zero 2 W draws roughly 100-150mA idle, more during video playback. With a 1200mAh PiSugar 3 battery, expect a few hours of standby time with intermittent use.

---

## File Reference

All Pi deployment files are in the `pi-files/` directory:

| File | Purpose |
|------|---------|
| `pi-files/wizard-card.py` | Main control script (GPIO monitoring, video playback) |
| `pi-files/wizard-card.service` | Systemd service for auto-start on boot |
| `pi-files/config.txt` | Reference `/boot/firmware/config.txt` with display driver config |
| `pi-files/cmdline.txt` | Reference `/boot/firmware/cmdline.txt` with boot flags |

Printable card files:

| File | Purpose |
|------|---------|
| `printables/wizard-card-print.pdf` | Full card template for color printing on heavy cardstock |
| `printables/wizard-card-cutout.pdf` | Portrait window cutout file for laser cutter (xTool F1 Ultra or similar) |

Pre-formatted videos are in `pi-files/animations/` (240x320, 24fps, H.264, no audio). The `scp -r pi-files/*` command copies them to `~/animations/` on the Pi automatically.

---

## Wiring Reference

### LCD (Waveshare 2.4" ILI9341)

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

### Reed Switch

| Reed Switch Leg | Pi Physical Pin |
|-----------------|-----------------|
| Leg 1 | Pin 37 (GPIO 26) |
| Leg 2 | Pin 39 (GND) |

---

## Lessons Learned

- **Raspbian Trixie broke fbcp-ili9341.** Debian 13 removed the legacy VideoCore libraries (`bcm_host.h`), so the popular fbcp-ili9341 driver won't compile. The built-in `fbtft` kernel dtoverlay works great as a replacement.

- **ffmpeg direct to framebuffer is all you need.** No need for mpv, vlc, or any video player. `ffmpeg -re` with `-f fbdev /dev/fb0` gives smooth real-time playback on the SPI display.

- **PiSugar 3 eliminates all battery wiring.** It replaces a LiPo battery + TP4056 charger + MT3608 boost converter with a single board that connects via pogo pins. No soldering at all.

- **Hot glue your dupont connectors.** Once everything is working and packed into the tin, a dab of hot glue on each dupont connector where it meets the header prevents wires from wiggling loose.

- **The cardboard mat is the secret weapon.** The rectangular LCD doesn't need to match the tin's pentagon shape. The printed card overlay hides all the edges, so only the portrait window is visible. This is what makes the build look polished despite simple mounting.

- **Run the script as root.** GPIO and framebuffer access require root. The systemd service handles this, but remember that `~/` resolves to `/root/` -- so hardcode `/home/pi/animations` in the script.

- **Add `quiet` and cursor-hiding flags early.** Nothing breaks the illusion like boot messages and a blinking cursor on the LCD. Set these up before final assembly so you don't have to pull the SD card later.
