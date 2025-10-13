from pathlib import Path
from typing import List, Optional


def list_files_by_ext(root: Path, exts: List[str]) -> List[Path]:
    result: List[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in {e.lower() for e in exts}:
            result.append(p)
    return sorted(result)


def ensure_dir(path: Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def find_image_by_stem(root_dir: Path, stem: str) -> Optional[Path]:
    exts = [".jpg", ".jpeg", ".png", ".bmp"]
    for ext in exts:
        p = Path(root_dir) / f"{stem}{ext}"
        if p.exists():
            return p
    return None