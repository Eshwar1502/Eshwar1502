#!/usr/bin/env python3
"""Turn a photo into the ASCII block that gen.py draws in the left panel.

stdlib only, to match gen.py. Feed it a PNG (macOS: `sips -s format png ...`);
JPEG decoding is out of scope.

    python3 ascii_from_photo.py photo.png --rot ccw --crop 0.39,0.57,0.78,1.0

Prints a ready-to-paste ASCII list. Tune --crop / --gamma / --clip until the
face reads, then paste the output over the ASCII list in gen.py.
"""
import argparse, struct, sys, zlib

# dense -> sparse. The panel draws glyphs bright on a dark card, so dark parts of
# the photo (hair, shirt) need the dense glyphs and the blown-out background maps
# to a space and disappears.
RAMP = "@#%*+=:. "


def read_png(path):
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit("not a PNG")
    pos, idat, w = 8, [], None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", body)
            if depth != 8 or interlace or color not in (0, 2, 6):
                sys.exit("need 8-bit non-interlaced grey/RGB/RGBA")
        elif typ == b"IDAT":
            idat.append(body)
        elif typ == b"IEND":
            break
        pos += 12 + ln
    chans = {0: 1, 2: 3, 6: 4}[color]
    raw = zlib.decompress(b"".join(idat))
    stride = w * chans
    out, prev, p = [], bytearray(stride), 0
    for _ in range(h):                      # undo the per-scanline filters
        f = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        if f == 1:
            for i in range(chans, stride):
                line[i] = (line[i] + line[i - chans]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i - chans] if i >= chans else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - chans] if i >= chans else 0
                b = prev[i]
                c = prev[i - chans] if i >= chans else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        elif f != 0:
            sys.exit("bad filter %d" % f)
        row = [0] * w
        for x in range(w):                  # straight to luminance
            o = x * chans
            row[x] = (line[o] if chans == 1 else
                      (line[o] * 299 + line[o + 1] * 587 + line[o + 2] * 114) // 1000)
        out.append(row)
        prev = line
    return w, h, out


def rotate(px, mode):
    if mode == "ccw":
        w = len(px[0])
        return [[px[y][x] for y in range(len(px))] for x in range(w - 1, -1, -1)]
    if mode == "cw":
        return [list(col) for col in zip(*px[::-1])]
    return px


def write_grey_png(path, px):
    """Minimal greyscale PNG writer, only so the crop can be eyeballed."""
    h, w = len(px), len(px[0])
    raw = b"".join(b"\x00" + bytes(row) for row in px)
    def chunk(typ, body):
        return (struct.pack(">I", len(body)) + typ + body +
                struct.pack(">I", zlib.crc32(typ + body) & 0xFFFFFFFF))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw))
           + chunk(b"IEND", b""))
    open(path, "wb").write(png)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("png")
    ap.add_argument("--rot", choices=["none", "cw", "ccw"], default="none")
    ap.add_argument("--crop", default="0,0,1,1", help="x0,y0,x1,y1 as fractions, applied before rotation")
    ap.add_argument("--cols", type=int, default=40)
    ap.add_argument("--rows", type=int, default=20)
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--clip", default="2,98", help="low,high percentile for the contrast stretch")
    ap.add_argument("--preview", help="also write the cropped/rotated greyscale here as a PNG")
    ap.add_argument("--ramp", default=RAMP, help="dense->sparse glyph ramp")
    ap.add_argument("--local", type=int, default=0,
                    help="local-contrast radius in cells. Judges each cell against its "
                         "neighbourhood instead of the whole frame, which is what pulls "
                         "features out of an evenly-lit face")
    ap.add_argument("--bg-cut", type=float, default=0.0, dest="bg_cut",
                    help="cells brighter than this (0-1, global tone) are blanked before local "
                         "contrast runs. Without it, local contrast turns a flat wall into noise")
    ap.add_argument("--posterize", type=int, default=0,
                    help="quantise to N hard bands instead of the smooth ramp; at panel "
                         "resolution a few flat bands read as a face where a gradient reads as noise")
    args = ap.parse_args()

    _, _, px = read_png(args.png)
    x0, y0, x1, y1 = (float(v) for v in args.crop.split(","))
    h, w = len(px), len(px[0])
    px = [row[int(x0 * w):int(x1 * w)] for row in px[int(y0 * h):int(y1 * h)]]
    px = rotate(px, args.rot)
    h, w = len(px), len(px[0])

    if args.preview:
        write_grey_png(args.preview, px)

    flat = sorted(v for row in px for v in row)
    lo_p, hi_p = (float(v) for v in args.clip.split(","))
    lo = flat[int(len(flat) * lo_p / 100)]
    hi = flat[min(len(flat) - 1, int(len(flat) * hi_p / 100))]
    span = max(1, hi - lo)

    ramp = args.ramp
    # cell grid first, so local contrast and the glyph mapping both work on cells
    grid = []
    for r in range(args.rows):
        ya, yb = r * h // args.rows, max(r * h // args.rows + 1, (r + 1) * h // args.rows)
        row = []
        for c in range(args.cols):
            xa, xb = c * w // args.cols, max(c * w // args.cols + 1, (c + 1) * w // args.cols)
            tot = n = 0
            for y in range(ya, yb):
                srow = px[y]
                for x in range(xa, xb):
                    tot += srow[x]; n += 1
            row.append((tot / n - lo) / span)
        grid.append(row)

    # Global tone decides what is background; local contrast only shapes what is left.
    bg = [[args.bg_cut and grid[r][c] > args.bg_cut for c in range(args.cols)]
          for r in range(args.rows)]

    if args.local:
        rad = args.local
        blur = []
        for r in range(args.rows):
            brow = []
            for c in range(args.cols):
                tot = n = 0
                for y in range(max(0, r - rad), min(args.rows, r + rad + 1)):
                    for x in range(max(0, c - rad), min(args.cols, c + rad + 1)):
                        tot += grid[y][x]; n += 1
                brow.append(tot / n)
            blur.append(brow)
        grid = [[grid[r][c] - blur[r][c] + 0.5 for c in range(args.cols)]
                for r in range(args.rows)]

    lines = []
    for r in range(args.rows):                        # box-average each character cell
        out = []
        for c in range(args.cols):
            if bg[r][c]:
                out.append(" ")
                continue
            v = min(1.0, max(0.0, grid[r][c])) ** args.gamma
            if args.posterize:
                band = min(args.posterize - 1, int(v * args.posterize))
                idx = band * (len(ramp) - 1) // max(1, args.posterize - 1)
                out.append(ramp[idx])
            else:
                out.append(ramp[min(len(ramp) - 1, int(v * len(ramp)))])
        lines.append("".join(out).rstrip())

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    print("ASCII = [")
    for ln in lines:
        print('    "%s",' % ln.replace("\\", "\\\\").replace('"', '\\"'))
    print("]")


main()
