# -*- coding: utf-8 -*-
"""
轨道组件 - 可视化时间轴和轨道管理
支持视频轨道、音频轨道、水印轨道的可视化显示
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QSlider, QLabel, QScrollArea, QSizePolicy,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsPathItem, QFrame
)
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QMimeData, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QFont, QDrag


class TimeRuler(QWidget):
    """时间标尺组件"""
    
    def __init__(self, duration=60.0, parent=None):
        super().__init__(parent)
        self.duration = duration  # 总时长（秒）
        self.scale = 50.0  # 每秒像素数
        self.offset = 0.0  # 滚动偏移（秒）
        
    def set_duration(self, duration):
        self.duration = max(duration, 1.0)
        self.update()
        
    def set_scale(self, scale):
        self.scale = max(10, min(200, scale))
        self.update()
        
    def set_offset(self, offset):
        self.offset = max(0, offset)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景
        painter.fillRect(event.rect(), QColor("#2a2a2a"))
        
        # 计算可见范围
        start_sec = self.offset
        end_sec = self.offset + self.width() / self.scale
        
        # 绘制刻度
        painter.setPen(QColor("#888888"))
        font = QFont("Arial", 8)
        painter.setFont(font)
        
        # 主刻度（整秒）
        step = max(1, int(10 / self.scale * 10) // 10)
        if step < 1:
            step = 1
        if self.scale < 20:
            step = 5
        elif self.scale < 40:
            step = 2
            
        for sec in range(int(start_sec), int(end_sec) + 1, step):
            x = int((sec - self.offset) * self.scale)
            
            # 长刻度
            painter.setPen(QColor("#aaaaaa"))
            painter.drawLine(x, 0, x, 10 if sec % (step * 2) == 0 else 5)
            
            # 时间标签
            if sec % (step * 2) == 0:
                minutes = sec // 60
                seconds = sec % 60
                text = f"{minutes}:{seconds:02d}"
                painter.setPen(QColor("#cccccc"))
                painter.drawText(x + 2, 12, text)
                
        painter.setPen(QColor("#555555"))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)


class TrackSegment(QWidget):
    """轨道片段组件"""
    
    clicked = pyqtSignal()
    double_clicked = pyqtSignal()
    
    def __init__(self, name, start_time, duration, color="#4a9eff", parent=None):
        super().__init__(parent)
        self.name = name
        self.start_time = start_time
        self.duration = duration
        self.color = color
        self.selected = False
        self.dragging = False
        
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(24)
        self.setMaximumHeight(32)
        
    def set_duration(self, duration):
        self.duration = max(0.1, duration)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = event.rect()
        
        # 背景
        bg_color = QColor(self.color)
        if self.selected:
            bg_color = bg_color.lighter(130)
        painter.fillRect(rect, bg_color)
        
        # 边框
        border_color = QColor("#ffffff") if self.selected else QColor(self.color).darker(130)
        painter.setPen(QPen(border_color, 1 if self.selected else 0.5))
        painter.drawRect(rect.adjusted(1, 1, -1, -1))
        
        # 文字
        painter.setPen(QColor("#ffffff"))
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        text = self.name
        if self.width() > 60:
            text += f" {self.duration:.1f}s"
            
        painter.drawText(rect.adjusted(4, 0, -4, -2), Qt.AlignVCenter | Qt.AlignLeft, text)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier:
            self.double_clicked.emit()
        elif event.button() == Qt.LeftButton:
            self.clicked.emit()
            
    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()


class Track(QWidget):
    """单条轨道组件"""
    
    def __init__(self, name, track_type="video", color="#4a9eff", parent=None):
        super().__init__(parent)
        self.name = name
        self.track_type = track_type  # "video", "audio", "watermark"
        self.color = color
        self.segments = []
        self.scale = 50.0
        self.duration = 60.0
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 轨道标签
        label = QLabel(self.name)
        label.setFixedWidth(80)
        label.setStyleSheet(f"""
            background-color: {self.color};
            color: white;
            padding: 4px 8px;
            font-size: 11px;
            font-weight: bold;
        """)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # 轨道内容区域
        self.content_area = QScrollArea()
        self.content_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_area.setWidgetResizable(False)
        self.content_area.setFixedHeight(32)
        self.content_area.setStyleSheet("border: none; background-color: #333333;")
        
        self.content_widget = QWidget()
        self.content_widget.setMinimumHeight(32)
        self.content_widget.setStyleSheet("background-color: #333333;")
        
        content_layout = QHBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 4, 0, 4)
        content_layout.setSpacing(2)
        
        self.content_area.setWidget(self.content_widget)
        layout.addWidget(self.content_area, 1)
        
    def set_duration(self, duration):
        self.duration = max(duration, 1.0)
        total_width = int(self.duration * self.scale)
        self.content_widget.setMinimumWidth(total_width)
        
    def set_scale(self, scale):
        self.scale = max(20, min(200, scale))
        self.set_duration(self.duration)
        
    def add_segment(self, name, start_time, duration):
        """添加片段"""
        segment = TrackSegment(name, start_time, duration, self.color)
        segment.clicked.connect(lambda: self._on_segment_clicked(segment))
        
        # 设置位置
        x_pos = int(start_time * self.scale)
        segment.setFixedWidth(int(duration * self.scale))
        
        # 找到正确的插入位置
        for i, seg in enumerate(self.segments):
            if start_time < seg.start_time:
                self.segments.insert(i, segment)
                self._get_content_layout().insertWidget(i, segment)
                return segment
        
        self.segments.append(segment)
        self._get_content_layout().addWidget(segment)
        return segment
        
    def _get_content_layout(self):
        return self.content_widget.layout()
        
    def _on_segment_clicked(self, segment):
        """片段被点击"""
        # 清除其他选中状态
        for seg in self.segments:
            seg.selected = False
            seg.update()
        # 选中当前
        segment.selected = True
        segment.update()
        
    def clear(self):
        """清除所有片段"""
        for seg in self.segments:
            seg.deleteLater()
        self.segments.clear()
        
    def remove_selected(self):
        """移除选中的片段"""
        for seg in self.segments:
            if seg.selected:
                self.segments.remove(seg)
                seg.deleteLater()


class TimelineWidget(QWidget):
    """时间轴组件 - 包含多条轨道"""
    
    segment_double_clicked = pyqtSignal(object)  # 双击片段
    play_position_changed = pyqtSignal(float)  # 播放位置改变
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.duration = 60.0  # 默认60秒
        self.scale = 50.0  # 每秒像素数
        self.playhead_position = 0.0  # 播放头位置（秒）
        self.is_playing = False
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 时间标尺
        self.ruler = TimeRuler(self.duration, self)
        self.ruler.set_scale(self.scale)
        self.ruler.setFixedHeight(25)
        layout.addWidget(self.ruler)
        
        # 轨道容器
        self.tracks_container = QWidget()
        self.tracks_layout = QVBoxLayout(self.tracks_container)
        self.tracks_layout.setContentsMargins(0, 0, 0, 0)
        self.tracks_layout.setSpacing(1)
        self.tracks_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidget(self.tracks_container)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFixedHeight(100)
        scroll.setStyleSheet("border: none;")
        layout.addWidget(scroll)
        
        # 播放控制条
        control_layout = QHBoxLayout()
        control_layout.addSpacing(80)  # 对齐轨道标签
        
        self.playhead = QWidget()
        self.playhead.setFixedWidth(2)
        self.playhead.setFixedHeight(20)
        self.playhead.setStyleSheet("background-color: #ff4444;")
        
        # 播放头位置指示器
        self.playhead_container = QWidget()
        ph_layout = QHBoxLayout(self.playhead_container)
        ph_layout.setContentsMargins(0, 0, 0, 0)
        ph_layout.addSpacing(80)  # 标签宽度
        ph_layout.addWidget(self.playhead)
        ph_layout.addStretch()
        
        # 连接滚动信号
        scroll.horizontalScrollBar().valueChanged.connect(self._on_scroll)
        
        self.setMinimumHeight(150)
        
    def _on_scroll(self, value):
        """滚动时更新标尺"""
        offset_sec = value / self.scale
        self.ruler.set_offset(offset_sec)
        
    def add_track(self, name, track_type="video", color="#4a9eff"):
        """添加轨道"""
        track = Track(name, track_type, color)
        track.set_scale(self.scale)
        track.set_duration(self.duration)
        
        # 移除stretch，添加轨道，再添加stretch
        self.tracks_layout.insertWidget(self.tracks_layout.count() - 1, track)
        
        return track
        
    def set_duration(self, duration):
        """设置总时长"""
        self.duration = max(duration, 1.0)
        self.ruler.set_duration(self.duration)
        
        # 更新所有轨道
        for i in range(self.tracks_layout.count() - 1):
            item = self.tracks_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), Track):
                item.widget().set_duration(self.duration)
                
    def set_scale(self, scale):
        """设置缩放比例"""
        self.scale = max(20, min(200, scale))
        self.ruler.set_scale(self.scale)
        
        for i in range(self.tracks_layout.count() - 1):
            item = self.tracks_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), Track):
                item.widget().set_scale(self.scale)
                
    def set_playhead_position(self, position):
        """设置播放头位置"""
        self.playhead_position = max(0, min(position, self.duration))
        x_pos = int(self.playhead_position * self.scale)
        self.playhead.move(x_pos, 0)
        
    def add_segment(self, track_index, name, start_time, duration):
        """在指定轨道添加片段"""
        track = self._get_track(track_index)
        if track:
            return track.add_segment(name, start_time, duration)
        return None
        
    def _get_track(self, index):
        """获取指定索引的轨道"""
        count = 0
        for i in range(self.tracks_layout.count() - 1):
            item = self.tracks_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), Track):
                if count == index:
                    return item.widget()
                count += 1
        return None
        
    def get_tracks(self):
        """获取所有轨道"""
        tracks = []
        for i in range(self.tracks_layout.count() - 1):
            item = self.tracks_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), Track):
                tracks.append(item.widget())
        return tracks


class ProcessingProgressWidget(QWidget):
    """处理进度组件 - 显示当前操作的可视化进度"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.operation_name = ""
        self.current_time = 0.0
        self.total_time = 0.0
        self.progress_percent = 0
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # 操作名称
        self.name_label = QLabel("")
        self.name_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        layout.addWidget(self.name_label)
        
        # 进度条容器
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        # 进度条背景
        self.progress_bar = QWidget()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("background-color: #333333; border-radius: 4px;")
        progress_layout.addWidget(self.progress_bar)
        
        # 百分比
        self.percent_label = QLabel("0%")
        self.percent_label.setFixedWidth(40)
        self.percent_label.setStyleSheet("color: #888888; font-size: 10px;")
        progress_layout.addWidget(self.percent_label)
        
        layout.addWidget(progress_container)
        
        # 时间显示
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: #666666; font-size: 10px;")
        layout.addWidget(self.time_label)
        
    def set_operation(self, name, total_time=0):
        """设置操作信息"""
        self.operation_name = name
        self.total_time = total_time
        self.current_time = 0
        self.progress_percent = 0
        self.name_label.setText(name)
        self._update_display()
        
    def update_progress(self, current_time, total_time=None):
        """更新进度"""
        self.current_time = current_time
        if total_time is not None:
            self.total_time = total_time
        if self.total_time > 0:
            self.progress_percent = int(self.current_time / self.total_time * 100)
        self._update_display()
        
    def _update_display(self):
        """更新显示"""
        # 更新百分比
        self.percent_label.setText(f"{self.progress_percent}%")
        
        # 更新进度条宽度
        bar_width = max(10, int(self.progress_percent / 100.0 * self.progress_bar.parent().width()))
        self.progress_bar.setFixedWidth(bar_width)
        
        # 更新时间
        self.time_label.setText(f"{self._format_time(self.current_time)} / {self._format_time(self.total_time)}")
        
    def _format_time(self, seconds):
        """格式化时间"""
        if seconds <= 0:
            return "00:00"
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"
        
    def clear(self):
        """清除进度显示"""
        self.operation_name = ""
        self.current_time = 0
        self.total_time = 0
        self.progress_percent = 0
        self.name_label.setText("")
        self.percent_label.setText("0%")
        self.progress_bar.setFixedWidth(0)
        self.time_label.setText("00:00 / 00:00")