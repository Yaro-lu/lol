# 小程序合集

一些日常用得上的独立小工具：图片处理、视频创作、文件整理和开奖查询。

**项目导航：[lol-lu.cn](https://lol-lu.cn/#tools)** · 每个工具都有自己的目录，集中放置说明、源码或成品下载入口。

## 找到你需要的工具

[Releases 下载](https://github.com/Yaro-lu/lol/releases/latest) · [完整源码包](https://github.com/Yaro-lu/lol/releases/latest/download/lol-tools-source.zip)

主库与 Releases 统一列出以下 **8 个工具**。只有成品的工具在主库保留说明和下载入口，程序附件保存在 Releases；原有历史发布继续保留。

| 工具 | 用途 | 使用方式 | 入口 |
| --- | --- | --- | --- |
| 图片转 ICO | 将 PNG、JPG 等图片转换为多尺寸 ICO 图标 | Python 图形界面 | [说明与源码](tools/image-to-ico/) |
| 剪映 video | 处理剪映已渲染的复合片段，作为普通视频打开 | Windows 可执行程序 | [使用说明与下载](tools/jianying-video/) |
| 文件名清理 | 递归清理文件和文件夹名称中的特殊字符 | Python 图形界面 | [说明与源码](tools/filename-cleaner/) |
| 双色球 / 大乐透查询 | 按期号、号码查询开奖结果与中奖情况 | Python 图形界面，需联网 | [说明与源码](tools/lottery-checker/) |
| AI 图像与视频生成 | 在网页中调用 Seedance 视频、Seedream 图片模型 | 单文件网页，自备方舟 API Key | [说明与网页文件](tools/ai-media-workspace/) |
| 图片转 PDF＋Word | 多张图片转为单个 PDF 和 Word 文档 | Windows 已编译程序 | [说明与下载](tools/images-to-pdf-word/) |
| 图片转 PDF | 多张图片合并为单个 PDF | Windows 已编译程序 | [说明与下载](tools/images-to-pdf/) |
| 简单锁屏 | 独立锁屏小工具 | Windows 已编译程序 | [说明与下载](tools/lock-screen/) |

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
├── images-to-pdf-word/   图片转 PDF＋Word（成品下载说明）
├── images-to-pdf/        图片转 PDF（成品下载说明）
├── lock-screen/          简单锁屏（成品下载说明）
└── ai-media-workspace/    AI 图像与视频生成
    ├── index.html
    └── README.md
```

## 以后添加工具

每个工具放进 `tools/<工具名>/`，附上自己的 README；有第三方 Python 依赖时放在该目录的 `requirements.txt`。将入口补进上方工具表，根目录保持为总导航。

## 主库与 Releases 同步

`tools.json` 是这 8 个工具及发布附件的清单。GitHub Actions 在 `main` 的工具、清单或说明更新后发布对应提交的工具集合，也可在 Actions 中手动运行。

每次发布包含当前主库源码包、各源码工具的独立包、剪映程序，以及原有 Releases 的 4 份成品附件。原成品按 SHA-256 核对后复制到新发布，不改动历史附件。Release 说明逐项列出主库目录与下载链接，并注明对应的 Git 提交。

增加工具时同步更新 `tools.json` 与上方导航表，避免主库和下载页各自维护一份不同的名单。
