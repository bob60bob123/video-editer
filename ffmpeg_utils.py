# -*- coding: utf-8 -*-
"""
FFmpeg 封装工具 - 视频编辑器的核心操作模块
"""
import subprocess
import os
import sys
import re
import threading
from pathlib import Path


class FFmpegUtils:
    """FFmpeg 操作封装类"""

    def __init__(self):
        # FFmpeg 路径
        self.ffmpeg_dir = Path(__file__).parent / "ffmpeg-8.1.1-essentials_build" / "bin"
        self.ffmpeg_path = self.ffmpeg_dir / "ffmpeg.exe"
        self.ffprobe_path = self.ffmpeg_dir / "ffprobe.exe"

    def _parse_duration(self, duration_str: str) -> float:
        """解析 HH:MM:SS.ms 格式为秒数"""
        if not duration_str:
            return 0.0
        parts = duration_str.strip().split(':')
        if len(parts) == 3:
            h, m, s = parts
            return float(h) * 3600 + float(m) * 60 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return float(m) * 60 + float(s)
        return 0.0

    def _parse_ffmpeg_progress(self, line: str) -> float:
        """从 FFmpeg stderr 解析进度百分比 (0-100)"""
        # FFmpeg 输出格式: time=00:00:01.50 bitrate=...
        match = re.search(r'time=(\d{2}:\d{2}:\d{2}\.\d{2})', line)
        if match:
            current = self._parse_duration(match.group(1))
            # 总时长需要在外部传入，这里返回-1表示无法计算
            return current
        return -1

    def _run_with_progress(self, cmd: list, total_duration: float = 0,
                           progress_callback=None) -> tuple:
        """
        运行 FFmpeg 命令并实时报告进度
        progress_callback: 回调函数，接收 (percent: int, current_seconds: float) 参数
        total_duration: 视频总时长（秒），传0则不计算百分比
        """
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        result_stderr = []
        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
            if line:
                result_stderr.append(line)
                if total_duration > 0 and progress_callback:
                    current = self._parse_ffmpeg_progress(line)
                    if current > 0:
                        percent = min(int(current / total_duration * 100), 100)
                        progress_callback(percent, current)

        process.wait()
        stderr = ''.join(result_stderr)

        if process.returncode == 0:
            if progress_callback and total_duration > 0:
                progress_callback(100, total_duration)
            return True, stderr
        else:
            return False, stderr

    def check_ffmpeg(self) -> tuple:
        """检查 FFmpeg 是否可用，返回 (是否可用, 版本信息)"""
        try:
            result = subprocess.run(
                [str(self.ffmpeg_path), "-version"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                return True, version
            return False, "FFmpeg 运行失败"
        except Exception as e:
            return False, str(e)

    def get_media_info(self, file_path: str) -> dict:
        """获取媒体文件信息"""
        cmd = [
            str(self.ffprobe_path),
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=30)
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
        except Exception:
            pass
        return {}

    def get_duration_seconds(self, file_path: str) -> float:
        """获取视频/音频总时长（秒），获取失败返回0"""
        info = self.get_media_info(file_path)
        try:
            format_info = info.get('format', {})
            duration = format_info.get('duration', '0')
            return float(duration)
        except (ValueError, TypeError):
            return 0.0

    def merge_videos(self, video_files: list, output_file: str, progress_callback=None) -> tuple:
        """
        合并多个视频文件
        video_files: 视频文件路径列表
        output_file: 输出文件路径
        return: (成功与否, 消息)
        """
        if len(video_files) < 2:
            return False, "需要至少2个视频文件"

        # 创建临时文件列表
        list_file = output_file + ".list.txt"
        with open(list_file, 'w', encoding='utf-8') as f:
            for video in video_files:
                f.write(f"file '{video}'\n")

        cmd = [
            str(self.ffmpeg_path),
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            "-y",
            output_file
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=3600)
            if os.path.exists(list_file):
                os.remove(list_file)

            if result.returncode == 0:
                return True, f"视频合并成功: {output_file}"
            else:
                error = result.stderr[-500:] if result.stderr else "未知错误"
                return False, f"合并失败: {error}"
        except Exception as e:
            if os.path.exists(list_file):
                os.remove(list_file)
            return False, f"合并异常: {str(e)}"

    def _concat_audio_files(self, audio_files: list, output_file: str) -> tuple:
        """将多个音频文件拼接为一个"""
        list_file = output_file + ".audio_list.txt"
        try:
            with open(list_file, 'w', encoding='utf-8') as f:
                for af in audio_files:
                    f.write(f"file '{af}'\n")

            cmd = [
                str(self.ffmpeg_path),
                "-f", "concat",
                "-safe", "0",
                "-i", list_file,
                "-c", "copy",
                "-y",
                output_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=3600)
            return result.returncode == 0, result.stderr
        finally:
            if os.path.exists(list_file):
                os.remove(list_file)

    def add_audio_to_video(self, video_file: str, audio_files, output_file: str,
                           audio_volume: float = 1.0, mix_audio: bool = True,
                           duration_mode: int = 0, loop_count: int = 3,
                           progress_callback=None) -> tuple:
        """
        将音频混入视频
        video_file: 视频文件路径
        audio_files: 音频文件路径或路径列表
        output_file: 输出文件路径
        audio_volume: 音频音量 (0.0-2.0)
        mix_audio: True=混合原音, False=替换原音
        duration_mode: 0=静音填充, 1=循环播放(loop_count次), 2=单曲循环(无限)
        loop_count: 循环次数（duration_mode=1时有效）
        progress_callback: 进度回调 (percent: int, current_sec: float)
        return: (成功与否, 消息)
        """
        # 统一为列表
        if isinstance(audio_files, str):
            audio_files = [audio_files]

        # 检查视频是否有音轨
        info = self.get_media_info(video_file)
        has_audio = False
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'audio':
                has_audio = True
                break

        if mix_audio and not has_audio:
            return False, "视频文件没有音轨，无法使用混合模式。请选择「替换原音」模式。"

        video_dur = self.get_duration_seconds(video_file)

        # ========== 多音频拼接 ==========
        if len(audio_files) > 1:
            # 先拼接多个音频为一个临时文件
            concat_audio = output_file + ".concat_audio.tmp"
            ok, err = self._concat_audio_files(audio_files, concat_audio)
            if not ok:
                return False, f"音频拼接失败: {err[-300:]}"
            audio_files = [concat_audio]

        single_audio = audio_files[0]
        audio_dur = self.get_duration_seconds(single_audio)

        if mix_audio:
            # ========== 混合原音模式 ==========
            if duration_mode == 0:
                filter_str = (
                    f"[0:a]volume=1[a0]; "
                    f"[1:a]volume={audio_volume}[a1]; "
                    f"[a1]apad=whole_dur={video_dur}[a1p]; "
                    f"[a0][a1p]amix=inputs=2:duration=first[aout]"
                )
                cmd = [
                    str(self.ffmpeg_path),
                    "-i", video_file,
                    "-i", single_audio,
                    "-filter_complex", filter_str,
                    "-map", "0:v",
                    "-map", "[aout]",
                    "-c:v", "copy",
                    "-shortest",
                    "-y",
                    output_file
                ]
            elif duration_mode == 1:
                loop_times = max(1, loop_count - 1)
                filter_str = (
                    f"[1:a]volume={audio_volume}[a1]; "
                    f"[a1]apad=whole_dur={video_dur}[a1p]; "
                    f"[0:a]volume=1[a0]; "
                    f"[a0][a1p]amix=inputs=2:duration=first[aout]"
                )
                cmd = [
                    str(self.ffmpeg_path),
                    "-i", video_file,
                    "-stream_loop", str(loop_times),
                    "-i", single_audio,
                    "-filter_complex", filter_str,
                    "-map", "0:v",
                    "-map", "[aout]",
                    "-c:v", "copy",
                    "-shortest",
                    "-y",
                    output_file
                ]
            else:
                filter_str = (
                    f"[1:a]volume={audio_volume},aloop=loop=-1:size=0[a1looped]; "
                    f"[a1looped]apad=whole_dur={video_dur}[a1p]; "
                    f"[0:a]volume=1[a0]; "
                    f"[a0][a1p]amix=inputs=2:duration=first[aout]"
                )
                cmd = [
                    str(self.ffmpeg_path),
                    "-i", video_file,
                    "-stream_loop", "0",
                    "-i", single_audio,
                    "-filter_complex", filter_str,
                    "-map", "0:v",
                    "-map", "[aout]",
                    "-c:v", "copy",
                    "-shortest",
                    "-y",
                    output_file
                ]

            total_duration = video_dur
            try:
                success, stderr = self._run_with_progress(cmd, total_duration, progress_callback)
                if len(audio_files) > 1 and os.path.exists(single_audio):
                    os.remove(single_audio)
                if success:
                    return True, f"音频添加成功: {output_file}"
                else:
                    error = stderr[-500:] if stderr else "未知错误"
                    return False, f"添加音频失败: {error}"
            except Exception as e:
                if len(audio_files) > 1 and os.path.exists(single_audio):
                    os.remove(single_audio)
                return False, f"添加音频异常: {str(e)}"
        else:
            # ========== 替换原音模式 ==========
            if duration_mode == 0:
                filter_str = f"[1:a]volume={audio_volume},apad=whole_dur={video_dur}[aout]"
                cmd = [
                    str(self.ffmpeg_path),
                    "-i", video_file,
                    "-i", single_audio,
                    "-filter_complex", filter_str,
                    "-map", "0:v",
                    "-map", "[aout]",
                    "-shortest",
                    "-y",
                    output_file
                ]
            elif duration_mode == 1:
                loop_times = max(1, loop_count - 1)
                cmd = [
                    str(self.ffmpeg_path),
                    "-i", video_file,
                    "-stream_loop", str(loop_times),
                    "-i", single_audio,
                    "-filter_complex", f"[1:a]volume={audio_volume}[aout]",
                    "-map", "0:v",
                    "-map", "[aout]",
                    "-shortest",
                    "-y",
                    output_file
                ]
            else:
                cmd = [
                    str(self.ffmpeg_path),
                    "-i", video_file,
                    "-stream_loop", "0",
                    "-i", single_audio,
                    "-filter_complex", f"[1:a]volume={audio_volume},aloop=loop=-1:size=0,apad=whole_dur={video_dur}[aout]",
                    "-map", "0:v",
                    "-map", "[aout]",
                    "-shortest",
                    "-y",
                    output_file
                ]

            total_duration = video_dur
            try:
                success, stderr = self._run_with_progress(cmd, total_duration, progress_callback)
                if len(audio_files) > 1 and os.path.exists(single_audio):
                    os.remove(single_audio)
                if success:
                    return True, f"音频添加成功: {output_file}"
                else:
                    error = stderr[-500:] if stderr else "未知错误"
                    return False, f"添加音频失败: {error}"
            except Exception as e:
                if len(audio_files) > 1 and os.path.exists(single_audio):
                    os.remove(single_audio)
                return False, f"添加音频异常: {str(e)}"

    def add_subtitle(self, video_file: str, subtitle_file: str, output_file: str,
                     subtitle_codec: str = "copy", progress_callback=None) -> tuple:
        """
        为视频添加字幕
        video_file: 视频文件路径
        subtitle_file: 字幕文件路径 (SRT/ASS)
        output_file: 输出文件路径
        subtitle_codec: 'srt', 'ass', 'copy'
        return: (成功与否, 消息)
        """
        ext = Path(subtitle_file).suffix.lower()

        if subtitle_codec == "auto":
            subtitle_codec = "srt" if ext == ".srt" else "ass"

        # 根据字幕格式选择编码器
        codec_map = {
            "srt": "srt",
            "ass": "ass",
            "copy": "copy"
        }
        codec = codec_map.get(subtitle_codec, "srt")

        cmd = [
            str(self.ffmpeg_path),
            "-i", video_file,
            "-f", "srt" if ext == ".srt" else "ass",
            "-i", subtitle_file,
            "-map", "0:v",
            "-map", "0:a",
            "-map", "1",
            "-c:v", "copy",
            "-c:a", "copy",
            "-c:s", codec,
            "-y",
            output_file
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=3600)
            if result.returncode == 0:
                return True, f"字幕添加成功: {output_file}"
            else:
                error = result.stderr[-500:] if result.stderr else "未知错误"
                return False, f"添加字幕失败: {error}"
        except Exception as e:
            return False, f"添加字幕异常: {str(e)}"

    def add_text_watermark(self, video_file: str, output_file: str,
                           text: str,
                           font_size: int = 24,
                           font_color: str = "white",
                           position: str = "bottom-right",
                           opacity: float = 1.0,
                           font_path: str = None,
                           progress_callback=None) -> tuple:
        """
        为视频添加文字水印
        video_file: 视频文件路径
        output_file: 输出文件路径
        text: 文字内容
        font_size: 字体大小
        font_color: 字体颜色 (white, black, red, #RRGGBB)
        position: 位置 (top-left, top-center, top-right, center, bottom-left, bottom-center, bottom-right)
        opacity: 不透明度 (0.0-1.0)
        font_path: 字体文件路径 (可选)
        progress_callback: 进度回调 (percent: int, current_sec: float)
        return: (成功与否, 消息)
        """
        import tempfile

        # 位置映射 - x/y 表达式中的 : 用 \: 转义，避免与 filter 参数分隔符冲突
        position_map = {
            "top-left": "x=10:y=10",
            "top-center": "x=(w-text_w)/2\\:y=10",
            "top-right": "x=w-text_w-10:y=10",
            "middle-left": "x=10:y=(h-text_h)/2",
            "center": "x=(w-text_w)/2\\:y=(h-text_h)/2",
            "middle-right": "x=w-text_w-10:y=(h-text_h)/2",
            "bottom-left": "x=10:y=h-text_h-10",
            "bottom-center": "x=(w-text_w)/2\\:y=h-text_h-10",
            "bottom-right": "x=w-text_w-10:y=h-text_h-10"
        }

        pos_str = position_map.get(position, "x=w-text_w-10:y=h-text_h-10")

        # 颜色处理
        color_map = {
            "white": "white",
            "black": "black",
            "red": "red",
            "yellow": "yellow"
        }
        color = color_map.get(font_color, font_color)

        # 字体路径 - 优先使用指定字体，否则使用默认字体
        if font_path and os.path.exists(font_path):
            font_str = f"fontfile='{font_path}'"
        else:
            font_str = ""

        # 如果文本包含中文字符，自动使用系统中文字体
        # 检测是否有非ASCII字符（中文、日文、韩文等）
        has_cjk = any(ord(c) > 0x4E00 and ord(c) < 0x9FFF for c in text)
        if has_cjk and not font_path:
            # FFmpeg 中 C: 的冒号需要转义为 \: 才能正确解析 Windows 路径
            font_str = r"fontfile='C\:/Windows/Fonts/simhei.ttf'"

# 通过临时文件传递文本内容，避免命令行编码问题
        # 注意: Python 的 subprocess 在 Windows 上不会 shell-escape 参数，
        # 需要手动对文本内容进行 FFmpeg filter 语法转义
        text_file = None
        try:
# 对文本进行 escape：换行、回车、冒号需要转义，单引号和反斜杠也要处理
            text_escaped = text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r").replace(":", "\\:")
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
                f.write(text)
                text_file = f.name

            # Windows 路径需要用正斜杠 / 代替反斜杠 \，避免转义问题
            text_file_posix = text_file.replace('\\', '/')
            filter_parts = [
                f"drawtext=text='{text_escaped}'",
                f"{pos_str}",
                f"fontsize={font_size}",
                f"fontcolor={color}",
                f"borderw=2",
                f"bordercolor=black@0.5"
            ]
            if font_str:
                filter_parts.append(font_str)

            filter_str = ":".join(filter_parts)

            cmd = [
                str(self.ffmpeg_path),
                "-i", video_file,
                "-vf", filter_str,
                "-c:a", "copy",
                "-y",
                output_file
            ]

            # 获取总时长用于进度计算
            total_duration = self.get_duration_seconds(video_file)

            success, stderr = self._run_with_progress(cmd, total_duration, progress_callback)
            if success:
                return True, f"文字水印添加成功: {output_file}"
            else:
                error = stderr[-500:] if stderr else "未知错误"
                return False, f"添加水印失败: {error}"
        except Exception as e:
            return False, f"添加水印异常: {str(e)}"
        finally:
            if text_file and os.path.exists(text_file):
                try:
                    os.remove(text_file)
                except Exception:
                    pass

    def extract_audio(self, video_file: str, output_file: str,
                      audio_format: str = "mp3",
                      progress_callback=None) -> tuple:
        """
        从视频中提取音频
        video_file: 输入视频文件路径
        output_file: 输出音频文件路径
        audio_format: 输出音频格式 (mp3/aac/wav/flac)
        progress_callback: 进度回调 (percent: int, current_sec: float)
        return: (成功与否, 消息)
        """
        # 检查输入文件是否存在
        if not os.path.exists(video_file):
            return False, f"输入文件不存在: {video_file}"

        # 检查视频是否有音轨
        info = self.get_media_info(video_file)
        has_audio = False
        audio_codec_name = ""
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'audio':
                has_audio = True
                audio_codec_name = stream.get('codec_name', '')
                break

        if not has_audio:
            return False, "视频文件中没有音轨，无法提取音频"

        # 根据格式选择编码器
        codec_map = {
            "mp3": "libmp3lame",
            "aac": "aac",
            "wav": "pcm_s16le",
            "flac": "flac",
        }
        codec = codec_map.get(audio_format.lower(), "libmp3lame")

        # 构建命令
        cmd = [
            str(self.ffmpeg_path),
            "-i", video_file,
            "-vn",  # 不处理视频
            "-c:a", codec,
            "-y",
            output_file
        ]

        total_duration = self.get_duration_seconds(video_file)

        try:
            success, stderr = self._run_with_progress(cmd, total_duration, progress_callback)
            if success:
                return True, f"音频提取成功: {output_file}"
            else:
                error = stderr[-500:] if stderr else "未知错误"
                return False, f"提取失败: {error}"
        except Exception as e:
            return False, f"提取异常: {str(e)}"

    def convert_format(self, input_file: str, output_file: str,
                       video_codec: str = "libx264",
                       audio_codec: str = "aac",
                       progress_callback=None) -> tuple:
        """
        转换视频格式
        input_file: 输入文件路径
        output_file: 输出文件路径
        video_codec: 视频编码器
        audio_codec: 音频编码器
        progress_callback: 进度回调 (percent: int, current_sec: float)
        return: (成功与否, 消息)
        """
        cmd = [
            str(self.ffmpeg_path),
            "-i", input_file,
            "-c:v", video_codec,
            "-c:a", audio_codec,
            "-y",
            output_file
        ]

        total_duration = self.get_duration_seconds(input_file)

        try:
            success, stderr = self._run_with_progress(cmd, total_duration, progress_callback)
            if success:
                return True, f"格式转换成功: {output_file}"
            else:
                error = stderr[-500:] if stderr else "未知错误"
                return False, f"转换失败: {error}"
        except Exception as e:
            return False, f"转换异常: {str(e)}"


# 便捷函数
_utils = None

def get_utils() -> FFmpegUtils:
    global _utils
    if _utils is None:
        _utils = FFmpegUtils()
    return _utils
