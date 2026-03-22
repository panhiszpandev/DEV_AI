import io
import requests
from PIL import Image

CROP = (240, 98, 525, 387)
TARGET_OFFSET = (-100, -10)
TARGET_CROP = tuple(CROP[i] + TARGET_OFFSET[i % 2] for i in range(4))


class ImageProcessor:
    def download_and_crop(self, url: str, target: bool = False) -> Image.Image:
        resp = requests.get(url)
        img = Image.open(io.BytesIO(resp.content))
        return img.crop(TARGET_CROP if target else CROP)

    def split_into_cells(self, img: Image.Image) -> dict:
        """Returns dict mapping 'AxB' (row x col) → PIL Image."""
        w, h = img.size
        cw, ch = w // 3, h // 3
        cells = {}
        for row in range(1, 4):
            for col in range(1, 4):
                cell = img.crop(
                    ((col - 1) * cw, (row - 1) * ch, col * cw, row * ch)
                )
                cells[f"{row}x{col}"] = cell
        return cells
