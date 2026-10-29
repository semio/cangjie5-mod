# 在同文输入法中使用 Norman 键盘布局

本文档介绍如何在手机输入法中使用 Norman 键盘布局，包括虚拟键盘和外置键盘的配置方法。对其它布局也适用的。

---

## 一、Android

### 1.1 虚拟键盘（同文输入法 Trime）

通过创建新的虚拟键盘布局可以很容易实现这个效果。本目录的 `trime.custom.yaml` 中包含了一个例子。

在 `trime.yaml` 或 `trime.custom.yaml` 中使用 `preset_keyboards` 定义自定义键盘布局：

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

### 1.2 外置键盘（蓝牙 / USB 硬件键盘）

(注：以下是AI生成。我试过 `RIME 方案级别的部分重映射`，是可行的。但只局限于中文打字，在 ascii 状态下还是输出 Qwerty 的键 )

外置键盘的布局映射比虚拟键盘复杂，因为硬件键盘的按键信号由操作系统层面处理，输入法无法直接拦截和重映射。

#### 同文输入法（Trime）的限制

**同文输入法本身不支持外置键盘布局重映射。** 原因如下：

- Trime 处理硬件键盘事件时，直接读取 Android 系统 `KeyCharacterMap` 解析出的字符（`event.unicodeChar`）
- 这个字符由 Android 系统的键盘布局决定，输入法无法修改
- Trime 的 `KeyValue.fromKeyEvent()` 源码：

```kotlin
// app/src/main/java/com/osfans/trime/core/KeyValue.kt
fun fromKeyEvent(event: KeyEvent): KeyValue {
    val charCode = event.unicodeChar  // ← 直接使用系统解析的字符
    if (charCode != 0 && ...) {
        return KeyValue(charCode)
    }
    return KeyValue(RimeKeyMapping.keyCodeToVal(event.keyCode))
}
```

#### Android 解决方案

需要使用系统级的键盘布局修改工具（不需要 root）：

| 应用名称 | 价格 | 功能 | 链接 |
|---------|------|------|------|
| **More Physical Keyboard Layouts** | 免费 | 添加 Colemak、Dvorak 等布局到系统硬件键盘设置 | [Google Play](https://play.google.com/store/apps/details?id=varzan.extraKeyboardLayouts) |
| **ExKeyMo** | 免费 | 自定义构建外置键盘布局 APK | [GitHub](https://github.com/ris58h/exkeymo-web) |
| **KeymapKit** | 免费 | 系统级物理键盘布局，无需 IME | [GitHub](https://github.com/mahmutaunal/KeymapKit) |
| **External Keyboard Helper Pro** | $1.49 | 商业方案，支持自定义布局 | [Google Play](https://play.google.com/store/apps/details?id=com.apedroid.hwkeyboardhelper) |
| **Key Mapper** | 免费 | 基于无障碍服务的按键重映射 | [GitHub](https://github.com/KeyMapperOrg/KeyMapper) |

**推荐方案**：

1. **首选**：安装 **More Physical Keyboard Layouts**，在 `设置 > 系统 > 语言和输入法 > 物理键盘` 中选择布局。如果列表中没有诺曼，可以联系开发者添加。
2. **自定义**：使用 **ExKeyMo** 或 **KeymapKit** 创建诺曼布局的 `.kcm` 文件。
3. **逐键映射**：使用 **Key Mapper** 逐个重映射按键（QWERTY F → Norman T，等等）。

#### RIME 方案级别的部分重映射

如果只需要在 RIME 输入法内部 remap（不影响系统快捷键），可以使用 RIME 的 `key_binder` 或 `punctuator`：

```yaml
# 在你的 schema.custom.yaml 中
key_binder:
  bindings:
    - {accept: "f", send: "t", when: always}  # 仅在 RIME 内 remap
    - {accept: "j", send: "b", when: always}
```

或者参考 [rime-colemak](https://github.com/gkovacs/rime-colemak) 的 `punctuator` 方案创建 `rime-norman` schema。

> ⚠️ 注意：这种方法只在 RIME 激活时生效，不影响 Ctrl+C/V 等系统快捷键。

---

## 二、iOS / iPadOS

### 2.1 虚拟键盘

iOS 系统自带的虚拟键盘不支持诺曼布局，但可以通过第三方键盘应用实现：

| 应用名称 | 价格 | 支持的布局 | 备注 |
|---------|------|-----------|------|
| **Auri** | 免费（内购） | Colemak、Dvorak 等 | 支持多种布局，但无诺曼 |
| **Colemak** | 付费 | Colemak | 仅 Colemak 布局 |
| **Dvorak + Colemak Keyboards** | $0.99 | Dvorak、Colemak | 付费应用 |
| **Keyman** | 免费 | 2500+ 种语言/布局 | 可自定义键盘布局，支持开发者自制诺曼布局 |
| **ℂKey (CKey)** | 免费 | 自定义 | iPad 专用，可自定义按键布局 |
| **xKeyboard** | 免费（内购） | 自定义 | 可自定义按键映射 |

**推荐方案**：使用 **Keyman** 或 **ℂKey** 创建自定义诺曼布局，或使用 **Auri**（支持 Colemak，接近诺曼体验）。

### 2.2 外置键盘（蓝牙 / USB 硬件键盘）

外置键盘的布局映射在 iOS 上比 Android 更受限。

#### iOS 系统自带功能

iOS/iPadOS（13.4+）提供有限的硬件键盘自定义功能：

**修改修饰键（Modifier Keys）**：

```
设置 > 通用 > 键盘 > 硬件键盘 > 修饰键
```

可重映射的按键：

| 物理按键 | 可改为 |
|---------|--------|
| Caps Lock（大写锁定） | Caps Lock / Control / Option / Command / Escape / Globe / 无操作 |
| Control（控制） |同上 |
| Option（选项） |同上 |
| Command（命令） |同上 |
| Function（功能键 / Globe 地球键） |同上 |

**选择替代布局（Alternative Layouts）**：

```
设置 > 通用 > 键盘 > 硬件键盘 > [选择语言，如 English (US)]
```

iOS 内置支持 **Dvorak** 布局。Colemak 在部分 iOS 版本中也可用。**诺曼（Norman）布局不在 iOS 内置列表中。**

> ⚠️ **重要限制**：iOS 的修饰键重映射**只能修改修饰键**（Caps Lock、Control、Option、Command、Globe），**不能重映射字母键**（如把 F 键改为 T 键）。

#### iOS 第三方应用

经过调研，**iOS 上没有能够全局重映射外置键盘字母键的第三方应用**。原因：

- iOS 的沙盒机制（Sandbox）阻止第三方应用拦截和修改硬件键盘事件
- 与 Android 不同，iOS 不提供类似 `KeyCharacterMap`（`.kcm`）文件的用户自定义接口
- 无障碍服务（Accessibility）也无法拦截硬件键盘的按键事件进行全局 remap

**iOS 上可用的键盘相关应用**（均只能自定义**虚拟键盘**，不能修改硬件键盘布局）：

| 应用名称 | 价格 | 功能 | 是否支持硬件键盘重映射 |
|---------|------|------|:---:|
| **Auri** | 免费（内购） | 多布局虚拟键盘（含 Colemak、Dvorak） | ❌ 否 |
| **Colemak** | 付费 | Colemak 虚拟键盘 | ❌ 否 |
| **Dvorak + Colemak Keyboards** | $0.99 | Dvorak/Colemak 虚拟键盘 | ❌ 否 |
| **Keyman** | 免费 | 2500+ 语言虚拟键盘，可自定义布局 | ❌ 否 |
| **ℂKey (CKey)** | 免费 | iPad 自定义虚拟键盘 | ❌ 否 |
| **xKeyboard** | 免费（内购） | 自定义虚拟键盘布局 | ❌ 否 |
| **仓鼠输入法 (Hamster)** | 免费 | iOS 版 RIME 输入法，支持自定义 schema | ❌ 否（仅限输入法内） |

**Hamster（仓鼠输入法）** 是 iOS 上的 RIME 前端，支持自定义 schema。可以在 RIME schema 内使用 `key_binder` 进行有限的按键重映射，但同样**只在输入法激活时生效**，无法全局 remap 硬件键盘。

#### iOS 推荐解决方案

由于 iOS 无法全局 remap 硬件键盘字母键，推荐以下替代方案：

| 方案 | 说明 |
|------|------|
| **1. 使用可编程键盘（QMK/VIA）** | 购买支持 QMK 固件的键盘（如 Keychron、NuPhy 等），在键盘固件层面 remap 布局。这是最彻底的方案，布局保存在键盘上，插到任何设备都生效。 |
| **2. 使用带布局切换的键盘** | 部分蓝牙键盘支持 Fn + 键切换 iOS/Android/Windows 模式，或有专门的布局切换键。但通常只有预设的几种布局。 |
| **3. 使用虚拟键盘替代** | 在 iPad 上使用 Keyman、ℂKey 等应用创建诺曼虚拟键盘布局，放弃硬件键盘。 |
| **4. iPad 系统设置 + 修饰键** | 至少可以用 `设置 > 硬件键盘 > 修饰键` 优化 Caps Lock 等修饰键的功能。 |
| **5. 使用 Hamster 输入法 + RIME schema** | 在仓鼠输入法内使用自定义 schema（含 `key_binder`）实现输入法内的按键 remap。 |
| **6. 越狱（Jailbreak）** | 越狱后可通过 Cydia 工具（如 KeyManager）实现全局键盘 remap，但会失去保修和安全性。 |

**最推荐方案**：购买支持 QMK/VIA 的可编程键盘（如 Keychron Q 系列、NuPhy Air 系列），在 VIA 软件中导入诺曼布局。这样：

- 布局保存在键盘固件中
- 插到 iOS、Android、Windows、macOS 都生效
- 不依赖任何系统设置或第三方应用
- 可以保留 QWERTY 层，按需切换

---

## 三、跨平台方案对比

| 平台 | 虚拟键盘支持诺曼 | 硬件键盘全局 remap | 推荐方案 |
|------|:---:|:---:|---------|
| **Android** | ✅ 可自定义 | ✅ 需第三方应用 | Key Mapper / More Physical Keyboard Layouts / 可编程键盘 |
| **iOS / iPadOS** | ⚠️ 需第三方应用（Keyman/ℂKey） | ❌ 不支持 | 可编程键盘（QMK/VIA） / 虚拟键盘 |
| **Windows** | ✅ 系统内置多种布局 | ✅ 系统设置或 PowerToys | 系统设置 / PowerToys Keyboard Manager |
| **macOS** | ✅ 系统内置 | ✅ 系统设置或 Karabiner-Elements | Karabiner-Elements |
| **Linux** | ✅ 系统内置 | ✅ 系统设置或 setxkbmap | setxkbmap / 自定义 xkb 布局 |

---

## 四、相关资源

- [Norman 布局官网](https://normanlayout.com/) - 诺曼布局介绍
- [Colemak 官网](https://colemak.com/) - 类似的人体工学布局
- [QMK 固件](https://qmk.fm/) - 可编程键盘固件
- [VIA Configurator](https://usevia.app/) - QMK 键盘配置工具
- [Karabiner-Elements](https://karabiner-elements.pqrs.org/) - macOS 键盘 remap 工具
- [rime-colemak](https://github.com/gkovacs/rime-colemak) - RIME 的 Colemak schema（可参考创建 rime-norman）
- [Hamster（仓鼠输入法）](https://apps.apple.com/app/仓鼠输入法/id1535_wrap) - iOS 版 RIME
- [Keyman](https://keyman.com/) - 多语言键盘应用
