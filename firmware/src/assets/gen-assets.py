#!/usr/bin/env python3

from itertools import groupby
import sys

from PIL import Image

white_pixel = 255

# img = Image.open('pixmaps/text-snips.png')
# gray = img.convert('L')
# pix = gray.load()
# w, h = gray.size
#
# def row_is_blank(row):
#     return all(pix[i, row] == white_pixel for i in range(w))
#
# def col_is_blank(col):
#     return all(pix[col, i] == white_pixel for i in range(h))
#
# left = 0
# while left < w and col_is_blank(left):
#     left += 1
#
# right = w
# while right > left and col_is_blank(right - 1):
#     right -= 1
#
# regions = []
#
# active = False
# for row in range(h):
#     if row_is_blank(row):
#         if active:
#             active = False
#             active_height = row - start
#             regions.append((start, row))
#     else:
#         if not active:
#             active = True
#             start = row
#
# assert len(regions) == 7
# region_width = right - left
# region_height = regions[0][1] - regions[0][0]
# region_size = region_height * region_width
# assert all(reg[1] - reg[0] == region_height for reg in regions)
#
# reg_img = [gray.crop((left, reg[0], right, reg[1],)) for reg in regions]
#
# def get_data(img):
#     return [list(255 - b for (i, b) in row)
#             for (g, row) in groupby(enumerate(img.getdata()),
#                                     lambda x: x[0] // region_width)]
#
# reg_data = [get_data(img) for img in reg_img]
#
# region_map = {
#     0: 'pb2aa',
#     1: 'pb2fade',
#     2: 'pb2fill',
#     3: 0,
#     4: 1,
#     5: 'pb4more',
#     6: 'pb4less',
# }
#
# for k in region_map:
#     v = region_map[k]
#     if isinstance(v, int):
#         assert reg_img[k] == reg_img[v]
#         assert reg_img[k] != reg_img[v+1]
#         print('img[{}] == img[{}]'.format(k, v))

def by_n(n, seq):
    return ((x for (i, x) in g)
            for (k, g) in groupby(enumerate(seq), lambda x: x[0] // n))

########################################################################

def pack_rgb565(tup):
    return (tup[0] >> 3 << 11 |
            tup[1] >> 2 << 5 |
            tup[2] >> 3 << 0)

ts_path = 'tilesheet.png'
ts_img = Image.open(ts_path)
ts_img = ts_img.convert("RGBA")
ts_pix = ts_img.load()
ts_w, ts_h = ts_img.size

ts_packed = [[pack_rgb565(ts_pix[x, y])
              for x in range(ts_w)]
             for y in range(ts_h)]

ts_bytes = ',\n'.join('    {{ {} }}'
                      .format(',\n      '.join(', '.join('{:3d}'.format(b)
                                                         for b in line)
                                               for line in by_n(8, row)))
                      for row in ts_packed)

ts_template = '''
#define TS_PIXMAP_HEIGHT {h}
#define TS_PIXMAP_WIDTH {w}

static const uint16_t ts_pixmap[TS_PIXMAP_HEIGHT][TS_PIXMAP_WIDTH] = {{
{bytes}
}};'''.lstrip()

ts_def = ts_template.format(h=ts_h, w=ts_w, bytes=ts_bytes)


########################################################################

template = '''
#ifndef ASSETS_H
#define ASSETS_H

/* This file was automatically generated by {program}.  Do not edit. */

#include <stdint.h>

{ts_def}

#endif /* ASSETS_H */
'''.lstrip()

# '''
# #define TEXT_PIXMAP_WIDTH {width}
# #define TEXT_PIXMAP_HEIGHT {height}
#
# //typedef uint8_t text_pixmap[{height}][{width}];
#
# //{definitions}
# '''

pixmap_template = r'''
static const text_pixmap {name} = {{
{bytes}
}};
'''.lstrip()

def format_map(index, name):
    pixels = reg_data[index]
    s = ',\n'.join('    {{ {} }}'
                   .format(',\n      '.join(', '.join('{:3d}'.format(b)
                                                     for b in line)
                                           for line in by_n(12, row)))
                   for row in pixels)
    return pixmap_template.format(name=name,
                                  height=region_height,
                                  width=region_width,
                                  bytes=s)

# defs = '\n\n'.join(
#     format_map(index, name)
#     for (index, name) in region_map.items()
#     if isinstance(name, str))

print(template.format(program=sys.argv[0],
                      ts_def=ts_def))
# width=region_width,
# height=region_height,
# definitions=defs,
