# Pyxel_Mandelbrot
## Overview / 概要
Pyxelを使ってマンデルブロ集合を描画します。画面を操作して色々な図形を探せます。  
## How to Start / 起動方法
```
pyxel run pyxel_mandelbrot.py
```
前提条件として、次のPythonモジュールが必要です。  
- Pyxel
- Numpy
- Numba
## How to Use / 使い方
- Left-click + Drag : Expand the selected area
- Right-click + Drag : Move the position
- Mouse wheel : Scaling
- Up / Down arrow : Increase / Decrease Mandelbrot calculation number
- F1 : Change the coloring method
- F2 : Save config into /mand folder
- Drop file onto screen : Load config
- F5 : Reset
## Screenshots / スクリーンショット
![play movie](https://github.com/gomatama5/Pyxel_Mandelbrot/blob/main/screenshots/pyxel-20250306-170516.gif)
## Development History / 開発経緯
Pyxelでカラーパレット拡張を試したくて、何か描いてみようと思ってマンデルブロ集合を試してみました。
サクサク動いて楽しくなったので、ちゃんと機能を実装してしまいました。  
以下では、開発の際に試したことを幾つか紹介します。  
- TurboカラーマップをPyxelのパレットを拡張して設定する
- マンデルブロ集合の数値データをPyxelのdata_ptr()を使って高速に描画する
- Numbaを使ってマンデルブロ集合の計算を高速化する
以下で紹介するテストコードは/testフォルダ以下に入っています。
### TurboカラーマップをPyxelのパレットを拡張して設定する
見た目がいい感じのTurboカラーマップは[作者様がPythonの定義ファイルを公開されている](https://gist.github.com/mikhailov-work/ee72ba4191942acecc03fe6da94fc73f)
のでそれを使わせていただきました。  
TurboのRGBカラーデータが長さ256の配列で定義されています。
しかし、Pyxelのパレットは最大で256色しか設定できないので、Turboのカラーデータの半分の128色だけ設定しました。  
以下が、Pyxelのデフォルトのパレットの後ろにTurboの128色を追加するコードです。
```
pal = [
    int(rgb[2] * 255) + int(rgb[1] * 255) * 0x100 + int(rgb[0] * 255) * 0x10000
    for rgb in turbo_colormap.turbo_colormap_data[::2]
]
pyxel.colors.from_list(pyxel.colors.to_list() + pal)
```
設定したパレットの色を画面に表示させてみたコードがpyxel_turbo_colormap.pyです。  
[[Web Pyxel] pyxel_turbo_colormap.py](https://kitao.github.io/pyxel/wasm/launcher/?run=gomatama5.Pyxel_Mandelbrot.test.pyxel_turbo_colormap)
### マンデルブロ集合の数値データをPyxelのdata_ptr()を使って高速に描画する

### Numbaを使ってマンデルブロ集合の計算を高速化する

## Libraries / 使用したライブラリ
[Pyxel](https://github.com/kitao/pyxel)  
[Numpy](https://numpy.org/ja/)   
[Numba](https://numba.pydata.org/)   
[Turbo Colormap](https://gist.github.com/mikhailov-work/ee72ba4191942acecc03fe6da94fc73f)  
