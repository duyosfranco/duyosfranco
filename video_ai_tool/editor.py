"""Video editing utilities built on top of MoviePy.

The module intentionally keeps the API small so it can be used from scripts or
from the command line entry-point in :mod:`video_ai_tool.cli`.
"""

from __future__ import annotations

from typing import Iterable, Optional, Tuple

from moviepy.editor import AudioFileClip, CompositeVideoClip, TextClip, VideoFileClip, concatenate_videoclips
from moviepy.video.fx import all as vfx

from .ai import OverlayPlan

Position = Tuple[str, str] | str


def load_clip(path: str) -> VideoFileClip:
    return VideoFileClip(path)


def trim_clip(clip: VideoFileClip, start: Optional[float], end: Optional[float]) -> VideoFileClip:
    return clip.subclip(start or 0, end)


def change_speed(clip: VideoFileClip, factor: float) -> VideoFileClip:
    return clip.fx(vfx.speedx, factor)


def overlay_text(
    clip: VideoFileClip,
    overlay: OverlayPlan,
    position: Position = ("center", "bottom"),
    font_size: int = 48,
    color: str = "white",
    stroke_color: str = "black",
    stroke_width: int = 2,
) -> VideoFileClip:
    pos: Position = position if overlay.position == "bottom" else ("center", "top")
    text = TextClip(overlay.text, fontsize=font_size, color=color, stroke_color=stroke_color, stroke_width=stroke_width)
    text = text.set_start(overlay.start).set_duration(overlay.duration).set_pos(pos)
    return CompositeVideoClip([clip, text])


def overlay_texts(
    clip: VideoFileClip,
    overlays: Iterable[OverlayPlan],
    font_size: int = 48,
    color: str = "white",
    stroke_color: str = "black",
    stroke_width: int = 2,
) -> VideoFileClip:
    composed = clip
    for overlay in overlays:
        composed = overlay_text(
            composed,
            overlay,
            font_size=font_size,
            color=color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
        )
    return composed


def merge_audio(clip: VideoFileClip, audio_path: Optional[str]) -> VideoFileClip:
    if not audio_path:
        return clip
    audio = AudioFileClip(audio_path)
    return clip.set_audio(audio)


def export_clip(clip: VideoFileClip, output_path: str, fps: int = 24, codec: str = "libx264", audio_codec: str = "aac") -> None:
    clip.write_videofile(output_path, fps=fps, codec=codec, audio_codec=audio_codec)


def stitch_clips(paths: Iterable[str]) -> VideoFileClip:
    clips = [load_clip(path) for path in paths]
    return concatenate_videoclips(clips)


__all__ = [
    "load_clip",
    "trim_clip",
    "change_speed",
    "overlay_text",
    "overlay_texts",
    "merge_audio",
    "export_clip",
    "stitch_clips",
]
