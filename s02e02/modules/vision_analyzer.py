import io
import base64
from collections import Counter
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps
from shared.ai_client import ask_vision

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

VOTE_PROMPTS = [
    "Describe the cable exits in clock notation.",
    "Look only at the black lines. Which edges (top/right/bottom/left) does the black cable touch? Reply in clock notation.",
    "Trace the black cable from the center. Which edges does it reach? Use clock notation (12=top, 3=right, 6=bottom, 9=left).",
    "Ignore the background. Only the black cable matters. List which edges it exits through in clock notation.",
    "Which of the four edges (12, 3, 6, 9) has a black cable crossing it? Reply with clock notation only.",
]


class VisionAnalyzer:
    def __init__(self, votes: int = 5):
        self._system_prompt = (PROMPTS_DIR / "system.md").read_text()
        self._votes = votes

    def analyze_tile(self, img: Image.Image) -> frozenset:
        b64 = self._to_base64(img)
        results = []
        for prompt in VOTE_PROMPTS[:self._votes]:
            raw = ask_vision(self._system_prompt, b64, prompt, model="google/gemini-2.0-flash-001")
            try:
                results.append(self._parse(raw))
            except Exception:
                pass
        return Counter(results).most_common(1)[0][0]

    def _to_base64(self, img: Image.Image) -> str:
        w, h = img.size
        img = img.crop((5, 5, w - 5, h - 5))
        img = ImageOps.grayscale(img)
        img = img.point(lambda p: 0 if p < 128 else 255, "L")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    def _parse(self, response: str) -> frozenset:
        last_line = [l.strip() for l in response.strip().splitlines() if l.strip()][-1]
        return frozenset(int(x) for x in last_line.split("+"))
