import pyxel
import turbo_colormap
import numpy as np
import time

MAND_ORIGIN = complex(0, 0)  # 表示の中心座標
MAND_WIDTH = 4.4  # 表示幅
MAND_NUM = 50  # 計算回数

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


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


def set_image_data2(image: pyxel.Image, x: int, y: int, image_data):
    ptr = image.data_ptr()
    width = image.width
    for ny in range(len(image_data)):
        for nx in range(len(image_data[ny])):
            ptr[x + nx + (y + ny) * width] = image_data[ny][nx]


def set_image_data3(image: pyxel.Image, x: int, y: int, image_data):
    for ny in range(len(image_data)):
        for nx in range(len(image_data[ny])):
            pyxel.pset(x + nx, y + ny, image_data[ny][nx])


def image_from_data(image_data):
    width = len(image_data[0])
    height = len(image_data)
    image = pyxel.Image(width, height)
    ptr = image.data_ptr()
    for image_y, image_row in enumerate(image_data):
        offset = image_y * width
        ptr[offset : offset + width] = image_row
    return image


pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT)

pal = [
    int(rgb[2] * 255) + int(rgb[1] * 255) * 0x100 + int(rgb[0] * 255) * 0x10000
    for rgb in turbo_colormap.turbo_colormap_data[::2]
]
pyxel.colors.from_list(pyxel.colors.to_list() + pal)

mesh = mesh_mand(MAND_ORIGIN, MAND_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT, MAND_NUM)
image_data = (mesh / MAND_NUM * 127).astype(int) + 16

# set_image_data
start = time.perf_counter()
set_image_data(pyxel.screen, 0, 0, image_data)
end = time.perf_counter()
print("set_image_data : {0}".format(end - start))

# set_image_data2
start = time.perf_counter()
set_image_data2(pyxel.screen, 0, 0, image_data)
end = time.perf_counter()
print("set_image_data2: {0}".format(end - start))

# set_image_data3
start = time.perf_counter()
set_image_data3(pyxel.screen, 0, 0, image_data)
end = time.perf_counter()
print("set_image_data3: {0}".format(end - start))

# blt_image_obj
temp_image = image_from_data(image_data)
start = time.perf_counter()
pyxel.blt(0, 0, temp_image, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
end = time.perf_counter()
print("blt_image_obj  : {0}".format(end - start))

pyxel.show()
