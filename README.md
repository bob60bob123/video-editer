# Video Editor (视频编辑器)

> A lightweight desktop video editor built with PyQt5 and FFmpeg.

[![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)](https://github.com/bob60bob123/video-make)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 功能特性

- **视频合并** — 将多个视频文件合并为一个
- **音视频混合** — 将音频与视频混合，支持混合/替换原音多种模式
- **音频提取** — 从视频中提取音频，支持 MP3/AAC/WAV/FLAC 格式
- **字幕添加** — 支持 SRT 和 ASS 字幕文件
- **文字水印** — 添加文字水印，支持位置、颜色、透明度设置
- **格式转换** — 视频格式转换，支持 MP4/MKV 输出
- **多语言界面** — 支持简体中文和 English 界面切换

## 系统要求

- Windows 10/11
- Python 3.8+
- FFmpeg（已打包在项目中）

## 快速开始

1. 双击运行 `start.bat`
2. 选择功能标签页
3. 添加视频文件并设置参数
4. 点击执行按钮

## 从源码运行

```bash
pip install PyQt5
python main.py
```

> 注意：首次运行需要确保 FFmpeg 可用（项目已自带）。

---

## Features

- **Video Merge** — Merge multiple video files into one
- **Audio Mix** — Mix audio with video, supports mix/replace original audio modes
- **Audio Extract** — Extract audio from video, supports MP3/AAC/WAV/FLAC formats
- **Subtitles** — Add SRT and ASS subtitle files
- **Text Watermark** — Add text watermarks with position, color, and opacity settings
- **Format Convert** — Convert video format, supports MP4/MKV output
- **Multi-language UI** — Supports Chinese and English interface switching

## Project Structure

```
video-make/
├── main.py              # PyQt5 主程序
├── ffmpeg_utils.py      # FFmpeg 封装工具
├── i18n.py              # 国际化模块
├── track_widget.py      # 时间轴组件
├── start.bat            # Windows 启动脚本
├── requirements.txt     # Python 依赖
├── README.md            # 本文件
├── LICENSE              # MIT 许可证
└── ffmpeg-8.1.1-essentials_build/  # FFmpeg 二进制
```

## Dependencies

```
PyQt5>=5.15.0
```

## License

MIT License — see [LICENSE](LICENSE) file.
