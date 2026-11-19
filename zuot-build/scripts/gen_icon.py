# -*- coding: utf-8 -*-
import zlib, struct

W = H = 192

def make_img():
    bg    = (11, 14, 20, 255)      # #0b0e14
    red   = (239, 68, 68, 255)     # #ef4444
    green = (34, 197, 94, 255)     # #22c55e
    blue  = (59, 130, 246, 255)    # #3b82f6

    px = [[bg] * W for _ in range(H)]

    def rect(x0, y0, x1, y1, c):
        for y in range(max(0, int(y0)), min(H, int(y1))):
            for x in range(max(0, int(x0)), min(W, int(x1))):
                px[y][x] = c

    def vline(cx, y0, y1, c, t=3):
        for y in range(int(y0), int(y1)):
            for x in range(int(cx) - t // 2, int(cx) - t // 2 + t):
                if 0 <= x < W and 0 <= y < H:
                    px[y][x] = c

    # candlesticks (red up / green down)
    candles = [
        (36, 26, 150, 52, 96, red),
        (76, 42, 142, 74, 88, green),
        (116, 20, 158, 58, 114, red),
        (156, 48, 146, 78, 96, green),
    ]
    for cx, wt, wb, bt, bb, c in candles:
        vline(cx, wt, wb, c, 3)
        rect(cx - 9, bt, cx + 9, bb, c)

    # blue MA line
    pts = [(10, 120), (40, 132), (80, 100), (120, 118), (160, 86), (182, 104)]
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for s in range(steps + 1):
            x = x0 + (x1 - x0) * s // max(1, steps)
            y = y0 + (y1 - y0) * s // max(1, steps)
            rect(x - 1, y - 1, x + 2, y + 2, blue)

    return px

def write_png(path, px):
    H = len(px)
    W = len(px[0])
    raw = b''
    for y in range(H):
        raw += b'\x00'
        for x in range(W):
            r, g, b, a = px[y][x]
            raw += struct.pack('BBBB', r, g, b, a)

    def chunk(t, data):
        c = t + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 6, 0, 0, 0)  # 8-bit RGBA
    idat = zlib.compress(raw, 9)
    png = sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    print('wrote', path, len(png), 'bytes')

img = make_img()
write_png(r'D:\stock\make_t_test_andorid\zuot-build\out\icon.png', img)
