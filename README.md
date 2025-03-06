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
- マンデルブロ集合の数値データをPyxelのdata_ptrを使って高速に描画する
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
### マンデルブロ集合の数値データをPyxelのdata_ptrを使って高速に描画する
Pyxelでは、スクリーンのImageオブジェクトの描きたい位置に描きたい色のパレット番号を設定して表示させますが、pyxel.psetなどでデータを1つ1つ設定するのでは時間がかかってしまいます。
高速に描画したいならdata_ptrを使うと良いとのことなのですが、分かりやすく高速なコードを紹介している記事が無いようなので、自分で試してみました。
試したのは次の3つのコードです。
```
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
```
処理時間を計測した結果がこちら。
```
set_image_data : 0.050218699965626
set_image_data2: 0.198544500162825
set_image_data3: 0.2425997001118958
blt_image_obj  : 0.0010430000256747007
```
それぞれの処理は次の通り。
- set_image_data : data_ptrを使って配列データを**1行毎に**書き込む
- set_image_data2 : data_ptrを使ってデータを**1つずつ**書き込む
- set_image_data3 : pyxel.psetを使ってデータを**1つずつ**書き込む
- blt_image_obj : あらかじめデータを書き込んだImageオブジェクトを用意しておいて、pyxel.bltでコピーする（但し、Imageオブジェクト作成の時間は含まず）

まず、pyxel.psetを使う方法が一番遅いです。
次に、data_ptrを使ってもデータを**1つずつ**書き込むのでは、大して早くなりません。
ところが、data_ptrを使って配列データを**1行毎に**書き込むとかなり高速化されて、pyxel.psetの5倍くらい早くなりました。

毎フレームデータを更新する場合、1行毎に書き込む方法が一番早そうですが、
今回のマンデルブロ集合の描画の場合、毎フレームデータを作るわけではないので、あらかじめImageデータを作成しておいてpyxel.bltしたら早いのでは？
と考えて計測してみたのがblt_image_objですが、やはり**爆速でした**。
これなら、毎フレームデータ更新する場合も一旦Imageデータを作成してからpyxel.bltしても1番目の方法と大して時間は変わらないでしょう。

2次元配列からImageデータを作るのであれば、次のコードでOKです。
```
def image_from_data(image_data):
    width = len(image_data[0])
    height = len(image_data)
    image = pyxel.Image(width, height)
    ptr = image.data_ptr()
    for image_y, image_row in enumerate(image_data):
        offset = image_y * width
        ptr[offset : offset + width] = image_row
    return image
```
書き込む位置の指定が不要になったので、コードが少しスッキリしました。

結論としては、**毎フレームデータ更新するかどうかに関わらず上記の方法でImageデータを作成してpyxel.bltすれば良さそうです**。

### Numbaを使ってマンデルブロ集合の計算を高速化する

## Libraries / 使用したライブラリ
[Pyxel](https://github.com/kitao/pyxel)  
[Numpy](https://numpy.org/ja/)   
[Numba](https://numba.pydata.org/)   
[Turbo Colormap](https://gist.github.com/mikhailov-work/ee72ba4191942acecc03fe6da94fc73f)  
