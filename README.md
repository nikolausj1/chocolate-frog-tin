# Chocolate Frog Tin — Animated Wizard Card

A Raspberry Pi-powered animated wizard card that fits inside a Harry Potter Chocolate Frog tin. When the lid opens, a small LCD screen plays a randomly selected wizard portrait animation. When the lid closes, the screen goes dark. Just like magic.

## How It Works

1. A **reed switch** detects when the tin lid opens (magnet moves away)
2. A **Python script** picks a random wizard animation
3. **ffmpeg** plays the video directly to the LCD's framebuffer
4. When the lid closes, the video stops and the screen goes black
5. Everything runs on battery power via a **PiSugar 3**

## Hardware

| Component | Details |
|-----------|---------|
| **Computer** | Raspberry Pi Zero 2 WH (pre-soldered headers) |
| **Display** | Waveshare 2.4" ILI9341 SPI TFT LCD (240×320) |
| **Battery** | PiSugar 3 (1200mAh, USB-C charging) |
| **Trigger** | Gebildet reed switch + neodymium magnet |
| **Storage** | Samsung EVO Plus 32GB MicroSD |
| **OS** | Raspbian Trixie (Debian 13), headless |

## Characters

- Godric Gryffindor
- Salazar Slytherin
- Rowena Ravenclaw
- Helga Hufflepuff
- Albus Dumbledore

Animations were generated from still portraits using AI video tools (Kling), then cropped to 3:4 and resized to 240×320 for the LCD.

## Wiring

| LCD Pin | Pi Pin | Physical Pin |
|---------|--------|-------------|
| VCC | 3.3V | Pin 1 |
| GND | GND | Pin 6 |
| DIN | SPI0 MOSI | Pin 19 |
| CLK | SPI0 SCLK | Pin 23 |
| CS | SPI0 CE0 | Pin 24 |
| DC | GPIO 25 | Pin 22 |
| RST | GPIO 27 | Pin 13 |
| BL | GPIO 18 | Pin 12 |

Reed switch: GPIO 26 (Pin 37) to GND (Pin 39)

## Software Setup

### Display Driver

Uses the built-in `fbtft` kernel module. Add to `/boot/firmware/config.txt`:

```
dtparam=spi=on
dtoverlay=fbtft,spi0-0,ili9341,bgr,reset_pin=27,dc_pin=25,led_pin=18,rotate=0,speed=32000000,fps=60,width=240,height=320
```

### Boot Config

Add to `/boot/firmware/cmdline.txt`:
```
quiet vt.global_cursor_default=0 consoleblank=0 logo.nologo
```

Disable login prompt on LCD:
```
sudo systemctl disable getty@tty1
```

### Control Script

Copy `pi-files/wizard-card.py` to the Pi and install the systemd service:

```bash
# Copy files
scp pi-files/wizard-card.py pi@wizardcard.local:~/
sudo cp wizard-card.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wizard-card
sudo systemctl start wizard-card
```

### Video Playback

Videos play via ffmpeg direct to the framebuffer:
```
ffmpeg -re -i <video> -vf 'format=rgb565le' -f fbdev /dev/fb0
```

## Project Files

- `Chocolate_frog_wizard_card_project.md` — Full project specification
- `Chocolate_frog_execution.md` — Step-by-step build guide with lessons learned
- `pi-files/wizard-card.py` — Main control script
- `pi-files/wizard-card.service` — Systemd service file
- `pi-files/config.txt` — Boot config reference
- `pi-files/cmdline.txt` — Kernel command line reference
- `Videos/formatted/` — LCD-ready animations (240×320, 24fps)

## Key Lessons Learned

- **Raspbian Trixie (Debian 13)** removed the legacy VideoCore libraries, so `fbcp-ili9341` doesn't compile. Use the `fbtft` kernel dtoverlay instead.
- **ffmpeg direct to framebuffer** works great for video playback on SPI displays — no need for mpv or vlc.
- **PiSugar 3** eliminates all battery wiring (no soldering needed) — pogo pins connect through the back of the Pi.
- Hot glue dupont connectors to the GPIO header to prevent wires from coming loose.

## Built With

- [Claude Code](https://claude.ai) — All Pi software written and deployed via Claude Code over SSH
- Raspberry Pi Zero 2 WH
- Kling AI — Wizard portrait animations

## License

MIT
