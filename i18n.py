# -*- coding: utf-8 -*-
"""
国际化模块 - 中英文界面支持
"""

LANG_CN = "cn"
LANG_EN = "en"

_strings = {
    LANG_CN: {
        # 主窗口
        "app_title": "视频编辑器 v1.0",
        "output_dir": "输出目录:",
        "select_dir": "选择目录",
        "ready": "就绪",

        # 标签页名称
        "tab_merge": "视频合并",
        "tab_audio_mix": "音视频混合",
        "tab_extract_audio": "音频提取",
        "tab_subtitle": "字幕添加",
        "tab_watermark": "文字水印",
        "tab_convert": "格式转换",

        # 视频合并
        "merge_info": "将多个视频文件合并为一个",
        "video_list": "视频文件列表",
        "add_videos": "添加视频",
        "remove_selected": "移除选中",
        "clear_list": "清空列表",
        "move_up": "上移",
        "move_down": "下移",
        "output_filename": "输出文件名:",
        "output_format": "输出格式:",
        "start_merge": "开始合并",
        "mp4_h264": "MP4 (H.264)",
        "mkv": "MKV",

        # 音视频混合
        "audio_mix_info": "将音频与视频混合",
        "video_file": "视频文件",
        "audio_file": "音频文件",
        "select_video": "选择视频",
        "add_audio": "添加音频",
        "remove_audio": "移除选中",
        "clear_audio": "清空列表",
        "mix_settings": "混音设置",
        "mode": "模式:",
        "mix_original": "混合原音",
        "replace_original": "替换原音",
        "audio_length": "音频长度:",
        "fill_silence": "音频不足时用静音填充",
        "loop_play": "音频不足时循环播放",
        "loop_single": "单曲循环（无限循环）",
        "loop_count": "循环次数:",
        "music_volume": "音乐音量:",
        "add_audio_btn": "添加音频",

        # 音频提取
        "extract_info": "从视频文件中提取音频音乐",
        "input_file": "输入文件",
        "output_file": "输出设置",
        "output_filename": "输出文件名:",
        "output_format_label": "输出格式:",
        "extract_btn": "提取音频",
        "merge_videos": "合并视频",
        "at_least_2_videos": "请至少添加2个视频文件",
        "add_audio_warning": "请至少添加一个音频文件",
        "select_video_subtitle_warning": "请选择视频和字幕文件",
        "subtitle": "字幕",
        "subtitle_format": "字幕格式",
        "audio": "音频",
        "mp3": "MP3",
        "aac": "AAC",
        "wav": "WAV",
        "flac": "FLAC",

        # 字幕添加
        "subtitle_info": "为视频添加字幕文件 (支持 SRT 和 ASS)",
        "subtitle_file": "字幕文件",
        "select_subtitle": "选择字幕",
        "subtitle_encoding": "字幕编码:",
        "auto_detect": "自动检测",
        "add_subtitle_btn": "添加字幕",

        # 文字水印
        "watermark_info": "为视频添加文字水印",
        "watermark_text": "水印文字:",
        "watermark_default": "水印文字",
        "text_settings": "文字设置",
        "text_content": "文字内容",
        "white": "白色",
        "font_size": "字体大小:",
        "font_color": "字体颜色:",
        "select_color": "选择颜色",
        "position": "位置:",
        "position_tl": "左上",
        "position_tc": "中上",
        "position_tr": "右上",
        "position_lc": "左中",
        "position_cc": "居中",
        "position_rc": "右中",
        "position_bl": "左下",
        "position_bc": "中下",
        "position_br": "右下",
        "opacity": "透明度:",
        "add_watermark_btn": "添加水印",
        "video": "视频",
        "select_videos_warning": "请选择要合并的视频",
        "no_videos_warning": "没有可合并的视频",
        "add_videos_warning": "请先添加视频",
        "select_video_warning2": "请选择视频",
        "select_subtitle_warning": "请选择字幕文件",
        "enter_watermark_warning": "请输入水印文字",

        # 格式转换
        "convert_info": "转换视频格式",
        "convert_btn": "转换格式",

        # 对话框
        "ffmpeg_error": "FFmpeg 错误",
        "ffmpeg_not_found": "FFmpeg 不可用",
        "warning": "警告",
        "success": "成功",
        "error": "错误",
        "select_video_warning": "请选择要转换的文件",
        "select_video_for_extract_warning": "请选择要提取音频的视频文件",
        "merge_success": "视频合并成功",
        "merge_error": "合并失败",
        "audio_added": "音频添加成功",
        "audio_add_error": "音频添加失败",
        "extract_success": "音频提取成功",
        "extract_error": "提取失败",
        "subtitle_added": "字幕添加成功",
        "subtitle_add_error": "字幕添加失败",
        "watermark_added": "水印添加成功",
        "watermark_add_error": "水印添加失败",
        "convert_success": "格式转换成功",
        "convert_error": "转换失败",
        "no_audio_track": "视频文件中没有音轨，无法提取音频",
        "no_audio_track_mix": "视频文件没有音轨，无法使用混合模式。请选择「替换原音」模式。",
        "input_file_not_exist": "输入文件不存在",

        # 状态消息
        "merging": "正在合并视频...",
        "adding_audio": "正在添加音频...",
        "extracting_audio": "正在提取音频...",
        "adding_subtitle": "正在添加字幕...",
        "adding_watermark": "正在添加水印...",
        "converting": "正在转换格式...",
        "processing": "处理中... {}%",

        # 语言选择
        "language": "语言:",
        "chinese": "简体中文",
        "english": "English",
    },

    LANG_EN: {
        # 主窗口
        "app_title": "Video Editor v1.0",
        "output_dir": "Output:",
        "select_dir": "Browse",
        "ready": "Ready",

        # 标签页名称
        "tab_merge": "Merge Videos",
        "tab_audio_mix": "Audio Mix",
        "tab_extract_audio": "Extract Audio",
        "tab_subtitle": "Subtitles",
        "tab_watermark": "Text Watermark",
        "tab_convert": "Convert Format",

        # 视频合并
        "merge_info": "Merge multiple video files into one",
        "video_list": "Video File List",
        "add_videos": "Add Videos",
        "remove_selected": "Remove Selected",
        "clear_list": "Clear List",
        "move_up": "Move Up",
        "move_down": "Move Down",
        "output_filename": "Output filename:",
        "output_format": "Output format:",
        "start_merge": "Start Merge",
        "mp4_h264": "MP4 (H.264)",
        "mkv": "MKV",

        # 音视频混合
        "audio_mix_info": "Mix audio with video",
        "video_file": "Video File",
        "audio_file": "Audio File",
        "select_video": "Select Video",
        "add_audio": "Add Audio",
        "remove_audio": "Remove Selected",
        "clear_audio": "Clear List",
        "mix_settings": "Mix Settings",
        "mode": "Mode:",
        "mix_original": "Mix with original",
        "replace_original": "Replace original",
        "audio_length": "Audio length:",
        "fill_silence": "Pad with silence if audio is shorter",
        "loop_play": "Loop if audio is shorter",
        "loop_single": "Single loop (infinite)",
        "loop_count": "Loop count:",
        "music_volume": "Music volume:",
        "add_audio_btn": "Add Audio",

        # 音频提取
        "extract_info": "Extract audio from video file",
        "input_file": "Input File",
        "output_file": "Output Settings",
        "output_filename": "Output filename:",
        "output_format_label": "Output format:",
        "extract_btn": "Extract Audio",
        "merge_videos": "Merge Videos",
        "at_least_2_videos": "Please add at least 2 video files",
        "add_audio_warning": "Please add at least one audio file",
        "select_video_subtitle_warning": "Please select video and subtitle files",
        "subtitle": "Subtitle",
        "subtitle_format": "Subtitle format",
        "audio": "Audio",
        "mp3": "MP3",
        "aac": "AAC",
        "wav": "WAV",
        "flac": "FLAC",

        # 字幕添加
        "subtitle_info": "Add subtitle file to video (SRT and ASS supported)",
        "subtitle_file": "Subtitle File",
        "select_subtitle": "Select Subtitle",
        "subtitle_encoding": "Encoding:",
        "auto_detect": "Auto-detect",
        "add_subtitle_btn": "Add Subtitles",

        # 文字水印
        "watermark_info": "Add text watermark to video",
        "watermark_text": "Watermark text:",
        "watermark_default": "Watermark",
        "text_settings": "Text Settings",
        "text_content": "Text content",
        "white": "White",
        "font_size": "Font size:",
        "font_color": "Font color:",
        "select_color": "Pick Color",
        "position": "Position:",
        "position_tl": "Top Left",
        "position_tc": "Top Center",
        "position_tr": "Top Right",
        "position_lc": "Middle Left",
        "position_cc": "Center",
        "position_rc": "Middle Right",
        "position_bl": "Bottom Left",
        "position_bc": "Bottom Center",
        "position_br": "Bottom Right",
        "opacity": "Opacity:",
        "add_watermark_btn": "Add Watermark",
        "video": "Video",
        "select_videos_warning": "Please select videos to merge",
        "no_videos_warning": "No videos to merge",
        "add_videos_warning": "Please add videos first",
        "select_video_warning2": "Please select a video",
        "select_subtitle_warning": "Please select a subtitle file",
        "enter_watermark_warning": "Please enter watermark text",

        # 格式转换
        "convert_info": "Convert video format",
        "convert_btn": "Convert",

        # 对话框
        "ffmpeg_error": "FFmpeg Error",
        "ffmpeg_not_found": "FFmpeg not available",
        "warning": "Warning",
        "success": "Success",
        "error": "Error",
        "select_video_warning": "Please select a file to convert",
        "select_video_for_extract_warning": "Please select a video file to extract audio",
        "merge_success": "Videos merged successfully",
        "merge_error": "Merge failed",
        "audio_added": "Audio added successfully",
        "audio_add_error": "Audio add failed",
        "extract_success": "Audio extracted successfully",
        "extract_error": "Extract failed",
        "subtitle_added": "Subtitles added successfully",
        "subtitle_add_error": "Subtitle add failed",
        "watermark_added": "Watermark added successfully",
        "watermark_add_error": "Watermark add failed",
        "convert_success": "Format converted successfully",
        "convert_error": "Convert failed",
        "no_audio_track": "No audio track in video file, cannot extract audio",
        "no_audio_track_mix": "Video has no audio track, cannot use mix mode. Please select 'Replace original'.",
        "input_file_not_exist": "Input file does not exist",

        # 状态消息
        "merging": "Merging videos...",
        "adding_audio": "Adding audio...",
        "extracting_audio": "Extracting audio...",
        "adding_subtitle": "Adding subtitles...",
        "adding_watermark": "Adding watermark...",
        "converting": "Converting format...",
        "processing": "Processing... {}%",

        # 语言选择
        "language": "Language:",
        "chinese": "简体中文",
        "english": "English",
    }
}


def T(key, lang=LANG_CN):
    """获取翻译字符串"""
    return _strings.get(lang, _strings[LANG_CN]).get(key, key)


# 位置选项（显示文本, FFmpeg位置key）
POSITION_OPTIONS_CN = [
    ("左上", "top-left"), ("中上", "top-center"), ("右上", "top-right"),
    ("左中", "middle-left"), ("居中", "center"), ("右中", "middle-right"),
    ("左下", "bottom-left"), ("中下", "bottom-center"), ("右下", "bottom-right")
]
POSITION_OPTIONS_EN = [
    ("Top Left", "top-left"), ("Top Center", "top-center"), ("Top Right", "top-right"),
    ("Middle Left", "middle-left"), ("Center", "center"), ("Middle Right", "middle-right"),
    ("Bottom Left", "bottom-left"), ("Bottom Center", "bottom-center"), ("Bottom Right", "bottom-right")
]

# 混音模式
MIX_MODE_CN = ["混合原音", "替换原音"]
MIX_MODE_EN = ["Mix with original", "Replace original"]

# 音频长度模式
AUDIO_LEN_MODE_CN = ["音频不足时用静音填充", "音频不足时循环播放", "单曲循环（无限循环）"]
AUDIO_LEN_MODE_EN = ["Pad with silence if shorter", "Loop if shorter", "Single loop (infinite)"]
