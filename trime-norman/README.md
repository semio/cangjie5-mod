# 在同文输入法中使用自定义的键盘布局

我想把自定义的仓颉输入法放到我的安卓手机上用，以下是一些笔记。

在手机上用，会有两种情况：1. 手机的虚拟键盘；2. 外置键盘。

## 虚拟键盘

虚拟键盘是比较简单的，只要在同文里创建新的键盘布局就好了。

在 `trime.custom.yaml` 中使用 `preset_keyboards` 定义自定义键盘布局：

```yaml
patch:
  "preset_keyboards/norman":
    name: "诺曼键盘"
    author: "your-name"
    ascii_mode: 0
    keys:
      # 第一行（对应 QWERTY 的 QWERTYUIOP 位置，输出诺曼布局字符）
      - {click: q}
      - {click: w}
      - {click: e}
      # ... 按诺曼布局排列
```

本目录的 `trime.custom.yaml` 中包含了一个例子。


## 外置键盘

外置键盘就比较复杂，因为必须要系统支持我们用的 ascii 布局才行。我用的是 Norman 布局，安卓是没有自带的（虽然 Norman 2013年就已经加入到 xkeyboard-config 了）。

另，GBoard 中已包含几个常用的布局：Colemak, Dvorak, Workman，如果是用这几种布局，只需安装 Gboard 即可。 

对于没有的布局，可以尝试按照 https://github.com/ris58h/custom-keyboard-layout 的方法自定义一个。这个我还没试过，我用的是另一个较简单的折中方法。

### RIME 方案级别的部分重映射

使用 RIME 的 `key_binder`：

```yaml
# 在你的 schema.custom.yaml 中
key_binder:
  bindings:
    - {accept: "f", send: "t", when: always}  # 输入 f, 输出 t
    - {accept: "j", send: "b", when: always}
```

但这个方案只对中文生效，在 ascii 状态就仍然会是 qwerty 布局。
