"""Command line interface for the AI-assisted video editing workflow."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Optional

from moviepy.editor import VideoFileClip

from .ai import ScriptSuggester
from .editor import change_speed, export_clip, load_clip, merge_audio, overlay_texts, stitch_clips, trim_clip


class VideoPipeline:
    def __init__(self, input_path: str, transcript: Optional[str] = None) -> None:
        self.input_path = input_path
        self.transcript = transcript or ""

    def build_clip(
        self,
        start: Optional[float] = None,
        end: Optional[float] = None,
        speed: float = 1.0,
        audio_path: Optional[str] = None,
        overlays: Optional[Iterable[str]] = None,
        ai_prompt: Optional[str] = None,
    ) -> VideoFileClip:
        clip = load_clip(self.input_path)
        clip = trim_clip(clip, start, end)
        if speed != 1.0:
            clip = change_speed(clip, speed)

        overlay_plans = []
        if ai_prompt:
            planner = ScriptSuggester()
            overlay_plans.extend(planner.plan_overlays(ai_prompt, clip.duration))
        if overlays:
            planner = ScriptSuggester()
            overlay_plans.extend(planner.plan_overlays(". ".join(overlays), clip.duration))

        if overlay_plans:
            clip = overlay_texts(clip, overlay_plans)

        clip = merge_audio(clip, audio_path)
        return clip


class CLI:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description="AI-assisted video editing toolkit")
        self._configure()

    def _configure(self) -> None:
        self.parser.add_argument("input", help="Ruta del video de entrada")
        self.parser.add_argument("output", help="Ruta del video final")
        self.parser.add_argument("--prompt", help="Texto que describe el video; se usa para generar overlays AI")
        self.parser.add_argument("--start", type=float, help="Segundo de inicio para recorte")
        self.parser.add_argument("--end", type=float, help="Segundo de fin para recorte")
        self.parser.add_argument("--speed", type=float, default=1.0, help="Factor de velocidad del clip")
        self.parser.add_argument("--audio", help="Pista de audio opcional para mezclar")
        self.parser.add_argument("--stitch", nargs="*", help="Lista de videos a unir antes de editar")
        self.parser.add_argument("--overlay", action="append", help="Textos a sobreponer manualmente")

    def parse(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        return self.parser.parse_args(args=args)

    def run(self, args: Optional[List[str]] = None) -> Path:
        options = self.parse(args)
        input_path = options.input

        if options.stitch:
            stitched = stitch_clips([input_path, *options.stitch])
            temp_path = Path("/tmp/stitched_clip.mp4")
            export_clip(stitched, temp_path.as_posix())
            input_path = temp_path.as_posix()

        pipeline = VideoPipeline(input_path)
        clip = pipeline.build_clip(
            start=options.start,
            end=options.end,
            speed=options.speed,
            audio_path=options.audio,
            overlays=options.overlay,
            ai_prompt=options.prompt,
        )
        export_clip(clip, options.output)
        return Path(options.output)


def main() -> None:
    CLI().run()


__all__ = ["main", "CLI", "VideoPipeline"]
