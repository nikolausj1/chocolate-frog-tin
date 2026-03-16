---
title: "Chocolate Frog Tin - Animated Wizard Card"
created: 2026-03-11
modified: 2026-03-12
version: 4.0
author: Claude Opus 4.6 (claude-opus-4-6)
tags:
---

# Chocolate Frog Tin - Animated Wizard Card

A Raspberry Pi-powered animated wizard card that fits inside a Chocolate Frog tin. When the lid opens, a small LCD screen plays a looping animation of a randomly selected Harry Potter wizard portrait. When the lid closes, the screen goes dark to save battery. The surrounding printed cardboard mat frames the screen to look like a real Chocolate Frog card from the films.

## Decisions

| Decision            | Detail                                                                               |
| ------------------- | ------------------------------------------------------------------------------------ |
| Characters          | Founding Hogwarts wizards                                                            |
| Animation source    | Stills animated with AI video tools (owner handles creative)                         |
| Animation selection | Random wizard chosen each time the tin is opened                                     |
| Lid close behavior  | Screen goes fully dark to preserve battery                                           |
| Hardware source     | Amazon.com preferred, expand to other sources if needed                              |
| Development tool    | Claude app (Claude Code) on MacBook Pro M1 for all Pi software                       |
| Soldering comfort   | Low - no soldering; Pi WH has pre-soldered headers, all connections via dupont wires |
| Screen cover        | Cardboard mat placed directly over screen (no acrylic)                               |
| Tins on hand        | Two Chocolate Frog tins ready to go                                                  |
| Build pace          | Phased, worked on in free time                                                       |


## How It Works

The card is built from three visual layers, matching the design of the film props. The outer pentagon border and decorative architectural frame are printed on cardboard with a portrait-shaped cutout. Behind that cutout sits a small LCD screen driven by a Raspberry Pi Zero 2 WH.

A reed switch mounted near the lid edge detects a small magnet in the lid. When the lid opens, the magnet separates from the switch, the Pi wakes the display, picks a random animation file, and starts looping it. When the lid closes, the magnet triggers the switch again and the Pi kills playback and turns off the backlight.

The rectangular LCD does not need to match the pentagon shape of the tin. The cardboard mat hides the screen edges, so only the portrait window is visible. This is the key insight that makes the build simple.


## Tin Measurements

The enclosure is a standard Chocolate Frog tin with a pentagonal base.

| Measurement | Value |
|-------------|-------|
| Shape | Regular pentagon |
| Side length | 68 mm |
| Vertex-to-vertex diagonal | ~110 mm |
| Side-to-opposite-vertex span | ~104.6 mm |
| Base cavity depth | 36 mm (vertical walls) |

The pyramid slope exists only in the lid, which holds no electronics. The Pi Zero 2 WH (65 x 30 mm) fits easily when placed diagonally in the 110 mm base.


## Internal Stack

From top to bottom when the lid is open:

| Position | Component |
|----------|-----------|
| Top (visible) | Printed cardboard mat with portrait cutout |
| Below mat | 2.4" LCD display module |
| Spacer | Foam tape |
| Base layer | Raspberry Pi Zero 2 WH + battery + power electronics |
| Edge | Reed switch (near lid hinge) |

The portrait window in the mat targets roughly 40-45 mm wide by 50-60 mm tall, matching the proportions on the film cards. A 1-2 mm black border around the cutout hides the LCD bezel.


## Software

The Pi runs Raspberry Pi OS Lite. All software will be written and deployed from a MacBook Pro M1 using Claude Code over Wi-Fi/SSH.

**Boot sequence:**

1. Pi boots into OS Lite (no desktop)
2. systemd service launches the wizard-card control script
3. Script initializes GPIO for reed switch monitoring
4. Script waits for lid-open signal

**On lid open:**

1. Pick a random `.mp4` file from the `animations/` folder
2. Turn on display backlight
3. Play video fullscreen in a loop

**On lid close:**

1. Kill video playback
2. Turn off display backlight
3. Return to waiting state

**Playback tool** is TBD. Candidates include `mpv`, `vlc`, or a Python framebuffer approach, depending on what achieves smooth playback on the SPI display. The driver `fbcp-ili9341` may be needed to push the SPI bus past its default ~15 FPS limit toward 30+ FPS.

**Project file structure:**

```
wizard-card/
  animations/
    dumbledore.mp4
    gryffindor.mp4
    ravenclaw.mp4
    hufflepuff.mp4
    slytherin.mp4
  scripts/
    wizard-card.py
    start-animation.sh
  config/
    autostart.service
    display-config.txt
```


## Shopping List

This is the Phase 1 purchase list for prototyping the Pi + display outside the tin, plus the remaining components for the full build. All items are sourced from Amazon.

### Phase 1 - Core Prototype

These are the minimum components needed to get video playing on the screen at a desk.

**Raspberry Pi Zero 2 WH (pre-soldered headers)**
Pre-soldered color-coded GPIO headers - no soldering needed, just plug in dupont wires. 65 x 30 mm, quad-core ARM, 512 MB RAM, Wi-Fi, Bluetooth. Adds ~2.5 mm height for the pins, still fits well within the 36 mm tin depth.
[Amazon - Pi Zero 2 WH Color-Coded Headers](https://www.amazon.com/Zero-Pre-Soldered-Color-Coded-Quad-Core-Bluetooth/dp/B0DS68NPGF)
Approx: $18-28

**Waveshare 2.4" SPI TFT LCD Display (ILI9341)**
240 x 320 resolution, SPI interface, 65K RGB colors. Active area ~49 x 37 mm fits well inside the portrait window. Waveshare provides Pi-specific drivers, setup guides, and wiki documentation, which makes configuration with Claude Code much smoother.
[Amazon - Waveshare 2.4" LCD SPI](https://www.amazon.com/Waveshare-2-4inch-Display-Resolution-Interface/dp/B08H24H7KX)
Approx: $12-18

**32 GB MicroSD Card**
Class 10 or better. Stores the OS, animation files, and scripts. Samsung EVO Plus is reliable and cheap.
[Amazon - Samsung EVO Plus 32GB](https://www.amazon.com/Samsung-Class-Micro-Adapter-MB-MC32GA-AM/dp/B0749KG1JK)
Approx: $8-12

**Female-to-Female Dupont Jumper Wires (10 cm)**
For connecting the LCD to the Pi's GPIO pins without soldering. A 40-piece multicolor pack is plenty.
[Amazon - 40pcs F/F Dupont 10cm](https://www.amazon.com/Female-Dupont-Jumper-Wires-Cable/dp/B00RLQE3E0)
Approx: $5-7

**Micro-USB Power Supply (5V)**
Any standard 5V micro-USB phone charger or Pi power supply works for desk testing. You likely already have one. If not, any 5V 2A micro-USB adapter will do.
Approx: $0 (use existing) or $8-10

**Phase 1 estimated total: $38-59**

### Phase 2 - Battery, Sensor, and Assembly

Once the display prototype works, add these for the full wireless build.

**3.7V LiPo Battery 2000 mAh (2-pack)**
Flat pouch cell with PH 2.0 connector and integrated protection circuit (overcharge, over-discharge, short circuit). 1.5A max current is well above the ~300-500mA draw of the Pi + LCD. Two-pack gives you a spare.
[Amazon - JLJLUP 2-pack 3.7V 2000mAh LiPo](https://www.amazon.com/JLJLUP-Rechargeable-Integrated-Protection-Development/dp/B0FH7G1WPG)
Approx: $10-15

**TP4056 USB-C LiPo Charging Module (with protection)**
Charges the battery via USB-C, includes overcharge and over-discharge protection. The HiLetgo 3-pack gives you spares.
[Amazon - HiLetgo TP4056 Type-C 3-pack](https://www.amazon.com/HiLetgo-Lithium-Charging-Protection-Functions/dp/B07PKND8KG)
Approx: $7-9

**MT3608 Boost Converter**
Steps the 3.7V battery up to 5V for the Pi. Tiny board (~22 x 17 mm), adjustable output via potentiometer. Multi-packs are cheap and give you spares.
[Amazon - MT3608 Boost Converter 5-pack](https://www.amazon.com/Converter-Adjustable-Voltage-Regulator-Arduino/dp/B07PDGKBQN)
Approx: $6-8

**Reed Switch Kit (normally open)**
Glass capsule reed switches, ~14-20 mm. The Gebildet 30-piece pack includes switches plus small magnets.
[Amazon - Gebildet Reed Switch 30-pack](https://www.amazon.com/Gebildet-Normally-Magnetic-Induction-Miniature/dp/B07YDH998K)
Approx: $7-9

**Small Neodymium Magnets (5 x 2 mm)**
Mounted inside the lid. If the reed switch kit above includes magnets, you may not need these separately. Check the kit contents first.
Approx: $0-5

**Mounting Supplies**
3M VHB double-sided tape and thin foam tape for securing the Pi, battery, and LCD inside the tin. Most of this you can source from a hardware store or Amazon.
Approx: $5-10

**Phase 2 estimated total: $35-56**

### Tools Needed

You may already have some of these:

- Precision knife (X-Acto) for cutting the cardboard mat
- Small Phillips screwdriver
- Wire cutters/strippers
- Soldering iron - not needed for the base build; all connections use dupont wires on pre-soldered headers
- Double-sided tape

### Cost Summary

| Category | Estimate |
|----------|----------|
| Phase 1 (prototype) | $38-59 |
| Phase 2 (full build) | $35-56 |
| **Total** | **$73-115** |


## Matting Design

The printed cardboard mat is the visible "card" layer. It should include the pentagon card border, a castle or patterned background, a decorative architectural arch around the portrait area, and a character name banner at the bottom.

Only the portrait area is cut out. A 1-2 mm black border around the cutout hides the LCD bezel edges.

Material options: 300-350 gsm cardstock, matte photo paper, or laser-printed adhesive vinyl applied to cardboard.


## Build Phases

### Phase 1 - Hardware Acquisition and Desktop Prototype

Purchase the Phase 1 components. Get the Pi Zero 2 WH booting with Raspberry Pi OS Lite, connect the SPI display with dupont wires, and confirm video playback works on the small screen. All configuration and scripting done via Claude Code over SSH from the MacBook.

### Phase 2 - Software Development

Build the main Python control script with Claude Code:

- Reed switch GPIO monitoring (using `gpiozero` or `RPi.GPIO`)
- Random animation selection from the `animations/` folder
- Video playback (fullscreen, looping)
- Display backlight control (on for lid open, off for lid close)
- systemd service for auto-start on boot

Test everything on the desk with a button simulating the reed switch before wiring the real sensor.

### Phase 3 - Animation Creation

Source or create Founding Hogwarts wizard portrait stills. Animate them using Google Gemini VEO 3.1 (image-to-video). Resize and crop from 9:16 to 3:4 for the 240 x 320 display. Build a library of multiple wizard animations. See the execution file for the exact Gemini prompt and video formatting steps.

This phase is handled by the project owner.

### Phase 4 - Physical Assembly

- Purchase Phase 2 components (battery, charger, boost converter, reed switch)
- Cut the cardboard mat with a portrait window
- Mount the LCD and Pi inside the tin with tape/standoffs
- Wire the reed switch to GPIO and mount near the lid edge
- Glue the magnet inside the lid
- Connect the battery system (LiPo to TP4056 to MT3608 to Pi)
- Final integration testing

### Phase 5 - Polish

- Tune animation loop timing and transitions
- Adjust reed switch sensitivity/debouncing
- Optimize boot time (strip unnecessary services)
- Test battery life and charging


## Future Enhancements

- **Wireless animation uploads** - Push new wizard videos to the Pi over Wi-Fi without opening the tin.
- **Motion sensor** - PIR sensor to activate animation when someone approaches, even with the lid open.
- **Sound effects** - Mini speaker for magical ambience or character-specific audio clips.
- **Animated name plate** - Second small display at the bottom of the card for the wizard's name and bio text.
