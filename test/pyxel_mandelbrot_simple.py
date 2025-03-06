import pyxel
import turbo_colormap
import numpy as np

MAND_ORIGIN = complex(0, 0)  # 表示の中心座標
MAND_WIDTH = 4.4  # 表示幅
MAND_NUM = 50  # 計算回数

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900


def mandelbrot(n: int, c: complex):
    z = 0
    for i in range(n):
        z = z * z + c
        # zの絶対値が一度でも2を超えればzが発散
        if abs(z) >= 2:
            return i

    return n  # 無限大に発散しない場合にはnを返す


def mesh_mand(orig: complex, width: float, res_x: int, res_y: int, n: int):
    height = width * res_y / res_x
    x = np.linspace(orig.real - width / 2, orig.real + width / 2, res_x)
    y = np.linspace(orig.imag - height / 2, orig.imag + height / 2, res_y)
    # 実部と虚部の組み合わせを作成
    X, Y = np.meshgrid(x, y)
    C = X + Y * 1j
    mesh = np.array([mandelbrot(n, c) for c in C.ravel()])
    return mesh.reshape((res_y, res_x))


def set_image_data(image: pyxel.Image, x: int, y: int, image_data):
    ptr = image.data_ptr()
    width = image.width
    for image_y, image_row in enumerate(image_data):
        offset = x + (y + image_y) * width
        ptr[offset : offset + len(image_row)] = image_row


pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT)

pal = [
    int(rgb[2] * 255) + int(rgb[1] * 255) * 0x100 + int(rgb[0] * 255) * 0x10000
    for rgb in turbo_colormap.turbo_colormap_data[::2]
]
pyxel.colors.from_list(pyxel.colors.to_list() + pal)

mesh = mesh_mand(MAND_ORIGIN, MAND_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT, MAND_NUM)
image_data = (mesh / MAND_NUM * 127).astype(int) + 16
set_image_data(pyxel.screen, 0, 0, image_data)

pyxel.show()
