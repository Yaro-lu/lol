# 小程序合集

一些日常用得上的独立小工具：图片处理、视频创作、文件整理和开奖查询。

**项目导航：[lol-lu.cn](https://lol-lu.cn/#tools)** · 每个工具的文件、依赖和说明都放在自己的目录里。

## 找到你需要的工具

| 工具 | 用途 | 使用方式 | 入口 |
| --- | --- | --- | --- |
| 图片转 ICO | 将 PNG、JPG 等图片转换为多尺寸 ICO 图标 | Python 图形界面 | [说明与源码](tools/image-to-ico/) |
| 剪映 video | 处理剪映已渲染的复合片段，作为普通视频打开 | Windows 可执行程序 | [使用说明与下载](tools/jianying-video/) |
| 文件名清理 | 递归清理文件和文件夹名称中的特殊字符 | Python 图形界面 | [说明与源码](tools/filename-cleaner/) |
| 双色球 / 大乐透查询 | 按期号、号码查询开奖结果与中奖情况 | Python 图形界面，需联网 | [说明与源码](tools/lottery-checker/) |
| AI 图像与视频生成 | 在网页中调用 Seedance 视频、Seedream 图片模型 | 单文件网页，自备方舟 API Key | [说明与网页文件](tools/ai-media-workspace/) |

## 下载和运行

在仓库右上方选择 **Code → Download ZIP**，解压后进入对应工具目录。也可以使用 Git：

```bash
git clone https://github.com/Yaro-lu/lol.git
cd lol
```

- **Windows 程序**：进入 `tools/jianying-video/`，按目录内说明使用 `剪映video.exe`。
- **网页工具**：下载后打开 `tools/ai-media-workspace/index.html`；GitHub 文件预览页只显示源码。
- **Python 工具**：安装 Python 3 和对应目录列出的依赖，再运行 `main.py`。这三个工具均使用 Tkinter 图形界面，需要有桌面环境及 Tkinter。

例如，在仓库根目录启动图片转 ICO：

```bash
python -m pip install -r tools/image-to-ico/requirements.txt
python tools/image-to-ico/main.py
```

如果系统使用 `python3` 或 Windows 的 `py` 命令，将上述 `python` 替换为对应命令即可。其他工具的依赖和操作步骤见各自 README，无需一次安装所有工具的依赖。

## 目录

```text
tools/
├── image-to-ico/          图片转 ICO
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── jianying-video/        剪映片段处理
│   ├── 剪映video.exe
│   └── README.md
├── filename-cleaner/      文件名清理
│   ├── main.py
│   └── README.md
├── lottery-checker/       双色球 / 大乐透查询
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
└── ai-media-workspace/    AI 图像与视频生成
    ├── index.html
    └── README.md
```

## 以后添加工具

每个工具放进 `tools/<工具名>/`，附上自己的 README；有第三方 Python 依赖时放在该目录的 `requirements.txt`。将入口补进上方工具表，根目录保持为总导航。
