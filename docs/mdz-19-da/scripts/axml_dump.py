#!/usr/bin/env python3
"""Print the component tree of an APK's binary AndroidManifest.xml.

Usage: python3 -I axml_dump.py <app.apk>

Output is one tag per line, indented, with the attributes that matter for
system-app analysis (package, versionName, sharedUserId, component names,
intent actions, permissions). No aapt or Android SDK needed.
"""
import struct
import sys
import zipfile

KEEP_ATTRS = ("package", "versionName", "versionCode", "sharedUserId", "name",
              "exported", "permission", "process", "value", "persistent",
              "priority")
TYPE_STRING, TYPE_INT_DEC, TYPE_INT_HEX, TYPE_BOOL, TYPE_REF = 3, 16, 17, 18, 1


def read_string_pool(buf, start):
    _, header_size, _ = struct.unpack_from("<HHI", buf, start)
    count, _, flags, strings_start, _ = struct.unpack_from("<5I", buf, start + 8)
    utf8 = bool(flags & 0x100)
    offsets = struct.unpack_from("<%dI" % count, buf, start + header_size)
    base = start + strings_start
    out = []
    for off in offsets:
        pos = base + off
        if utf8:
            n = buf[pos]
            pos += 2 if n & 0x80 else 1
            n = buf[pos]
            if n & 0x80:
                n = ((n & 0x7F) << 8) | buf[pos + 1]
                pos += 2
            else:
                pos += 1
            out.append(buf[pos:pos + n].decode("utf-8", "replace"))
        else:
            n = struct.unpack_from("<H", buf, pos)[0]
            pos += 2
            if n & 0x8000:
                n = ((n & 0x7FFF) << 16) | struct.unpack_from("<H", buf, pos)[0]
                pos += 2
            out.append(buf[pos:pos + n * 2].decode("utf-16-le", "replace"))
    return out


def fmt_value(strings, raw, dtype, data):
    if raw != 0xFFFFFFFF and raw < len(strings):
        return strings[raw]
    if dtype == TYPE_STRING and data < len(strings):
        return strings[data]
    if dtype == TYPE_INT_DEC:
        return str(data)
    if dtype == TYPE_BOOL:
        return "true" if data else "false"
    if dtype == TYPE_REF:
        return "@0x%08x" % data
    return "0x%x" % data


def dump(buf):
    pos = struct.unpack_from("<HH", buf, 0)[1]
    strings, depth = [], 0
    while pos + 8 <= len(buf):
        ctype, header_size, size = struct.unpack_from("<HHI", buf, pos)
        if size == 0:
            break
        if ctype == 0x0001:
            strings = read_string_pool(buf, pos)
        elif ctype == 0x0102:
            name_idx = struct.unpack_from("<I", buf, pos + 20)[0]
            attr_start, attr_size, attr_count = struct.unpack_from(
                "<HHH", buf, pos + 24)
            attrs = []
            for i in range(attr_count):
                a = pos + 16 + attr_start + i * attr_size
                _, aname, raw, _, _, dtype, data = struct.unpack_from(
                    "<IIIHBBI", buf, a)
                key = strings[aname] if aname < len(strings) else "?"
                if key in KEEP_ATTRS:
                    attrs.append("%s=%s" % (key, fmt_value(strings, raw, dtype, data)))
            tag = strings[name_idx] if name_idx < len(strings) else "?"
            print("%s<%s %s>" % ("  " * depth, tag, " ".join(attrs)))
            depth += 1
        elif ctype == 0x0103:
            depth = max(depth - 1, 0)
        pos += size


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 2
    try:
        with zipfile.ZipFile(argv[1]) as z:
            buf = z.read("AndroidManifest.xml")
    except (KeyError, zipfile.BadZipFile) as e:
        print("cannot read manifest: %s" % e)
        return 1
    try:
        dump(buf)
    except (struct.error, IndexError) as e:
        print("manifest parse stopped: %s" % e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
