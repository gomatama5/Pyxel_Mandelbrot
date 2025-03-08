import pyxel
import turbo_colormap
import calc_mandelbrot as mand
import numpy as np
import os
import re
import glob

# 画面サイズ
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# 起動時の設定
MAND_ORIGIN = complex(0, 0)  # 表示の中心座標
MAND_WIDTH = 4.4  # 表示幅
MAND_NUM = 64  # 計算回数
MODULO_COLOR = False
GAMEPAD_AXIS_THRESHOLD = 2048


# 色データの2次元配列からpyxel.Imageオブジェクトを作成
def image_from_data(image_data):
    width = len(image_data[0])
    height = len(image_data)
    image = pyxel.Image(width, height)
    ptr = image.data_ptr()
    for image_y, image_row in enumerate(image_data):
        offset = image_y * width
        ptr[offset : offset + width] = image_row
    return image


class App:
    # タイトル文字列を作成
    def title_str(self):
        s = "X={0} Y={1} Width={2} N={3}".format(self.orig.real, self.orig.imag, self.width, self.num)
        if self.modulo_color:
            s += " ModuloColor"
        return s

    # メッシュデータを作成
    def calc_mesh_data(self):
        pyxel.title(self.title + " [Calcurating...]")
        self.mesh_data = mand.mesh_mand(self.orig, self.width, SCREEN_WIDTH, SCREEN_HEIGHT, self.num)
        self.calc_image_data()

    # メッシュデータから画像データを作成
    def calc_image_data(self):
        if self.modulo_color:
            self.image_data = (self.mesh_data % 128).astype(int) + 16
        else:
            self.image_data = (self.mesh_data / self.num * 127).astype(int) + 16
        self.screen_image = image_from_data(self.image_data)
        self.title = self.title_str()
        pyxel.title(self.title)

    def __init__(self):
        self.orig = MAND_ORIGIN
        self.width = MAND_WIDTH
        self.num = MAND_NUM
        self.modulo_color = MODULO_COLOR

        self.title = self.title_str()
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title=self.title)

        pyxel.mouse(True)
        pal = [
            int(rgb[2] * 255) + int(rgb[1] * 255) * 0x100 + int(rgb[0] * 255) * 0x10000
            for rgb in turbo_colormap.turbo_colormap_data[::2]
        ]
        pyxel.colors.from_list(pyxel.colors.to_list() + pal)

        self.calc_mesh_data()

        self.mouse_x = 0
        self.mouse_y = 0
        self.draw_rect = False

        pyxel.run(self.update, self.draw)

    def update(self):
        # 左クリックで範囲指定して拡大
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.mouse_x = pyxel.mouse_x
            self.mouse_y = pyxel.mouse_y
            self.draw_rect = True
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            mouse_x = int(np.clip(pyxel.mouse_x, 0, SCREEN_WIDTH - 1))
            mouse_y = int(np.clip(pyxel.mouse_y, 0, SCREEN_HEIGHT - 1))
            if mouse_x != self.mouse_x and mouse_y != self.mouse_y:
                scale = max(
                    abs(self.mouse_x - pyxel.mouse_x) / SCREEN_WIDTH, abs(self.mouse_y - pyxel.mouse_y) / SCREEN_HEIGHT
                )
                offset_x = (self.mouse_x + mouse_x) / 2 - SCREEN_WIDTH / 2
                offset_y = (self.mouse_y + mouse_y) / 2 - SCREEN_HEIGHT / 2
                offset = complex(offset_x, offset_y) * self.width / SCREEN_WIDTH
                self.orig += offset
                self.width *= scale
                self.calc_mesh_data()

        # 右ドラッグで位置移動
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            self.rmouse_x = pyxel.mouse_x
            self.rmouse_y = pyxel.mouse_y
        if pyxel.btnr(pyxel.MOUSE_BUTTON_RIGHT):
            mouse_x = int(np.clip(pyxel.mouse_x, 0, SCREEN_WIDTH - 1))
            mouse_y = int(np.clip(pyxel.mouse_y, 0, SCREEN_HEIGHT - 1))
            offset_x = mouse_x - self.rmouse_x
            offset_y = mouse_y - self.rmouse_y
            offset = complex(offset_x, offset_y) * self.width / SCREEN_WIDTH
            self.orig -= offset
            self.calc_mesh_data()

        # ホイールで拡大縮小
        if pyxel.mouse_wheel > 0:
            self.width /= 2
            self.calc_mesh_data()
        if pyxel.mouse_wheel < 0:
            self.width *= 2
            self.calc_mesh_data()

        # Pad RB/Aを押しながらアナログスティックで3D移動
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_RIGHTSHOULDER) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.move3d_x = 0.0
            self.move3d_y = 0.0
            self.move3d_scale = 1.0

        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_RIGHTSHOULDER) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
            if abs(pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)) > GAMEPAD_AXIS_THRESHOLD:
                self.move3d_x -= self.move3d_scale * pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX) * 16 / 32768
            if abs(pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)) > GAMEPAD_AXIS_THRESHOLD:
                self.move3d_y -= self.move3d_scale * pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY) * 16 / 32768
            if abs(pyxel.btnv(pyxel.GAMEPAD1_AXIS_RIGHTY)) > GAMEPAD_AXIS_THRESHOLD:
                scale = 1 + abs(pyxel.btnv(pyxel.GAMEPAD1_AXIS_RIGHTY)) / 32768 / 10
                if pyxel.btnv(pyxel.GAMEPAD1_AXIS_RIGHTY) > 0:
                    self.move3d_scale *= scale
                else:
                    self.move3d_scale /= scale

        if pyxel.btnr(pyxel.GAMEPAD1_BUTTON_RIGHTSHOULDER) or pyxel.btnr(pyxel.GAMEPAD1_BUTTON_A):
            if not (self.move3d_x == 0 and self.move3d_y == 0 and self.move3d_scale == 1):
                self.orig += -complex(self.move3d_x, self.move3d_y) * self.width / SCREEN_WIDTH
                self.width *= self.move3d_scale
                self.calc_mesh_data()

        # 上下キー/ボタンで計算回数を増減
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.num *= 2
            self.calc_mesh_data()
        if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.num //= 2
            self.calc_mesh_data()

        # F1/Pad Xでカラーリング方式を変更
        if pyxel.btnp(pyxel.KEY_F1) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
            self.modulo_color ^= True
            self.calc_image_data()

        # F2/Pad Startで現在の情報を保存
        if pyxel.btnp(pyxel.KEY_F2) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
            fname = "mand/X{0}_Y{1}_W{2}_N{3}_.mand".format(self.orig.real, self.orig.imag, self.width, self.num)
            print("save: " + fname)
            open(fname, "w")

        # 設定を読み込む
        def loadConfig(fname):
            m = re.match(r".*X((?:\w|\.|-)+)_Y((?:\w|\.|-)+)_W((?:\w|\.|-)+)_N((?:\w|\.|-)+)_.mand", fname)
            if m:
                try:
                    print("load: " + fname)
                    sx, sy, sw, sn = m.group(1, 2, 3, 4)
                    offset = complex(float(sx), float(sy))
                    w = float(sw)
                    n = int(sn)
                    self.orig = offset
                    self.width = w
                    self.num = n
                    self.calc_mesh_data()
                except:
                    pass

        # 画面にファイルドロップしたファイルの設定を読み込む
        if pyxel.dropped_files:
            fname = os.path.basename(pyxel.dropped_files[0])
            loadConfig(fname)

        # Pad LBを押しながら左/右ボタンn回で、n番目に新しい/古いファイルの設定を読み込む
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_LEFTSHOULDER):
            self.fileSelect = 0
        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_LEFTSHOULDER):
            if pyxel.btnr(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
                self.fileSelect -= 1
            if pyxel.btnr(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                self.fileSelect += 1
        if pyxel.btnr(pyxel.GAMEPAD1_BUTTON_LEFTSHOULDER):
            if self.fileSelect != 0:
                files = sorted(glob.glob("mand/*.mand"), key=os.path.getmtime)
                if -len(files) <= self.fileSelect < len(files):
                    fname = files[self.fileSelect]
                    loadConfig(fname)

        # F5/Pad Backで初期設定に戻す
        if pyxel.btnp(pyxel.KEY_F5) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_BACK):
            self.orig = MAND_ORIGIN
            self.width = MAND_WIDTH
            self.num = MAND_NUM
            self.modulo_color = MODULO_COLOR
            self.calc_mesh_data()

    def draw(self):
        if self.screen_image:
            # 右ドラッグ中は画像の位置をずらして描画
            if pyxel.btn(pyxel.MOUSE_BUTTON_RIGHT):
                mouse_x = int(np.clip(pyxel.mouse_x, 0, SCREEN_WIDTH - 1))
                mouse_y = int(np.clip(pyxel.mouse_y, 0, SCREEN_HEIGHT - 1))
                offset_x = mouse_x - self.rmouse_x
                offset_y = mouse_y - self.rmouse_y
                pyxel.cls(0)
                pyxel.blt(offset_x, offset_y, self.screen_image, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            # Pad RB/A中は画像の位置やスケールをずらして描画
            elif pyxel.btn(pyxel.GAMEPAD1_BUTTON_RIGHTSHOULDER) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
                pyxel.cls(0)
                pyxel.blt(
                    self.move3d_x / self.move3d_scale,
                    self.move3d_y / self.move3d_scale,
                    self.screen_image,
                    0,
                    0,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT,
                    scale=1 / self.move3d_scale,
                )
            else:
                pyxel.blt(0, 0, self.screen_image, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        # 左ドラッグの範囲の四角を描画
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) and self.draw_rect:
            pyxel.rectb(
                min(self.mouse_x, pyxel.mouse_x),
                min(self.mouse_y, pyxel.mouse_y),
                abs(self.mouse_x - pyxel.mouse_x),
                abs(self.mouse_y - pyxel.mouse_y),
                7,
            )


App()
