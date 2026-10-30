# ColorPicker 取色器

Windows 屏幕取色小工具（Python + Tkinter），实时读取鼠标光标下的像素颜色，支持手动输入 RGB / HEX 显示颜色。

## 功能特性

- **Enable 模式**（默认）：约 50ms 连续采样，实时显示光标处颜色，输入框只读
- **Disable 模式**：停止采样，可手动输入 R/G/B（0–255）与 HEX（`#RRGGBB`），双向同步：
  - 输入 RGB → 自动更新 HEX 与颜色预览
  - 输入 HEX（回车或失焦提交）→ 自动更新 RGB 与颜色预览
  - 失焦时自动规范化：RGB 钳制到 0–255，HEX 统一为大写 `#RRGGBB`
- 无边框置顶悬浮窗，可拖拽（从标签、预览或空白区域按住拖动），记住窗口位置
- 系统托盘图标：`Hide/Show`（双击/默认项）与 `Exit`
- 单实例：再次运行会激活已打开的窗口，不会重复启动
- 窗口位置保存在程序目录下的 `config.json`

## 运行环境

- Windows（取色基于 Windows API）
- Python 3.10+

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 使用说明

1. 启动后默认处于 **Enable** 模式，移动鼠标即可看到 RGB / HEX 与右侧预览实时变化。
2. 点选 **Disable** 停止取色，此时可编辑四个输入框：
   - `R:` / `G:` / `B:`：各输入 0–255 的整数，输入合法时 HEX 与预览同步更新
   - `HEX:`：输入 `#RRGGBB` 或 `RRGGBB`（不区分大小写），按回车或点击别处后 RGB 与预览同步更新
3. 点选 **Enable** 恢复实时取色（输入框变回只读并显示采样值）。
4. 托盘图标右键菜单：`Hide/Show` 隐藏或显示窗口，`Exit` 保存窗口位置并退出。
5. 关闭窗口请使用托盘 `Exit`（无边框窗口没有标题栏关闭按钮）。

## 打包为 exe

```bash
pyinstaller ColorPicker.spec
```

生成 `dist/ColorPicker.exe`（单文件、无控制台窗口，已内置图标）。打包后 `config.json` 保存在 exe 同目录。

## 图标来源

应用图标 `icons8-color-picker-48.ico` 来自 [Icons8](https://icons8.com)。
