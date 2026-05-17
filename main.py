# -*- coding: utf-8 -*-
"""
视频编辑器 - PyQt5 主程序
功能：视频合并、音视频混合、字幕添加、文字水印
"""
import sys
import os
import json
import threading
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
    QListWidget, QFileDialog, QMessageBox, QProgressBar,
    QComboBox, QSpinBox, QDoubleSpinBox, QColorDialog,
    QGroupBox, QFormLayout, QCheckBox, QScrollArea,
    QFrame, QGridLayout, QMenu, QAction, QActionGroup
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QKeySequence

from ffmpeg_utils import FFmpegUtils
from i18n import T, LANG_CN, LANG_EN, MIX_MODE_CN, MIX_MODE_EN, AUDIO_LEN_MODE_CN, AUDIO_LEN_MODE_EN, POSITION_OPTIONS_CN, POSITION_OPTIONS_EN

CONFIG_FILE = str(Path(__file__).parent / "config.json")
MAX_HISTORY = 10


class Worker(QObject):
    """后台工作线程"""
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int, str)  # (percent, message)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            # 传入进度回调函数
            self.kwargs['progress_callback'] = self._progress_wrapper
            success, message = self.func(*self.args, **self.kwargs)
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, str(e))

    def _progress_wrapper(self, percent, current_sec):
        """将 FFmpeg 进度回调转为 Qt 信号（线程安全）"""
        self.progress.emit(percent, f"处理中... {percent}%")


class VideoEditorWindow(QMainWindow):
    """视频编辑器主窗口"""

    def __init__(self):
        super().__init__()
        self.ffmpeg_utils = FFmpegUtils()
        self.worker = None
        self.output_dir = str(Path.home() / "Videos")
        self.output_history = []
        self.lang = LANG_CN  # 默认中文

        self._load_config()

        # 检查 FFmpeg
        ffmpeg_ok, ffmpeg_msg = self.ffmpeg_utils.check_ffmpeg()
        if not ffmpeg_ok:
            QMessageBox.critical(self, T("ffmpeg_error", self.lang), f"{T('ffmpeg_not_found', self.lang)}: {ffmpeg_msg}")
            sys.exit(1)

        self.init_ui()

    def _load_config(self):
        """加载配置"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                self.output_history = cfg.get('output_history', [])
                # 确保历史目录仍然存在
                self.output_history = [d for d in self.output_history if os.path.exists(d)]
                if self.output_history:
                    self.output_dir = self.output_history[0]
                # 加载语言设置
                saved_lang = cfg.get('language', LANG_CN)
                if saved_lang in (LANG_CN, LANG_EN):
                    self.lang = saved_lang
        except Exception:
            self.output_history = []

    def _save_config(self):
        """保存配置"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'output_history': self.output_history,
                    'language': self.lang
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


    def _get_stylesheet(self):
        """获取现代化样式表"""
        return """
            /* 全局样式 */
            QMainWindow {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
                font-size: 10pt;
            }

            /* 标签页样式 */
            QTabWidget::pane {
                border: 1px solid #313244;
                border-radius: 8px;
                background-color: #181825;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #313244;
                color: #a6adc8;
                padding: 10px 20px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #cba6f7;
                color: #1e1e2e;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #45475a;
            }

            /* 按钮样式 */
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
            QPushButton:pressed {
                background-color: #585b70;
            }
            QPushButton:disabled {
                background-color: #313244;
                color: #6c7086;
            }

            /* 主要按钮 */
            QPushButton[objectName="primary"] {
                background-color: #89b4fa;
                color: #1e1e2e;
                font-weight: bold;
            }
            QPushButton[objectName="primary"]:hover {
                background-color: #b4befe;
            }

            /* 输入框样式 */
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px 10px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #89b4fa;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #a6adc8;
            }

            /* 列表样式 */
            QListWidget {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 6px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #89b4fa;
                color: #1e1e2e;
            }
            QListWidget::item:hover:!selected {
                background-color: #313244;
            }

            /* 分组框样式 */
            QGroupBox {
                font-weight: bold;
                border: 1px solid #45475a;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #cba6f7;
            }

            /* 滑块样式 */
            QSlider::groove:horizontal {
                height: 6px;
                background-color: #313244;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                height: 14px;
                background-color: #89b4fa;
                border-radius: 7px;
                margin: -4px 0;
            }
            QSlider::sub-page:horizontal {
                background-color: #89b4fa;
                border-radius: 3px;
            }

            /* 标签样式 */
            QLabel {
                color: #cdd6f4;
            }

            /* 进度条样式 */
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #313244;
                text-align: center;
                color: #cdd6f4;
            }
            QProgressBar::chunk {
                background-color: #89b4fa;
                border-radius: 6px;
            }

            /* 滚动条样式 */
            QScrollBar:vertical {
                width: 10px;
                background-color: #1e1e2e;
            }
            QScrollBar::handle:vertical {
                background-color: #45475a;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #585b70;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                height: 10px;
                background-color: #1e1e2e;
            }
            QScrollBar::handle:horizontal {
                background-color: #45475a;
                border-radius: 5px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #585b70;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }

            /* 菜单样式 */
            QMenu {
                background-color: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #313244;
            }
            QMenuBar {
                background-color: #1e1e2e;
            }
            QMenuBar::item {
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #313244;
                border-radius: 4px;
            }
        """


    def _add_output_history(self, path):
        """添加输出目录到历史"""
        folder = os.path.dirname(path)
        if not folder or not os.path.exists(folder):
            return
        if folder in self.output_history:
            self.output_history.remove(folder)
        self.output_history.insert(0, folder)
        if len(self.output_history) > MAX_HISTORY:
            self.output_history = self.output_history[:MAX_HISTORY]
        self._save_config()

    def _select_output_dir(self):
        """选择输出目录（带历史记录）"""
        # 构建菜单：历史目录 + 分隔符 + 浏览...
        menu = QMenu(self)

        # 历史目录
        group = QActionGroup(menu)
        for i, d in enumerate(self.output_history):
            action = menu.addAction(d)
            action.setData(d)
            group.addAction(action)
            if i == 0:
                font = action.font()
                font.setBold(True)
                action.setFont(font)
                action.setShortcut(QKeySequence(str(i + 1)))

        menu.addSeparator()
        browse_action = menu.addAction("浏览其他目录...")
        browse_action.setData("__browse__")

        menu.addSeparator()
        clear_action = menu.addAction("清空历史记录")
        clear_action.setData("__clear__")

        selected = menu.exec_(QCursor.pos())
        if not selected:
            return None
        data = selected.data()
        if data == "__browse__":
            folder = QFileDialog.getExistingDirectory(
                self, "选择输出目录", self.output_dir
            )
            if folder:
                self.output_dir = folder
                self._add_output_history(os.path.join(folder, "dummy.mp4"))
                return folder
            return None
        elif data == "__clear__":
            self.output_history = []
            self._save_config()
            return None
        elif data:
            self.output_dir = data
            return data
        return None

    def _on_select_output_dir(self):
        """点击选择目录按钮"""
        menu = QMenu(self)

        # 历史目录
        group = QActionGroup(menu)
        for i, d in enumerate(self.output_history):
            action = menu.addAction(d)
            action.setData(d)
            group.addAction(action)
            if i == 0:
                font = action.font()
                font.setBold(True)
                action.setFont(font)
                action.setShortcut(QKeySequence(str(i + 1)))

        menu.addSeparator()
        browse_action = menu.addAction("浏览其他目录...")
        browse_action.setData("__browse__")

        if self.output_history:
            menu.addSeparator()
            clear_action = menu.addAction("清空历史记录")
            clear_action.setData("__clear__")

        selected = menu.exec_(self.btn_output_dir.mapToGlobal(self.btn_output_dir.rect().bottomLeft()))
        if not selected:
            return
        data = selected.data()
        if data == "__browse__":
            folder = QFileDialog.getExistingDirectory(
                self, "选择输出目录", self.output_dir
            )
            if folder:
                self.output_dir = folder
                self._add_output_history(os.path.join(folder, "dummy.mp4"))
                self.output_dir_label.setText(folder)
                return
        elif data == "__clear__":
            self.output_history = []
            self._save_config()
            return
        elif data:
            self.output_dir = data
            self.output_dir_label.setText(data)

    def get_output_path(self, filename, format_combo):
        """获取完整输出路径"""
        format_ext = ".mp4" if format_combo.currentIndex() == 0 else ".mkv"
        name = filename if filename.endswith(format_ext) else filename + format_ext
        output_dir = self.output_dir if os.path.exists(self.output_dir) else str(Path.home() / "Videos")
        return os.path.join(output_dir, name)

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(T("app_title", self.lang))
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet(self._get_stylesheet())

        # 中央部件
        if self.centralWidget():
            self.centralWidget().deleteLater()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # 工具栏
        toolbar_layout = QHBoxLayout()

        # 语言选择
        toolbar_layout.addWidget(QLabel(T("language", self.lang)))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([T("chinese", LANG_CN), T("english", LANG_EN)])
        self.lang_combo.setCurrentIndex(0 if self.lang == LANG_CN else 1)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        self.lang_combo.setMaximumWidth(120)
        toolbar_layout.addWidget(self.lang_combo)

        toolbar_layout.addSpacing(20)

        # 输出目录选择栏
        toolbar_layout.addWidget(QLabel(T("output_dir", self.lang)))
        self.output_dir_label = QLabel(self.output_dir)
        self.output_dir_label.setStyleSheet("color: gray;")
        self.output_dir_label.setMinimumWidth(400)
        toolbar_layout.addWidget(self.output_dir_label)
        self.btn_output_dir = QPushButton(T("select_dir", self.lang))
        self.btn_output_dir.setMaximumWidth(100)
        self.btn_output_dir.clicked.connect(self._on_select_output_dir)
        toolbar_layout.addWidget(self.btn_output_dir)
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        # 标签页
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # 创建各个功能标签页
        self.create_merge_tab()
        self.create_audio_tab()
        self.create_extract_audio_tab()
        self.create_subtitle_tab()
        self.create_watermark_tab()
        self.create_convert_tab()

        # 状态栏
        self.status_label = QLabel(T("ready", self.lang))
        main_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.show()

    def _on_lang_changed(self, index):
        """切换语言"""
        new_lang = LANG_CN if index == 0 else LANG_EN
        if new_lang != self.lang:
            self.lang = new_lang
            self._save_config()
            # 重新初始化界面
            self.init_ui()

    def create_merge_tab(self):
        """视频合并标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 说明
        info_label = QLabel(T("merge_info", self.lang))
        layout.addWidget(info_label)

        # 视频列表
        list_group = QGroupBox(T("video_list", self.lang))
        list_layout = QVBoxLayout()

        self.merge_list = QListWidget()
        self.merge_list.setSelectionMode(QListWidget.MultiSelection)
        list_layout.addWidget(self.merge_list)

        btn_layout = QHBoxLayout()
        self.btn_add_videos = QPushButton(T("add_videos", self.lang))
        self.btn_add_videos.clicked.connect(self.add_merge_videos)
        btn_layout.addWidget(self.btn_add_videos)

        self.btn_remove_video = QPushButton(T("remove_selected", self.lang))
        self.btn_remove_video.clicked.connect(self.remove_merge_video)
        btn_layout.addWidget(self.btn_remove_video)

        self.btn_clear_list = QPushButton(T("clear_list", self.lang))
        self.btn_clear_list.clicked.connect(self.merge_list.clear)
        btn_layout.addWidget(self.btn_clear_list)

        list_layout.addLayout(btn_layout)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # 输出设置
        output_group = QGroupBox(T("output_file", self.lang))
        output_layout = QFormLayout()

        self.merge_output_name = QLineEdit("merged_video.mp4")
        output_layout.addRow(T("output_filename", self.lang), self.merge_output_name)

        self.merge_format = QComboBox()
        self.merge_format.addItems([T("mp4_h264", self.lang), T("mkv", self.lang)])
        output_layout.addRow(T("output_format", self.lang), self.merge_format)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # 执行按钮
        self.btn_execute_merge = QPushButton(T("merge_videos", self.lang))
        self.btn_execute_merge.clicked.connect(self.execute_merge)
        layout.addWidget(self.btn_execute_merge)

        layout.addStretch()
        self.tabs.addTab(tab, T("tab_merge", self.lang))

    def create_audio_tab(self):
        """音视频混合标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info_label = QLabel(T("audio_mix_info", self.lang))
        layout.addWidget(info_label)

        # 视频文件
        video_group = QGroupBox(T("video_file", self.lang))
        video_layout = QFormLayout()
        self.audio_video_path = QLineEdit()
        self.audio_video_path.setReadOnly(True)
        btn_select_video = QPushButton(T("select_video", self.lang))
        btn_select_video.clicked.connect(lambda: self.select_file(self.audio_video_path, "视频"))
        video_layout.addRow(T("video", self.lang) + ":", self.audio_video_path)
        video_layout.addRow("", btn_select_video)
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)

        # 音频文件
        audio_group = QGroupBox(T("audio_file", self.lang))
        audio_layout = QVBoxLayout()

        self.audio_audio_list = QListWidget()
        self.audio_audio_list.setSelectionMode(QListWidget.MultiSelection)
        audio_layout.addWidget(self.audio_audio_list)

        btn_audio_layout = QHBoxLayout()
        self.btn_add_audio = QPushButton(T("add_audio", self.lang))
        self.btn_add_audio.clicked.connect(self.add_audio_files)
        btn_audio_layout.addWidget(self.btn_add_audio)

        self.btn_remove_audio = QPushButton(T("remove_selected", self.lang))
        self.btn_remove_audio.clicked.connect(self.remove_audio_files)
        btn_audio_layout.addWidget(self.btn_remove_audio)

        self.btn_clear_audio = QPushButton(T("clear_list", self.lang))
        self.btn_clear_audio.clicked.connect(self.audio_audio_list.clear)
        btn_audio_layout.addWidget(self.btn_clear_audio)

        audio_layout.addLayout(btn_audio_layout)
        self.audio_info_label = QLabel("")
        self.audio_info_label.setStyleSheet("color: gray;")
        audio_layout.addWidget(self.audio_info_label)

        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)

        # 混音设置
        mix_group = QGroupBox(T("mix_settings", self.lang))
        mix_layout = QFormLayout()

        self.audio_mix_mode = QComboBox()
        self.audio_mix_mode.addItems([T("mix_original", self.lang), T("replace_original", self.lang)])
        mix_layout.addRow(T("mode", self.lang), self.audio_mix_mode)

        self.audio_duration_mode = QComboBox()
        self.audio_duration_mode.addItems([T("fill_silence", self.lang), T("loop_play", self.lang), T("loop_single", self.lang)])
        mix_layout.addRow(T("audio_length", self.lang), self.audio_duration_mode)

        self.audio_loop_count = QSpinBox()
        self.audio_loop_count.setRange(2, 100)
        self.audio_loop_count.setValue(3)
        self.audio_loop_count.setEnabled(False)
        self.audio_loop_count.valueChanged.connect(
            lambda v: self.audio_duration_mode.setCurrentIndex(1) if v > 1 else None
        )
        mix_layout.addRow(T("loop_count", self.lang), self.audio_loop_count)

        self.audio_volume = QDoubleSpinBox()
        self.audio_volume.setRange(0.0, 2.0)
        self.audio_volume.setSingleStep(0.1)
        self.audio_volume.setValue(1.0)
        mix_layout.addRow(T("music_volume", self.lang), self.audio_volume)

        mix_group.setLayout(mix_layout)
        layout.addWidget(mix_group)

        # 输出设置
        out_group = QGroupBox(T("output_file", self.lang))
        out_layout = QFormLayout()
        self.audio_output_name = QLineEdit("video_with_audio.mp4")
        self.audio_output_format = QComboBox()
        self.audio_output_format.addItems([T("mp4_h264", self.lang), T("mkv", self.lang)])
        out_layout.addRow(T("output_filename", self.lang), self.audio_output_name)
        out_layout.addRow(T("output_format", self.lang), self.audio_output_format)
        out_group.setLayout(out_layout)
        layout.addWidget(out_group)

        self.btn_execute_audio = QPushButton(T("add_audio", self.lang))
        self.btn_execute_audio.clicked.connect(self.execute_add_audio)
        layout.addWidget(self.btn_execute_audio)

        layout.addStretch()
        self.tabs.addTab(tab, T("tab_audio_mix", self.lang))

    def create_extract_audio_tab(self):
        """音频提取标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info_label = QLabel(T("extract_info", self.lang))
        layout.addWidget(info_label)

        # 输入文件
        input_group = QGroupBox(T("input_file", self.lang))
        input_layout = QFormLayout()
        self.extract_input_path = QLineEdit()
        self.extract_input_path.setReadOnly(True)
        btn_select = QPushButton(T("select_video", self.lang))
        btn_select.clicked.connect(lambda: self.select_file(self.extract_input_path, "视频"))
        input_layout.addRow(T("video", self.lang) + ":", self.extract_input_path)
        input_layout.addRow("", btn_select)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 输出设置
        out_group = QGroupBox(T("output_file", self.lang))
        out_layout = QFormLayout()
        self.extract_output_name = QLineEdit("audio")
        out_layout.addRow(T("output_filename", self.lang), self.extract_output_name)

        self.extract_format = QComboBox()
        self.extract_format.addItems([T("mp3", self.lang), T("aac", self.lang), T("wav", self.lang), T("flac", self.lang)])
        out_layout.addRow(T("output_format", self.lang), self.extract_format)

        out_group.setLayout(out_layout)
        layout.addWidget(out_group)

        self.btn_execute_extract = QPushButton(T("extract_btn", self.lang))
        self.btn_execute_extract.clicked.connect(self.execute_extract_audio)
        layout.addWidget(self.btn_execute_extract)

        layout.addStretch()
        self.tabs.addTab(tab, T("tab_extract_audio", self.lang))

    def create_subtitle_tab(self):
        """字幕添加标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info_label = QLabel(T("subtitle_info", self.lang))
        layout.addWidget(info_label)

        # 视频文件
        video_group = QGroupBox(T("video_file", self.lang))
        video_layout = QFormLayout()
        self.sub_video_path = QLineEdit()
        self.sub_video_path.setReadOnly(True)
        btn_select = QPushButton(T("select_video", self.lang))
        btn_select.clicked.connect(lambda: self.select_file(self.sub_video_path, "视频"))
        video_layout.addRow(T("video", self.lang) + ":", self.sub_video_path)
        video_layout.addRow("", btn_select)
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)

        # 字幕文件
        sub_group = QGroupBox(T("subtitle_file", self.lang))
        sub_layout = QFormLayout()
        self.sub_file_path = QLineEdit()
        self.sub_file_path.setReadOnly(True)
        btn_select_sub = QPushButton(T("select_subtitle", self.lang))
        btn_select_sub.clicked.connect(lambda: self.select_file(self.sub_file_path, "字幕",
            "Subtitle Files (*.srt *.ass);;All Files (*)"))
        sub_layout.addRow(T("subtitle", self.lang) + ":", self.sub_file_path)
        sub_layout.addRow("", btn_select_sub)
        sub_group.setLayout(sub_layout)
        layout.addWidget(sub_group)

        # 字幕设置
        settings_group = QGroupBox("字幕设置")
        settings_layout = QFormLayout()
        self.sub_codec = QComboBox()
        self.sub_codec.addItems([T("auto_detect", self.lang), "SRT", "ASS"])
        settings_layout.addRow(T("subtitle_format", self.lang) + ":", self.sub_codec)
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # 输出设置
        out_group = QGroupBox(T("output_file", self.lang))
        out_layout = QFormLayout()
        self.sub_output_name = QLineEdit("video_with_subtitle.mp4")
        self.sub_output_format = QComboBox()
        self.sub_output_format.addItems([T("mp4_h264", self.lang), T("mkv", self.lang)])
        out_layout.addRow(T("output_filename", self.lang), self.sub_output_name)
        out_layout.addRow(T("output_format", self.lang), self.sub_output_format)
        out_group.setLayout(out_layout)
        layout.addWidget(out_group)

        self.btn_execute_sub = QPushButton(T("add_subtitle_btn", self.lang))
        self.btn_execute_sub.clicked.connect(self.execute_add_subtitle)
        layout.addWidget(self.btn_execute_sub)

        layout.addStretch()
        self.tabs.addTab(tab, T("tab_subtitle", self.lang))

    def create_watermark_tab(self):
        """文字水印标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info_label = QLabel(T("watermark_info", self.lang))
        layout.addWidget(info_label)

        # 视频文件
        video_group = QGroupBox(T("video_file", self.lang))
        video_layout = QFormLayout()
        self.wm_video_path = QLineEdit()
        self.wm_video_path.setReadOnly(True)
        btn_select = QPushButton(T("select_video", self.lang))
        btn_select.clicked.connect(lambda: self.select_file(self.wm_video_path, "视频"))
        video_layout.addRow(T("video", self.lang) + ":", self.wm_video_path)
        video_layout.addRow("", btn_select)
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)

        # 文字设置
        text_group = QGroupBox(T("text_settings", self.lang))
        text_layout = QFormLayout()

        self.wm_text = QLineEdit(T("watermark_default", self.lang))
        text_layout.addRow(T("text_content", self.lang) + ":", self.wm_text)

        self.wm_font_size = QSpinBox()
        self.wm_font_size.setRange(8, 200)
        self.wm_font_size.setValue(48)
        text_layout.addRow(T("font_size", self.lang), self.wm_font_size)

        self.wm_color = QPushButton(T("white", self.lang))
        self.wm_color.setStyleSheet("background-color: white; color: black;")
        self.wm_color_value = "white"
        self.wm_color.clicked.connect(self.select_watermark_color)
        text_layout.addRow(T("font_color", self.lang), self.wm_color)

        self.wm_opacity = QDoubleSpinBox()
        self.wm_opacity.setRange(0.1, 1.0)
        self.wm_opacity.setSingleStep(0.1)
        self.wm_opacity.setValue(1.0)
        text_layout.addRow(T("opacity", self.lang) + ":", self.wm_opacity)

        self.wm_position = QComboBox()
        position_opts = POSITION_OPTIONS_CN if self.lang == LANG_CN else POSITION_OPTIONS_EN
        self.wm_position.addItems([opt[0] for opt in position_opts])
        self.wm_position.setCurrentIndex(6)  # 默认左下
        text_layout.addRow(T("position", self.lang), self.wm_position)

        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        # 输出设置
        out_group = QGroupBox(T("output_file", self.lang))
        out_layout = QFormLayout()
        self.wm_output_name = QLineEdit("video_with_watermark.mp4")
        self.wm_output_format = QComboBox()
        self.wm_output_format.addItems([T("mp4_h264", self.lang), T("mkv", self.lang)])
        out_layout.addRow(T("output_filename", self.lang), self.wm_output_name)
        out_layout.addRow(T("output_format", self.lang), self.wm_output_format)
        out_group.setLayout(out_layout)
        layout.addWidget(out_group)

        self.btn_execute_wm = QPushButton(T("add_watermark_btn", self.lang))
        self.btn_execute_wm.clicked.connect(self.execute_add_watermark)
        layout.addWidget(self.btn_execute_wm)

        layout.addStretch()
        self.tabs.addTab(tab, T("tab_watermark", self.lang))

    def create_convert_tab(self):
        """格式转换标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info_label = QLabel(T("convert_info", self.lang))
        layout.addWidget(info_label)

        # 输入文件
        input_group = QGroupBox(T("input_file", self.lang))
        input_layout = QFormLayout()
        self.conv_input_path = QLineEdit()
        self.conv_input_path.setReadOnly(True)
        btn_select = QPushButton("选择文件")
        btn_select.clicked.connect(lambda: self.select_file(self.conv_input_path, "视频"))
        input_layout.addRow(T("video", self.lang) + ":", self.conv_input_path)
        input_layout.addRow("", btn_select)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 输出设置
        out_group = QGroupBox(T("output_file", self.lang))
        out_layout = QFormLayout()
        self.conv_output_name = QLineEdit("converted_video")
        out_layout.addRow(T("output_filename", self.lang), self.conv_output_name)

        self.conv_format = QComboBox()
        self.conv_format.addItems([T("mp4_h264", self.lang), T("mkv", self.lang)])
        out_layout.addRow(T("output_format", self.lang), self.conv_format)

        out_group.setLayout(out_layout)
        layout.addWidget(out_group)

        self.btn_execute_conv = QPushButton(T("convert_btn", self.lang))
        self.btn_execute_conv.clicked.connect(self.execute_convert)
        layout.addWidget(self.btn_execute_conv)

        layout.addStretch()
        self.tabs.addTab(tab, T("tab_convert", self.lang))

    # ============ 辅助方法 ============

    def select_file(self, line_edit, file_type, filter_str=None):
        """选择文件"""
        if filter_str is None:
            filter_str = f"{file_type} Files (*.mp4 *.mkv *.avi *.mov *.flv *.wmv);;All Files (*)"

        file_path, _ = QFileDialog.getOpenFileName(self, f"选择{file_type}", self.output_dir, filter_str)
        if file_path:
            line_edit.setText(file_path)
            self.output_dir = str(Path(file_path).parent)

    def select_audio_and_show_info(self):
        """选择音频文件并显示视频/音频时长对比"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择音频", self.output_dir,
            "Audio Files (*.mp3 *.wav *.aac *.flac *.ogg *.m4a);;All Files (*)"
        )
        if not file_path:
            return
        self.audio_audio_path.setText(file_path)
        self.output_dir = str(Path(file_path).parent)

        # 显示时长信息
        audio_dur = self.ffmpeg_utils.get_duration_seconds(file_path)
        video_path = self.audio_video_path.text().strip()
        if video_path and os.path.exists(video_path):
            video_dur = self.ffmpeg_utils.get_duration_seconds(video_path)
            if audio_dur > 0 and video_dur > 0:
                if video_dur > audio_dur:
                    ratio = video_dur / audio_dur
                    self.audio_info_label.setText(
                        f"视频: {self._format_dur(video_dur)} | 音频: {self._format_dur(audio_dur)} | 视频更长 {ratio:.1f}x"
                    )
                elif audio_dur > video_dur:
                    self.audio_info_label.setText(
                        f"视频: {self._format_dur(video_dur)} | 音频: {self._format_dur(audio_dur)} | 音频更长"
                    )
                else:
                    self.audio_info_label.setText(
                        f"视频: {self._format_dur(video_dur)} | 音频: {self._format_dur(audio_dur)} | 时长相同"
                    )
            else:
                self.audio_info_label.setText("")
        else:
            self.audio_info_label.setText(f'{T("audio", self.lang)}: {self._format_dur(audio_dur)}' if audio_dur > 0 else "")

    def _format_dur(self, seconds: float) -> str:
        """格式化时长为 MM:SS 或 HH:MM:SS"""
        if seconds <= 0:
            return "00:00"
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    def add_merge_videos(self):
        """添加视频到合并列表"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择视频文件", self.output_dir,
            "Video Files (*.mp4 *.mkv *.avi *.mov *.flv *.wmv);;All Files (*)"
        )
        for f in files:
            self.merge_list.addItem(f)
            self.output_dir = str(Path(f).parent)

    def remove_merge_video(self):
        """移除选中的视频"""
        for item in self.merge_list.selectedItems():
            self.merge_list.takeItem(self.merge_list.row(item))

    def add_audio_files(self):
        """添加音频文件到列表"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择音频文件", self.output_dir,
            "Audio Files (*.mp3 *.wav *.aac *.flac *.ogg *.m4a);;All Files (*)"
        )
        if not files:
            return
        for f in files:
            self.audio_audio_list.addItem(f)
            self.output_dir = str(Path(f).parent)
        self._update_audio_info_label()

    def remove_audio_files(self):
        """移除选中的音频"""
        for item in self.audio_audio_list.selectedItems():
            self.audio_audio_list.takeItem(self.audio_audio_list.row(item))
        self._update_audio_info_label()

    def _update_audio_info_label(self):
        """更新音频时长信息标签"""
        count = self.audio_audio_list.count()
        if count == 0:
            self.audio_info_label.setText("")
            return

        audio_files = [self.audio_audio_list.item(i).text() for i in range(count)]
        video_path = self.audio_video_path.text().strip()

        total_audio_dur = 0.0
        for af in audio_files:
            total_audio_dur += self.ffmpeg_utils.get_duration_seconds(af)

        video_dur = 0.0
        if video_path and os.path.exists(video_path):
            video_dur = self.ffmpeg_utils.get_duration_seconds(video_path)

        if video_dur > 0 and total_audio_dur > 0:
            if video_dur > total_audio_dur:
                ratio = video_dur / total_audio_dur
                self.audio_info_label.setText(
                    f"{count}个音频 | 总计: {self._format_dur(total_audio_dur)} | 视频: {self._format_dur(video_dur)} | 视频更长 {ratio:.1f}x"
                )
            else:
                self.audio_info_label.setText(
                    f"{count}个音频 | 总计: {self._format_dur(total_audio_dur)} | 视频: {self._format_dur(video_dur)}"
                )
        elif total_audio_dur > 0:
            self.audio_info_label.setText(
                f"{count}个音频 | 总计: {self._format_dur(total_audio_dur)}"
            )

    def select_watermark_color(self):
        """选择水印颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.wm_color_value = color.name()
            self.wm_color.setText(color.name())
            self.wm_color.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")

    def get_output_path(self, filename, format_combo):
        """获取完整输出路径"""
        format_ext = ".mp4" if format_combo.currentIndex() == 0 else ".mkv"
        name = filename if filename.endswith(format_ext) else filename + format_ext
        output_dir = self.output_dir if os.path.exists(self.output_dir) else str(Path.home() / "Videos")
        return os.path.join(output_dir, name)

    def run_worker(self, func, *args, on_complete=None):
        """运行后台任务"""
        self.btn_execute_merge.setEnabled(False)
        self.btn_execute_audio.setEnabled(False)
        self.btn_execute_extract.setEnabled(False)
        self.btn_execute_sub.setEnabled(False)
        self.btn_execute_wm.setEnabled(False)
        self.btn_execute_conv.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.worker = Worker(func, *args)
        self.worker.progress.connect(self.on_progress_update)
        self.worker.finished.connect(lambda ok, msg: self.on_worker_complete(ok, msg, on_complete))
        threading.Thread(target=self.worker.run, daemon=True).start()

    @pyqtSlot(int, str)
    def on_progress_update(self, percent, message):
        """进度更新回调"""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)

    @pyqtSlot(bool, str)
    def on_worker_complete(self, success, message, callback=None):
        """工作完成回调"""
        self.progress_bar.setVisible(False)
        self.btn_execute_merge.setEnabled(True)
        self.btn_execute_audio.setEnabled(True)
        self.btn_execute_extract.setEnabled(True)
        self.btn_execute_sub.setEnabled(True)
        self.btn_execute_wm.setEnabled(True)
        self.btn_execute_conv.setEnabled(True)

        if success:
            self.status_label.setText(message)
            QMessageBox.information(self, T("success", self.lang), message)
        else:
            self.status_label.setText(T("error", self.lang) + f": {message}")
            QMessageBox.critical(self, T("error", self.lang), message)

        if callback:
            callback(success, message)

    # ============ 执行方法 ============

    def execute_merge(self):
        """执行视频合并"""
        count = self.merge_list.count()
        if count < 2:
            QMessageBox.warning(self, T("warning", self.lang), T("at_least_2_videos", self.lang))
            return

        video_files = [self.merge_list.item(i).text() for i in range(count)]
        output_name = self.merge_output_name.text().strip()
        output_path = self.get_output_path(output_name, self.merge_format)

        self.status_label.setText(T("merging", self.lang))
        self.run_worker(self.ffmpeg_utils.merge_videos, video_files, output_path)

    def execute_add_audio(self):
        """执行添加音频"""
        video_file = self.audio_video_path.text().strip()
        audio_count = self.audio_audio_list.count()

        if not video_file:
            QMessageBox.warning(self, T("warning", self.lang), T("select_video_warning2", self.lang))
            return
        if audio_count == 0:
            QMessageBox.warning(self, T("warning", self.lang), T("add_audio_warning", self.lang))
            return

        audio_files = [self.audio_audio_list.item(i).text() for i in range(audio_count)]

        output_name = self.audio_output_name.text().strip()
        output_path = self.get_output_path(output_name, self.audio_output_format)
        mix_audio = self.audio_mix_mode.currentIndex() == 0
        volume = self.audio_volume.value()
        duration_mode = self.audio_duration_mode.currentIndex()
        loop_count = self.audio_loop_count.value()

        self.status_label.setText(T("adding_audio", self.lang))
        self.run_worker(
            self.ffmpeg_utils.add_audio_to_video,
            video_file, audio_files, output_path, volume, mix_audio,
            duration_mode, loop_count
        )

    def execute_add_subtitle(self):
        """执行添加字幕"""
        video_file = self.sub_video_path.text().strip()
        subtitle_file = self.sub_file_path.text().strip()

        if not video_file or not subtitle_file:
            QMessageBox.warning(self, T("warning", self.lang), T("select_video_subtitle_warning", self.lang))
            return

        output_name = self.sub_output_name.text().strip()
        output_path = self.get_output_path(output_name, self.sub_output_format)

        codec = self.sub_codec.currentIndex()
        codec_map = ["auto", "srt", "ass"]
        codec_value = codec_map[codec]

        self.status_label.setText(T("adding_subtitle", self.lang))
        self.run_worker(
            self.ffmpeg_utils.add_subtitle,
            video_file, subtitle_file, output_path, codec_value
        )

    def execute_add_watermark(self):
        """执行添加水印"""
        video_file = self.wm_video_path.text().strip()
        text = self.wm_text.text().strip()

        if not video_file or not text:
            QMessageBox.warning(self, T("warning", self.lang), T("enter_watermark_warning", self.lang))
            return

        output_name = self.wm_output_name.text().strip()
        output_path = self.get_output_path(output_name, self.wm_output_format)

        font_size = self.wm_font_size.value()
        color = self.wm_color_value
        opacity = self.wm_opacity.value()
        position_opts = POSITION_OPTIONS_CN if self.lang == LANG_CN else POSITION_OPTIONS_EN
        position = position_opts[self.wm_position.currentIndex()][1]

        self.status_label.setText(T("adding_watermark", self.lang))
        self.run_worker(
            self.ffmpeg_utils.add_text_watermark,
            video_file, output_path, text, font_size, color, position, opacity
        )

    def execute_convert(self):
        """执行格式转换"""
        input_file = self.conv_input_path.text().strip()
        output_name = self.conv_output_name.text().strip()

        if not input_file:
            QMessageBox.warning(self, T("warning", self.lang), T("select_video_warning", self.lang))
            return

        format_ext = ".mp4" if self.conv_format.currentIndex() == 0 else ".mkv"
        output_name = output_name if output_name.endswith(format_ext) else output_name + format_ext
        output_path = os.path.join(self.output_dir, output_name)

        self.status_label.setText(T("converting", self.lang))
        self.run_worker(
            self.ffmpeg_utils.convert_format,
            input_file, output_path
        )

    def execute_extract_audio(self):
        """执行音频提取"""
        input_file = self.extract_input_path.text().strip()
        output_name = self.extract_output_name.text().strip()

        if not input_file:
            QMessageBox.warning(self, T("warning", self.lang), T("select_video_for_extract_warning", self.lang))
            return

        format_exts = [".mp3", ".aac", ".wav", ".flac"]
        format_ext = format_exts[self.extract_format.currentIndex()]
        output_name = output_name if output_name.endswith(format_ext) else output_name + format_ext
        output_path = os.path.join(self.output_dir, output_name)

        self.status_label.setText(T("extracting_audio", self.lang))
        self.run_worker(
            self.ffmpeg_utils.extract_audio,
            input_file, output_path, format_ext[1:]  # 去掉点的扩展名
        )


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = VideoEditorWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
