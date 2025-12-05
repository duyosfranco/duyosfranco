"""Simple AI helpers used to generate overlays from prompts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence


@dataclass
class OverlayPlan:
    """Represents a single overlay instruction."""

    text: str
    start: float
    duration: float
    position: str = "bottom"


class ScriptSuggester:
    """Creates overlay plans from a prompt or transcript.

    The goal is to provide a deterministic and dependency-light stand-in for AI
    generated instructions. The heuristic splits text into sentences, keeps the
    most relevant ones, and maps them to timeline slots so they can be rendered
    later in :mod:`video_ai_tool.editor`.
    """

    def __init__(self, max_items: int = 6, min_duration: float = 2.5) -> None:
        self.max_items = max_items
        self.min_duration = min_duration

    def _split_sentences(self, text: str) -> List[str]:
        normalized = text.replace("?", ".").replace("!", ".")
        parts = [part.strip() for part in normalized.split(".")]
        return [part for part in parts if part]

    def _score_sentences(self, sentences: Sequence[str]) -> List[tuple[str, float]]:
        scores = []
        for sentence in sentences:
            uniqueness = len(set(sentence.lower().split()))
            emphasis = 1.2 if any(token in sentence.lower() for token in ["ai", "video", "edit"]) else 1.0
            score = uniqueness * emphasis
            scores.append((sentence, score))
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores

    def _evenly_spread(self, count: int, total_duration: float) -> Iterable[float]:
        if count == 0:
            return []
        slot = total_duration / count
        return (slot * idx for idx in range(count))

    def plan_overlays(self, prompt: str, total_duration: float) -> List[OverlayPlan]:
        sentences = self._split_sentences(prompt)
        scored = self._score_sentences(sentences)
        top_sentences = [sentence for sentence, _ in scored[: self.max_items]]

        start_times = list(self._evenly_spread(len(top_sentences), total_duration))
        overlays = []
        for idx, (sentence, start) in enumerate(zip(top_sentences, start_times)):
            overlays.append(
                OverlayPlan(
                    text=sentence,
                    start=start,
                    duration=max(self.min_duration, total_duration / (len(top_sentences) + 1)),
                    position="bottom" if idx % 2 == 0 else "top",
                )
            )
        return overlays


__all__ = ["OverlayPlan", "ScriptSuggester"]
