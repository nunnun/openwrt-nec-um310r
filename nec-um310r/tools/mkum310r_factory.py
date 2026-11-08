#!/usr/bin/env python3
"""Build (and self-check) an NEC uM310R stock-web-UI firmware file ("V2 image").

Clean-room implementation of the upload file layout accepted by the stock
web UI (signature, magic and per-block header with an MD5), written from
observing the stock firmware's checks; contains no vendor code. Used to wrap
the OpenWrt initramfs so it can be uploaded from the stock web UI.

usage: mkum310r_factory.py <payload> <out> [--devname /dev/mtdblock/4] [--offset 0]
       mkum310r_factory.py --check <file>
"""
import hashlib, struct, sys

SIGNATURE = b"alpha_umrouter_amlte"
MAGIC = 0x20040220          # stored little-endian
HDR = 60                    # block header size


def block(payload, devname="/dev/mtdblock/4 0", offset=0):
    dn = devname.encode().ljust(32, b"\0")[:32]
    off = struct.pack("<I", offset)
    md5 = hashlib.md5(off + dn + payload).digest()
    return struct.pack("<II", MAGIC, len(payload)) + off + dn + md5 + payload


def build(payload, devname, offset):
    # stock is_diff_ubootmask reads the size field big-endian by mistake and
    # rejects values < 0x20001; pad so the low byte of the size is non-zero.
    if len(payload) & 0xff == 0:
        payload += b"\xff"
    return SIGNATURE.ljust(32, b"\0") + struct.pack("<I", MAGIC) + block(payload, devname, offset)


def check(img):
    """Mirror of the stock checks (mathopd upload_image + libUpgrade)."""
    err = []
    if len(img) < 0x20001:
        err.append("file shorter than 0x20001 (is_diff_ubootmask)")
    if img[:32].split(b"\0")[0] != SIGNATURE:
        err.append("signature mismatch")
    if struct.unpack("<I", img[32:36])[0] != MAGIC:
        err.append("file magic mismatch")
    pos = 36
    while pos < len(img):
        magic, size, off = struct.unpack("<III", img[pos:pos + 12])
        dn, digest = img[pos + 12:pos + 44], img[pos + 44:pos + 60]
        raw_size_be = struct.unpack(">I", img[pos + 4:pos + 8])[0]
        name = dn.split(b"\0")[0].decode(errors="replace")
        print(f"block @0x{pos:x}: devname='{name}' offset=0x{off:x} size=0x{size:x}")
        if magic != MAGIC:
            err.append(f"block magic mismatch @0x{pos:x}")
            break
        if pos + HDR + size > len(img):
            err.append("size out of boundary")
            break
        if raw_size_be < 0x20001:
            err.append("size field fails the stock big-endian size check")
        if hashlib.md5(img[pos + 8:pos + 44] + img[pos + HDR:pos + HDR + size]).digest() != digest:
            err.append(f"MD5 mismatch @0x{pos:x}")
        if name.split()[0][:15] == "/dev/mtdblock/4" and size > 0x750000:
            err.append("firmware block larger than one region (0x750000)")
        pos += HDR + size
    if pos != len(img):
        err.append(f"illegal block / trailing data at 0x{pos:x}")
    return err


def main(a):
    if a[:1] == ["--check"]:
        e = check(open(a[1], "rb").read())
        print("OK" if not e else "\n".join("ERROR: " + x for x in e))
        return 1 if e else 0
    payload, out = a[0], a[1]
    devname = a[a.index("--devname") + 1] if "--devname" in a else "/dev/mtdblock/4 0"
    offset = int(a[a.index("--offset") + 1], 0) if "--offset" in a else 0
    img = build(open(payload, "rb").read(), devname, offset)
    open(out, "wb").write(img)
    e = check(img)
    print("OK" if not e else "\n".join("ERROR: " + x for x in e))
    return 1 if e else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
