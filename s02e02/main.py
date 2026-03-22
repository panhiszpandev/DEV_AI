import os
import sys
import json
import re

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
from shared.hub_client import verify, HUB_KEY
from modules.image_processor import ImageProcessor
from modules.vision_analyzer import VisionAnalyzer
from modules.grid_solver import GridSolver

CURRENT_IMG_URL = f"https://hub.ag3nts.org/data/{HUB_KEY}/electricity.png"
TARGET_IMG_URL = "https://hub.ag3nts.org/i/solved_electricity.png"
TASK = "electricity"


def extract_flag(result: dict):
    match = re.search(r"\{FLG:[^}]+\}", json.dumps(result))
    return match.group(0) if match else None


def main():
    processor = ImageProcessor()
    analyzer = VisionAnalyzer()
    solver = GridSolver()

    # 1. Download and crop both images
    print("=== Downloading images ===")
    current_img = processor.download_and_crop(CURRENT_IMG_URL)
    target_img = processor.download_and_crop(TARGET_IMG_URL, target=True)

    # 2. Split into 9 cells each
    current_cells = processor.split_into_cells(current_img)
    target_cells = processor.split_into_cells(target_img)

    # 3. Analyze all 18 tiles with vision model
    print("\n=== Analyzing current grid ===")
    current_grid = {}
    for cell_id in sorted(current_cells.keys()):
        current_grid[cell_id] = analyzer.analyze_tile(current_cells[cell_id])
        print(f"  {cell_id}: {sorted(current_grid[cell_id])}")

    print("\n=== Analyzing target grid ===")
    target_grid = {}
    for cell_id in sorted(target_cells.keys()):
        target_grid[cell_id] = analyzer.analyze_tile(target_cells[cell_id])
        print(f"  {cell_id}: {sorted(target_grid[cell_id])}")

    # 4. Execute rotations cell by cell
    print("\n=== Executing rotations ===")
    for cell_id in sorted(current_grid.keys()):
        n = solver.rotations_needed(current_grid[cell_id], target_grid[cell_id])
        print(f"  {cell_id}: {n} rotation(s)")

        for _ in range(n):
            result = verify(TASK, {"rotate": cell_id})
            current_grid[cell_id] = solver.rotate_cw(current_grid[cell_id])

            flag = extract_flag(result)
            if flag:
                print(f"\n=== FLAG: {flag} ===")
                return

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
