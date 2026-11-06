# 图片转 ICO

将 PNG、JPG、JPEG 图片保存为包含多种尺寸的 ICO 图标。

## 运行

需要 Python 3、Tkinter 和 Pillow。在仓库根目录执行：

```bash
python -m pip install -r tools/image-to-ico/requirements.txt
python tools/image-to-ico/main.py
```

Tkinter 随部分 Python 发行版提供；未包含时需通过系统包管理器安装。

## 使用

1. 点击输入框旁的“浏览”，选择图片。
2. 选择输出目录。
3. 点击“开始转换”。

程序在输出目录生成 `output.ico`，包含 16、32、48、64、128 和 256 像素六种尺寸。相同输出目录里已有的 `output.ico` 会被覆盖。

[返回工具合集](../../README.md)
