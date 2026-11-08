#!/bin/sh
# Build the NEC uM310R images from this tree (used by the GitHub workflow,
# also works locally on a case-sensitive file system):
#   nec-um310r/build.sh            -> nec-um310r/out/
# Environment:
#   UM310R_FEED   the um310r feed: a git URL, or a local directory (src-link)
#                 (default: the GitHub repository)
#   JOBS          make -j (default: number of CPUs)
#
# Pass 1 (factory): the full configuration with ModemManager and the um310r
#   packages built as modules only, so that the initramfs fits the stock
#   firmware slot (0x750000). It is only used to migrate from the stock
#   firmware and has no LTE.
# Pass 2 (full): the full configuration -> sysupgrade image.
set -e
cd "$(dirname "$0")/.."
D=nec-um310r
OUT=$D/out
FEED=${UM310R_FEED:-https://github.com/nunnun/openwrt-um310r-feed.git}
JOBS=${JOBS:-$(nproc)}
B=bin/targets/ath79/generic/openwrt-ath79-generic-nec_um310r

cp feeds.conf.default feeds.conf
if [ -d "$FEED" ]; then
	echo "src-link um310r $(cd "$FEED" && pwd)" >> feeds.conf
else
	echo "src-git um310r $FEED" >> feeds.conf
fi
./scripts/feeds update -a
./scripts/feeds install -a

rm -rf files && cp -a $D/files files
rm -rf "$OUT" && mkdir -p "$OUT"

build() {
	make -j"$JOBS" || make -j1 V=s
}

echo "== pass 1: factory (no ModemManager)"
cp $D/config/full.diffconfig .config
make defconfig
for p in $(cat $D/config/factory-modules); do
	sed -i "s/^CONFIG_PACKAGE_$p=y$/CONFIG_PACKAGE_$p=m/" .config
done
make defconfig
make download -j"$JOBS"
build
cp $B-initramfs-kernel.bin "$OUT/"

echo "== pass 2: full"
cp $D/config/full.diffconfig .config
make defconfig
make download -j"$JOBS"
build
cp $B-squashfs-sysupgrade.bin $B.manifest "$OUT/"

python3 $D/tools/mkum310r_factory.py "$OUT/openwrt-ath79-generic-nec_um310r-initramfs-kernel.bin" \
	"$OUT/openwrt-ath79-generic-nec_um310r-initramfs-factory.bin"
python3 $D/tools/mkum310r_factory.py --check "$OUT/openwrt-ath79-generic-nec_um310r-initramfs-factory.bin"
rm "$OUT/openwrt-ath79-generic-nec_um310r-initramfs-kernel.bin"
git log -1 --format='built from %H (%cd)' > "$OUT/BUILDINFO"
( cd "$OUT" && sha256sum *.bin > sha256sums )
ls -l "$OUT"
