from pathlib import Path
from typing import Dict


def parse_label_map_txt(file_path: Path) -> Dict[str, int]:
    """
    解析标签映射 txt 文件，支持两种格式：
    1) 每行一个映射："0 person"、"1 car"
    2) 单行多映射："0 person 1 car 2 dog"
    忽略以#开头的注释与空行；后出现的条目会覆盖前面的同名标签。
    返回 label->id 的字典。
    """
    mapping: Dict[str, int] = {}
    text = Path(file_path).read_text(encoding="utf-8")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) == 2:
            try:
                idx = int(parts[0])
                label = parts[1]
                mapping[label] = idx
            except ValueError:
                continue
        elif len(parts) > 2 and len(parts) % 2 == 0:
            # 逐对解析
            for i in range(0, len(parts), 2):
                try:
                    idx = int(parts[i])
                    label = parts[i + 1]
                    mapping[label] = idx
                except ValueError:
                    continue
        else:
            # 不符合约定，忽略该行
            continue
    return mapping