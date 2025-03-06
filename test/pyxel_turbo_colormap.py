import pyxel
import turbo_colormap

SCREEN_WIDTH = 9
SCREEN_HEIGHT = 16
pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT)

pal = [
    int(rgb[2] * 255) + int(rgb[1] * 255) * 0x100 + int(rgb[0] * 255) * 0x10000
    for rgb in turbo_colormap.turbo_colormap_data[::2]
]
pyxel.colors.from_list(pyxel.colors.to_list() + pal)

image_data = [[y * SCREEN_WIDTH + x for x in range(SCREEN_WIDTH)] for y in range(SCREEN_HEIGHT)]


def set_image_data(image: pyxel.Image, x: int, y: int, image_data):
    ptr = image.data_ptr()
    width = image.width
    for image_y, image_row in enumerate(image_data):
        offset = x + (y + image_y) * width
        ptr[offset : offset + len(image_row)] = image_row


set_image_data(pyxel.screen, 0, 0, image_data)

pyxel.show()
