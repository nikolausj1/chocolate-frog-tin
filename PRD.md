# Product Requirements Document: Animated Wizard Card

A Raspberry Pi-powered animated wizard card that fits inside a Harry Potter Chocolate Frog tin. When the lid opens, a small LCD screen plays a randomly selected wizard portrait animation. When the lid closes, the screen goes dark to save battery. A printed cardboard mat frames the screen to look like a real Chocolate Frog card from the films.

## Overview

The card is built from three visual layers, matching the design of the film props. The outer pentagon border and decorative architectural frame are printed on cardboard with a portrait-shaped cutout. Behind that cutout sits a small LCD screen driven by a Raspberry Pi Zero 2 WH.

A reed switch mounted near the lid edge detects a small magnet in the lid. When the lid opens, the magnet separates from the switch, the Pi wakes the display, picks a random animation file, and plays it. When the lid closes, the magnet triggers the switch again, the Pi kills playback and clears the screen to black.

The rectangular LCD does not need to match the pentagon shape of the tin. The cardboard mat hides the screen edges, so only the portrait window is visible. This is the key insight that makes the build simple.

## Characters

| Character | House | Animation Style |
|-----------|-------|-----------------|
| Godric Gryffindor | Gryffindor | Warm, noble greeting then walks away |
| Salazar Slytherin | Slytherin | Cold, sinister acknowledgment then walks away |
| Rowena Ravenclaw | Ravenclaw | Warm, knowing smile then walks away |
| Helga Hufflepuff | Hufflepuff | Warm, friendly wave then walks away |
| Albus Dumbledore | — | Warm, knowing nod and wave then walks away |

Animations are generated from still portrait images using [Kling](https://klingai.com/) (AI video generation). Each animation is 8 seconds at 24fps, formatted to 240x320 for the LCD. See the [Build Guide](BUILD_GUIDE.md) for the exact prompts used.

## Tin Measurements

The enclosure is a standard Chocolate Frog tin with a pentagonal base.

| Measurement | Value |
|-------------|-------|
| Shape | Regular pentagon |
| Side length | 68 mm |
| Vertex-to-vertex diagonal | ~110 mm |
| Side-to-opposite-vertex span | ~104.6 mm |
| Base cavity depth | 36 mm (vertical walls) |

The Pi Zero 2 WH (65 x 30 mm) fits easily when placed diagonally in the 110 mm base.

## Internal Stack

From top to bottom when the lid is open:

| Layer | Component |
|-------|-----------|
| Top (visible) | Printed cardboard mat with portrait cutout |
| Below mat | 2.4" LCD display module |
| Spacer | Foam tape |
| Base layer | Raspberry Pi Zero 2 WH + PiSugar 3 battery |
| Edge | Reed switch (near lid hinge) |

The portrait window in the mat targets roughly 40-45 mm wide by 50-60 mm tall, matching the proportions on the film cards.

## Hardware

### Components

| Component | Details | Approx. Cost |
|-----------|---------|-------------|
| **Raspberry Pi Zero 2 WH** | Pre-soldered color-coded headers, quad-core ARM, 512MB RAM, Wi-Fi. [Amazon](https://www.amazon.com/Zero-Pre-Soldered-Color-Coded-Quad-Core-Bluetooth/dp/B0DS68NPGF) | $18-28 |
| **Waveshare 2.4" SPI LCD** | ILI9341 controller, 240x320, 65K colors. Active area ~49x37mm. [Amazon](https://www.amazon.com/Waveshare-2-4inch-Display-Resolution-Interface/dp/B08H24H7KX) | $12-18 |
| **PiSugar 3** | All-in-one battery module (1200mAh LiPo, USB-C charging, 5V boost). Attaches via pogo pins — no soldering. | $35-45 |
| **32GB MicroSD** | Samsung EVO Plus, Class 10. [Amazon](https://www.amazon.com/Samsung-Class-Micro-Adapter-MB-MC32GA-AM/dp/B0749KG1JK) | $8-12 |
| **Dupont Wires** | Female-to-female, 10cm, 40-pack. [Amazon](https://www.amazon.com/Female-Dupont-Jumper-Wires-Cable/dp/B00RLQE3E0) | $5-7 |
| **Reed Switch Kit** | Gebildet 30-pack, normally open. [Amazon](https://www.amazon.com/Gebildet-Normally-Magnetic-Induction-Miniature/dp/B07YDH998K) | $7-9 |
| **Neodymium Magnets** | 5x2mm, for the lid. May be included in the reed switch kit. | $0-5 |
| **Micro-USB Power Supply** | Any 5V charger for desk testing. You probably already have one. | $0 |

**Estimated total: $85-124**

### Tools

| Tool | Purpose |
|------|---------|
| **Hot glue gun** | Secure dupont connectors to GPIO header |
| **Laser cutter** (e.g., Xtool F1Ultra) | Cut the portrait window from the cardboard mat using [`printables/wizard-card-cutout.pdf`](printables/wizard-card-cutout.pdf) |
| **Color printer** | Print the card template from [`printables/wizard-card-print.pdf`](printables/wizard-card-print.pdf) on heavy cardstock |
| **3M VHB tape** | Mount components inside the tin |
| **Foam tape** | Create spacer layer between Pi and LCD |

> **No soldering required.** The Pi Zero 2 WH has pre-soldered headers, the PiSugar 3 connects via pogo pins, and the LCD uses dupont wires.

## Software Architecture

The Pi runs **Raspberry Pi OS Lite** (Raspbian Trixie / Debian 13). All software is deployed from a Mac via SSH using [Claude Code](https://claude.ai).

### Boot Sequence

1. Pi boots into OS Lite (no desktop)
2. systemd launches `wizard-card.service`
3. `wizard-card.py` initializes GPIO monitoring on pin 26
4. Script waits for lid-open signal

### On Lid Open

1. Reed switch opens (HIGH) → lid is open
2. Pick a random `.mp4` from `~/animations/` (avoids repeating the last one)
3. Play video to framebuffer via ffmpeg
4. When video ends, show last frame (stays on screen)

### On Lid Close

1. Reed switch closes (LOW) → lid is closed
2. Immediately kill ffmpeg process (non-blocking)
3. Clear framebuffer to black

### Display Driver

Uses the `fbtft` kernel module (built into the kernel). Configured via device tree overlay in `/boot/firmware/config.txt`:

```
dtoverlay=fbtft,spi0-0,ili9341,bgr,reset_pin=27,dc_pin=25,led_pin=18,rotate=0,speed=32000000,fps=60,width=240,height=320
```

> **Note:** The commonly recommended `fbcp-ili9341` driver does **not** compile on Raspbian Trixie because the legacy VideoCore libraries (`bcm_host.h`) have been removed. Use the `fbtft` dtoverlay instead.

### Video Playback

```bash
ffmpeg -re -i <video> -vf 'format=rgb565le' -f fbdev /dev/fb0
```

Achieves ~25fps real-time playback on the Pi Zero 2 WH.

## Printables

Two PDF templates are included in the [`printables/`](printables/) folder:

| File | Purpose |
|------|---------|
| [`wizard-card-print.pdf`](printables/wizard-card-print.pdf) | Full card template — print on heavy cardstock (300-350gsm) with a color printer |
| [`wizard-card-cutout.pdf`](printables/wizard-card-cutout.pdf) | Portrait window outline — send to a laser cutter (Xtool F1Ultra or similar) to cut the viewing window |

## Pi Deployment Files

Everything needed to set up the Pi is in the [`pi-files/`](pi-files/) folder:

| File | Purpose |
|------|---------|
| `wizard-card.py` | Main control script (GPIO monitoring, video playback) |
| `wizard-card.service` | systemd service for auto-start on boot |
| `config.txt` | Reference `/boot/firmware/config.txt` with display overlay |
| `cmdline.txt` | Reference kernel command line (cursor hidden, quiet boot) |
| `*.mp4` | Pre-formatted 240x320 wizard animations, ready to copy to `~/animations/` |

## Design Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Characters | Hogwarts founders + Dumbledore | Iconic, recognizable, good variety |
| Animation source | Kling (AI video) | Best quality for portrait-to-video animation |
| Display driver | fbtft kernel module | Only option that works on Raspbian Trixie |
| Video playback | ffmpeg to framebuffer | Smooth 25fps, no desktop environment needed |
| Battery | PiSugar 3 | No soldering, USB-C charging, pogo pin connection |
| Lid detection | Reed switch + magnet | Simple, reliable, no moving parts |
| Connections | Dupont wires + hot glue | No soldering required, secure with hot glue |
| Card overlay | Printed cardstock + laser-cut window | Clean look, hides LCD bezel |

## Future Enhancements

- **Wireless animation uploads** — Push new wizard videos over Wi-Fi without opening the tin
- **Motion sensor** — PIR sensor to activate animation when someone approaches
- **Sound effects** — Mini speaker for magical ambience or character-specific audio
- **More characters** — Expand the animation library beyond the initial 5
