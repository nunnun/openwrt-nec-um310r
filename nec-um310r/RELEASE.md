OpenWrt for the **NEC uM310R** (unofficial). Tested on a real device.

- First install from the stock firmware: `…-initramfs-factory.bin` from the stock web UI, back up all mtdblocks, then `…-squashfs-sysupgrade.bin` without keeping settings.
- Update from an earlier release: `…-squashfs-sysupgrade.bin` (settings can be kept).
- With Tailscale: use `…-tailscale-squashfs-sysupgrade.bin` instead of `…-squashfs-sysupgrade.bin` (about 1.5 MB of flash left for settings and packages instead of about 5.5 MB).

See [nec-um310r/README.md](https://github.com/nunnun/openwrt-nec-um310r/blob/nec-um310r/nec-um310r/README.md) for the full instructions, the way back to stock, and known limitations. The source commit is in `BUILDINFO`; checksums in `sha256sums`.
