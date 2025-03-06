import numpy as np
from numba import jit


@jit
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
