import io
import base64
from pathlib import Path
from PIL import Image
from shared.ai_client import ask_vision

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class VisionAnalyzer:
    def __init__(self):
        self._system_prompt = (PROMPTS_DIR / "system.md").read_text()

    def analyze_tile(self, img: Image.Image) -> frozenset:
        b64 = self._to_base64(img)
        raw = ask_vision(self._system_prompt, b64, "Describe the cable exits in clock notation.")
        return self._parse(raw)

    def _to_base64(self, img: Image.Image) -> str:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    def _parse(self, clock_str: str) -> frozenset:
        return frozenset(int(x) for x in clock_str.strip().split("+"))
