# OpenWrt for the NEC uM310R

Unofficial OpenWrt build for the **NEC uM310R** LTE router. Not affiliated with
NEC or AM Telecom. The device support is on its way upstream; until then this
branch (`nec-um310r` of nunnun/openwrt-nec-um310r) carries it on top of OpenWrt main, and
the GitHub workflow builds the images.

> **Use at your own risk.** Flashing third-party firmware can brick the device
> and voids any warranty. Read the whole page first, and make the backup below
> before writing the sysupgrade image.

## Hardware

| | |
|---|---|
| SoC | Qualcomm Atheros AR9344 |
| Flash / RAM | 16 MiB SPI NOR / 128 MiB |
| Wi-Fi | 2.4 GHz 2T2R (built-in) |
| Ethernet | 2 RJ45 (switch ports 1 and 2) |
| LTE | AM Telecom AMM570 on internal USB |
| Other | external watchdog (LMC555), Epson RX-8010SJ RTC, 2 temperature sensors, ANT/COM/ALM LEDs |
| Serial | U-Boot / console 115200 8N1 (internal header) |

## What works

- Ethernet, Wi-Fi, LEDs, buttons, sysupgrade
- LTE through **ModemManager** (MBIM), IPv4 + IPv6; the WWAN /64 is passed on to
  the LAN. Default APN in the image: `povo.jp` (change it under
  *Network → Interfaces → WWAN*)
- LuCI page *Network → LTE*: signal details (band, EARFCN, PCI, RSRP/RSRQ),
  IMEI, SMS list / send / delete. English and Japanese
- External watchdog fed by the kernel; NTP time stored in the RTC
- Automatic recovery of the LTE connection and of a hung card
- The ANT/COM/ALM LEDs behave like the stock firmware

The helper packages live in
[openwrt-um310r-feed](https://github.com/nunnun/openwrt-um310r-feed).

## Images (Releases)

| File | Use |
|---|---|
| `…-initramfs-factory.bin` | upload from the **stock** web UI (first install only; runs OpenWrt from RAM, no LTE) |
| `…-squashfs-sysupgrade.bin` | the real firmware, flashed from OpenWrt |
| `sha256sums`, `BUILDINFO` | checksums, source commit |

Releases are builds that were tested on a real device. The weekly workflow
runs build the branch rebased onto the latest OpenWrt main; their artifacts are
untested.

## Install from the stock firmware

1. In the stock web UI: *Maintenance → Firmware update*, upload
   `…-initramfs-factory.bin`. The router reboots into OpenWrt running from RAM
   at http://192.168.1.1 (user `root`, no password).
2. **Back up the flash now** (needed to go back to stock): in LuCI
   *System → Backup / Flash Firmware → Save mtdblock contents*, download
   **every** mtdblock (at least `u-boot`, `u-boot-env`, `firmware`, `art`).
   `art` holds the Wi-Fi calibration and MAC addresses of your unit; keep the
   files safe and private.
3. In the same page, *Flash new firmware image*: `…-squashfs-sysupgrade.bin`,
   **without** keeping settings.
4. After the reboot, set a root password (*System → Administration*) and check
   the LTE settings (APN).

On the first boot the LTE card, which the stock firmware keeps in ACM mode, is
switched to MBIM mode once; this takes about half a minute.

## Back to the stock firmware (not yet tested)

OpenWrt uses both stock firmware slots, so going back needs **your own backup
of the `firmware` mtdblock from step 2**. This project does not distribute any
stock firmware.

From OpenWrt (copy the file to `/tmp` first):

    mtd -r write /tmp/<your firmware backup> firmware

then, if the stock firmware does not boot, set the region it was installed in
from U-Boot: `setenv activeregion 1` (or `2`) and `saveenv`. The stock firmware
switches the LTE card back to its own mode by itself.

## Recovery

U-Boot (serial console, any key within 4 s) offers `tftpboot`, `bootm`,
`erase`, `cp.b`, so an initramfs can always be booted from RAM:
`tftpboot 0x82000000 <initramfs-kernel.bin>; bootm 0x82000000`.

## Build

On Linux (case-sensitive file system), with the usual OpenWrt build
dependencies:

    git clone -b nec-um310r https://github.com/nunnun/openwrt-nec-um310r.git
    cd openwrt
    nec-um310r/build.sh

The images end up in `nec-um310r/out/`. `nec-um310r/config/full.diffconfig`
is the configuration; `nec-um310r/files/` is the board overlay (LTE card power,
external watchdog, RTC update, first-boot network defaults).

## Known limitations

- The factory (initramfs) image has no LTE: it only exists to get from the
  stock firmware to the sysupgrade image.
- Kernel modules from the official OpenWrt snapshot repository usually do not
  match these images (different kernel build). Userspace packages install
  fine.
- Tested with a povo SIM (KDDI network) only.

## License

GPL-2.0 like OpenWrt; see the files and `LICENSES/`.
