#!/usr/bin/env python3
"""Extract the ramdisk (and second/dtb) from an Android v0 boot/recovery image.

Usage: python3 -I bootimg_ramdisk.py <boot.img> <out_dir>

Writes <out_dir>/ramdisk.cpio.gz, unpacks it into <out_dir>/ramdisk/
(regular files and directories only; symlinks are listed in symlinks.txt),
and writes <out_dir>/second.bin if present (Amlogic images usually carry
the device tree there).
"""
import gzip
import os
import struct
import sys

MAGIC = b"ANDROID!"


def pages(size, page_size):
    return (size + page_size - 1) // page_size


def safe_join(root, name):
    parts = [p for p in name.split("/") if p not in ("", ".")]
    if not parts or ".." in parts:
        return None
    return os.path.join(root, *parts)


def unpack_newc(blob, root):
    """Unpack a 'newc' cpio archive without trusting paths inside it."""
    os.makedirs(root, exist_ok=True)
    links, pos = [], 0
    while pos + 110 <= len(blob) and blob[pos:pos + 6] in (b"070701", b"070702"):
        fields = [int(blob[pos + 6 + i * 8:pos + 14 + i * 8], 16) for i in range(13)]
        mode, filesize, namesize = fields[1], fields[6], fields[11]
        name_start = pos + 110
        name = blob[name_start:name_start + namesize - 1].decode("utf-8", "replace")
        data_start = (name_start + namesize + 3) & ~3
        data = blob[data_start:data_start + filesize]
        pos = (data_start + filesize + 3) & ~3
        if name == "TRAILER!!!":
            break
        dest = safe_join(root, name)
        if dest is None:
            continue
        kind = mode & 0o170000
        if kind == 0o040000:
            os.makedirs(dest, exist_ok=True)
        elif kind == 0o100000:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as out:
                out.write(data)
        elif kind == 0o120000:
            links.append("%s -> %s" % (name, data.decode("utf-8", "replace")))
    with open(os.path.join(os.path.dirname(root), "symlinks.txt"), "w") as out:
        out.write("\n".join(links) + "\n")


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip())
        return 2
    image, out_dir = argv[1:]
    with open(image, "rb") as f:
        data = f.read()
    offset = data.find(MAGIC)
    if offset < 0:
        print("no ANDROID! header found in %s" % image)
        return 1
    hdr = data[offset:offset + 48]
    (kernel_size, _, ramdisk_size, _, second_size, _, _,
     page_size) = struct.unpack("<8I", hdr[8:40])
    if page_size not in (2048, 4096, 8192, 16384):
        print("unexpected page size %d" % page_size)
        return 1
    ramdisk_off = offset + page_size * (1 + pages(kernel_size, page_size))
    second_off = ramdisk_off + page_size * pages(ramdisk_size, page_size)
    os.makedirs(out_dir, exist_ok=True)
    ramdisk = data[ramdisk_off:ramdisk_off + ramdisk_size]
    with open(os.path.join(out_dir, "ramdisk.cpio.gz"), "wb") as out:
        out.write(ramdisk)
    try:
        unpack_newc(gzip.decompress(ramdisk), os.path.join(out_dir, "ramdisk"))
    except (OSError, EOFError, ValueError) as e:
        print("ramdisk not unpacked (not gzip+newc?): %s" % e)
    if second_size:
        with open(os.path.join(out_dir, "second.bin"), "wb") as out:
            out.write(data[second_off:second_off + second_size])
    cmdline = data[offset + 64:offset + 64 + 512].split(b"\0", 1)[0]
    print("kernel=%d ramdisk=%d second=%d page=%d" % (
        kernel_size, ramdisk_size, second_size, page_size))
    print("cmdline: %s" % cmdline.decode("ascii", "replace"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
