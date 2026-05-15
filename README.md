# Video Editor (视频编辑器 / 動画編集ツール / 동영상 편집기)

> A lightweight desktop video editor built with PyQt5 and FFmpeg.
> 支持简体中文、English、简体中文（简体）、日本語、한국어

[![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)](https://github.com/bob60bob123/video-make)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🌍 Multi-language README

<details>
<summary><b>🇨🇳 简体中文</b></summary>

### 功能特性

- **视频合并** — 将多个视频文件合并为一个
- **音视频混合** — 将音频与视频混合，支持混合/替换原音多种模式
- **音频提取** — 从视频中提取音频，支持 MP3/AAC/WAV/FLAC 格式
- **字幕添加** — 支持 SRT 和 ASS 字幕文件
- **文字水印** — 添加文字水印，支持位置、颜色、透明度设置
- **格式转换** — 视频格式转换，支持 MP4/MKV 输出
- **多语言界面** — 支持简体中文和 English 界面切换

### 系统要求

- Windows 10/11
- Python 3.8+
- FFmpeg（已打包在项目中）

### 快速开始

1. 双击运行 `start.bat`
2. 选择功能标签页
3. 添加视频文件并设置参数
4. 点击执行按钮

### 从源码运行

```bash
pip install PyQt5
python main.py
```

> 注意：首次运行需要确保 FFmpeg 可用（项目已自带）。

</details>

<details>
<summary><b>🇺🇸 English</b></summary>

### Features

- **Video Merge** — Merge multiple video files into one
- **Audio Mix** — Mix audio with video, supports mix/replace original audio modes
- **Audio Extract** — Extract audio from video, supports MP3/AAC/WAV/FLAC formats
- **Subtitles** — Add SRT and ASS subtitle files
- **Text Watermark** — Add text watermarks with position, color, and opacity settings
- **Format Convert** — Convert video format, supports MP4/MKV output
- **Multi-language UI** — Supports Chinese and English interface switching

### System Requirements

- Windows 10/11
- Python 3.8+
- FFmpeg (bundled in the project)

### Quick Start

1. Double-click `start.bat` to run
2. Select a feature tab
3. Add video files and configure parameters
4. Click the execute button

### Run from Source

```bash
pip install PyQt5
python main.py
```

> Note: FFmpeg is bundled — no additional installation needed.

</details>

<details>
<summary><b>🇯🇵 日本語</b></summary>

### 機能

- **動画結合** — 複数の動画を一つの動画に結合
- **音声混合** — 動画に音声を混合、元音との混合/置換モード対応
- **音声抽出** — 動画から音声を抽出、MP3/AAC/WAV/FLAC形式対応
- **字幕追加** — SRTおよびASS字幕ファイルに対応
- **テキスト透かし** — 位置、色、透明度を設定可能なテキスト透かし
- **形式変換** — 動画形式変換、MP4/MKV出力対応
- **多言語インターフェース** — 中文と英語のインターフェース切り替え対応

### 動作環境

- Windows 10/11
- Python 3.8+
- FFmpeg（プロジェクトにバンドル済み）

### 使い方

1. `start.bat`をダブルクリックして起動
2. 機能タブを選択
3. 動画ファイルを追加してパラメータを設定
4. 実行ボタンをクリック

### ソースから実行

```bash
pip install PyQt5
python main.py
```

> 注意：FFmpegはバンドル済み、追加インストール不要。

</details>

<details>
<summary><b>🇰🇷 한국어</b></summary>

### 기능

- **동영상 병합** — 여러 동영상 파일을 하나의 동영상으로 결합
- **음성 혼합** — 동영상에 음성을 혼합, 원본 음성 혼합/대체 모드 지원
- **음성 추출** — 동영상에서 음성 추출, MP3/AAC/WAV/FLAC 형식 지원
- **자막 추가** — SRT 및 ASS 자막 파일 지원
- **텍스트 워터마크** — 위치, 색상, 투명도 설정이 가능한 텍스트 워터마크
- **형식 변환** — 동영상 형식 변환, MP4/MKV 출력 지원
- **다국어 인터페이스** — 중국어 및 영어 인터페이스 전환 지원

### 동작 환경

- Windows 10/11
- Python 3.8+
- FFmpeg (프로젝트에 번들됨)

### 사용법

1. `start.bat`를 더블클릭하여 실행
2. 기능 탭을 선택
3. 동영상 파일을 추가하고 매개변수 설정
4. 실행 버튼 클릭

### 소스에서 실행

```bash
pip install PyQt5
python main.py
```

> 참고: FFmpeg가 번들되어 있어 추가 설치가 필요 없습니다.

</details>

---

## 📁 Project Structure

```
video-make/
├── main.py              # PyQt5 主程序
├── ffmpeg_utils.py      # FFmpeg 封装工具
├── i18n.py              # 国际化模块
├── start.bat            # Windows 启动脚本
├── requirements.txt     # Python 依赖
├── README.md            # 本文件
├── LICENSE              # MIT 许可证
└── ffmpeg-8.1.1-essentials_build/  # FFmpeg 二进制（不包含在仓库中）
```

## 📦 Dependencies

```
PyQt5>=5.15.0
```

## 📄 License

MIT License — see [LICENSE](LICENSE) file.
