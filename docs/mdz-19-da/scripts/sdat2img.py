#!/usr/bin/env python3
"""Rebuild a raw ext4 image from an Android block-based OTA.

Usage: python3 -I sdat2img.py <system.transfer.list> <system.new.dat> <system.img>

Only the "new" command writes data; "erase"/"zero"/stash commands are
ignored, which is correct for a full (non-incremental) OTA package.
"""
import sys

BLOCK_SIZE = 4096


def parse_ranges(text):
    nums = [int(x) for x in text.split(",")]
    if nums[0] != len(nums) - 1:
        raise ValueError("bad range list: %s" % text)
    return list(zip(nums[1::2], nums[2::2]))


def parse_transfer_list(path):
    with open(path) as f:
        lines = [line.strip() for line in f if line.strip()]
    version = int(lines[0])
    # v1: version, total_blocks; v2+: + stash entries, max stash
    body = lines[2:] if version == 1 else lines[4:]
    commands = []
    for line in body:
        parts = line.split(" ")
        if parts[0] in ("new", "erase", "zero"):
            commands.append((parts[0], parse_ranges(parts[1])))
    return version, commands


def main(argv):
    if len(argv) != 4:
        print(__doc__.strip())
        return 2
    transfer_list, new_dat, out_img = argv[1:]
    version, commands = parse_transfer_list(transfer_list)
    max_block = max(end for _, ranges in commands for _, end in ranges)
    with open(new_dat, "rb") as src, open(out_img, "wb") as dst:
        for cmd, ranges in commands:
            if cmd != "new":
                continue
            for begin, end in ranges:
                dst.seek(begin * BLOCK_SIZE)
                for _ in range(end - begin):
                    dst.write(src.read(BLOCK_SIZE))
        dst.truncate(max_block * BLOCK_SIZE)
    print("transfer.list v%d -> %s (%d blocks)" % (version, out_img, max_block))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
