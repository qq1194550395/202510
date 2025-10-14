from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import random
import math

from PIL import Image, ImageEnhance


@dataclass
class AugmentOptions:
    hflip: bool = False
    vflip: bool = False
    rotate_deg: int = 0
    crop_ratio: float = 1.0
    scale_ratio: float = 1.0
    jitter: bool = False
    brightness: float = 1.0
    contrast: float = 1.0
    saturation: float = 1.0
    mosaic: bool = False
    mixup: bool = False
    mixup_alpha: float = 0.5


def _read_yolo_labels(txt_path: Path) -> List[Tuple[int, float, float, float, float]]:
    entries: List[Tuple[int, float, float, float, float]] = []
    if not txt_path.exists():
        return entries
    for line in txt_path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        try:
            cls = int(parts[0])
            xc, yc, w, h = map(float, parts[1:])
            entries.append((cls, xc, yc, w, h))
        except Exception:
            continue
    return entries


def _write_yolo_labels(txt_path: Path, labels: List[Tuple[int, float, float, float, float]]):
    lines = []
    for cls, xc, yc, w, h in labels:
        # clip to [0,1]
        xc = min(max(xc, 0.0), 1.0)
        yc = min(max(yc, 0.0), 1.0)
        w = min(max(w, 0.0), 1.0)
        h = min(max(h, 0.0), 1.0)
        lines.append(f"{cls} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}")
    txt_path.write_text("\n".join(lines), encoding="utf-8")


def _yolo_to_xyxy(labels: List[Tuple[int, float, float, float, float]], w: int, h: int) -> List[Tuple[int, float, float, float, float]]:
    res = []
    for cls, xc, yc, bw, bh in labels:
        cx = xc * w
        cy = yc * h
        ww = bw * w
        hh = bh * h
        xmin = cx - ww / 2
        ymin = cy - hh / 2
        xmax = cx + ww / 2
        ymax = cy + hh / 2
        res.append((cls, xmin, ymin, xmax, ymax))
    return res


def _xyxy_to_yolo(labels: List[Tuple[int, float, float, float, float]], w: int, h: int) -> List[Tuple[int, float, float, float, float]]:
    res = []
    for cls, xmin, ymin, xmax, ymax in labels:
        xmin = max(0.0, min(xmin, w))
        ymin = max(0.0, min(ymin, h))
        xmax = max(0.0, min(xmax, w))
        ymax = max(0.0, min(ymax, h))
        bw = max(0.0, xmax - xmin)
        bh = max(0.0, ymax - ymin)
        cx = xmin + bw / 2
        cy = ymin + bh / 2
        res.append((cls, cx / w, cy / h, bw / w, bh / h))
    return res


def _clip_box(xmin: float, ymin: float, xmax: float, ymax: float, w: int, h: int) -> Tuple[float, float, float, float]:
    xmin = max(0.0, min(xmin, w))
    ymin = max(0.0, min(ymin, h))
    xmax = max(0.0, min(xmax, w))
    ymax = max(0.0, min(ymax, h))
    return xmin, ymin, xmax, ymax


def _apply_hflip(boxes: List[Tuple[int, float, float, float, float]], w: int) -> List[Tuple[int, float, float, float, float]]:
    res = []
    for cls, xmin, ymin, xmax, ymax in boxes:
        nxmin = w - xmax
        nxmax = w - xmin
        res.append((cls, nxmin, ymin, nxmax, ymax))
    return res


def _apply_vflip(boxes: List[Tuple[int, float, float, float, float]], h: int) -> List[Tuple[int, float, float, float, float]]:
    res = []
    for cls, xmin, ymin, xmax, ymax in boxes:
        nymin = h - ymax
        nymax = h - ymin
        res.append((cls, xmin, nymin, xmax, nymax))
    return res


def _rotate_point(x: float, y: float, cx: float, cy: float, rad: float) -> Tuple[float, float]:
    cosr = math.cos(rad)
    sinr = math.sin(rad)
    dx = x - cx
    dy = y - cy
    rx = cx + dx * cosr - dy * sinr
    ry = cy + dx * sinr + dy * cosr
    return rx, ry


def _apply_rotation(boxes: List[Tuple[int, float, float, float, float]], w: int, h: int, deg: int) -> List[Tuple[int, float, float, float, float]]:
    if deg % 360 == 0:
        return boxes
    rad = math.radians(deg)
    cx, cy = w / 2, h / 2
    res = []
    for cls, xmin, ymin, xmax, ymax in boxes:
        pts = [
            (xmin, ymin),
            (xmax, ymin),
            (xmax, ymax),
            (xmin, ymax),
        ]
        rpts = [_rotate_point(x, y, cx, cy, rad) for x, y in pts]
        xs = [p[0] for p in rpts]
        ys = [p[1] for p in rpts]
        nxmin, nxmax = min(xs), max(xs)
        nymin, nymax = min(ys), max(ys)
        nxmin, nymin, nxmax, nymax = _clip_box(nxmin, nymin, nxmax, nymax, w, h)
        res.append((cls, nxmin, nymin, nxmax, nymax))
    return res


def _apply_crop(boxes: List[Tuple[int, float, float, float, float]], w: int, h: int, ratio: float) -> Tuple[List[Tuple[int, float, float, float, float]], int, int, int, int]:
    if ratio >= 0.999:
        return boxes, 0, 0, w, h
    nw = int(w * ratio)
    nh = int(h * ratio)
    ox = random.randint(0, max(0, w - nw))
    oy = random.randint(0, max(0, h - nh))
    res = []
    for cls, xmin, ymin, xmax, ymax in boxes:
        nxmin = xmin - ox
        nymin = ymin - oy
        nxmax = xmax - ox
        nymax = ymax - oy
        nxmin, nymin, nxmax, nymax = _clip_box(nxmin, nymin, nxmax, nymax, nw, nh)
        if (nxmax - nxmin) > 1 and (nymax - nymin) > 1:
            res.append((cls, nxmin, nymin, nxmax, nymax))
    return res, ox, oy, nw, nh


def _apply_scale(boxes: List[Tuple[int, float, float, float, float]], scale: float) -> List[Tuple[int, float, float, float, float]]:
    if abs(scale - 1.0) < 1e-3:
        return boxes
    res = []
    for cls, xmin, ymin, xmax, ymax in boxes:
        res.append((cls, xmin * scale, ymin * scale, xmax * scale, ymax * scale))
    return res


def _apply_jitter(img: Image.Image, brightness: float, contrast: float, saturation: float) -> Image.Image:
    if abs(brightness - 1.0) > 1e-3:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if abs(contrast - 1.0) > 1e-3:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if abs(saturation - 1.0) > 1e-3:
        img = ImageEnhance.Color(img).enhance(saturation)
    return img


def _process_single(img_path: Path, out_dir: Path, opt: AugmentOptions):
    img = Image.open(img_path).convert("RGB")
    w, h = img.size

    # 解析 YOLO 标注（同名 .txt），若不存在则为空
    labels = _read_yolo_labels(img_path.with_suffix(".txt"))
    boxes_xyxy = _yolo_to_xyxy(labels, w, h)

    # 基础几何变换
    if opt.hflip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        boxes_xyxy = _apply_hflip(boxes_xyxy, w)
    if opt.vflip:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        boxes_xyxy = _apply_vflip(boxes_xyxy, h)

    if opt.rotate_deg:
        img = img.rotate(opt.rotate_deg, expand=False)
        boxes_xyxy = _apply_rotation(boxes_xyxy, w, h, opt.rotate_deg)

    # 随机裁剪
    boxes_crop, ox, oy, nw, nh = _apply_crop(boxes_xyxy, w, h, opt.crop_ratio)
    if (nw, nh) != (w, h):
        img = img.crop((ox, oy, ox + nw, oy + nh))
        w, h = nw, nh
        boxes_xyxy = boxes_crop

    # 缩放
    if abs(opt.scale_ratio - 1.0) > 1e-3:
        sw = int(w * opt.scale_ratio)
        sh = int(h * opt.scale_ratio)
        img = img.resize((sw, sh))
        boxes_xyxy = _apply_scale(boxes_xyxy, opt.scale_ratio)
        w, h = sw, sh

    # 色彩抖动
    if opt.jitter:
        img = _apply_jitter(img, opt.brightness, opt.contrast, opt.saturation)

    # 写出
    stem = img_path.stem
    out_img = out_dir / f"{stem}_aug.jpg"
    out_lab = out_dir / f"{stem}_aug.txt"
    out_dir.mkdir(parents=True, exist_ok=True)
    img.save(out_img, quality=95)
    out_labels = _xyxy_to_yolo(boxes_xyxy, w, h)
    _write_yolo_labels(out_lab, out_labels)


def _mosaic_four(imgs: List[Image.Image]) -> Image.Image:
    # 将四张图缩放到同等大小后拼接
    sizes = [im.size for im in imgs]
    minw = min(s[0] for s in sizes)
    minh = min(s[1] for s in sizes)
    resized = [im.resize((minw, minh)) for im in imgs]
    canvas = Image.new("RGB", (minw * 2, minh * 2))
    canvas.paste(resized[0], (0, 0))
    canvas.paste(resized[1], (minw, 0))
    canvas.paste(resized[2], (0, minh))
    canvas.paste(resized[3], (minw, minh))
    return canvas


def _mosaic_boxes(img_paths: List[Path]) -> Tuple[List[Tuple[int, float, float, float, float]], int, int]:
    # 合并四图的标注，缩放到统一最小尺寸，并按象限偏移
    imgs = [Image.open(p).convert("RGB") for p in img_paths]
    sizes = [im.size for im in imgs]
    minw = min(s[0] for s in sizes)
    minh = min(s[1] for s in sizes)
    all_boxes: List[Tuple[int, float, float, float, float]] = []
    for idx, (p, im) in enumerate(zip(img_paths, imgs)):
        w, h = im.size
        scale_w = minw / w
        scale_h = minh / h
        # 用同一比例缩放，保持长宽比，取较小者
        scale = min(scale_w, scale_h)
        # YOLO 标注
        yolo = _read_yolo_labels(p.with_suffix(".txt"))
        boxes = _yolo_to_xyxy(yolo, w, h)
        boxes = _apply_scale(boxes, scale)
        # 偏移
        offx = (idx % 2) * minw
        offy = (idx // 2) * minh
        for cls, xmin, ymin, xmax, ymax in boxes:
            all_boxes.append((cls, xmin + offx, ymin + offy, xmax + offx, ymax + offy))
    return all_boxes, minw * 2, minh * 2


def augment_dataset(input_dir: Path, output_dir: Path, opt: AugmentOptions) -> None:
    """对目录内图像执行增强，当前主要支持 YOLO 格式（同名 .txt）。
    - Mosaic：从目录随机抽取四张图拼接。
    - MixUp：随机抽取两张同尺寸图进行透明度融合。
    其它变换对每张图独立应用。
    """
    imgs = sorted([p for p in Path(input_dir).rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}])
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 逐图增强
    for p in imgs:
        _process_single(p, output_dir, opt)

    # Mosaic（生成若干拼图，数量取样与输入图像相同的 1/4）
    if opt.mosaic and len(imgs) >= 4:
        count = max(1, len(imgs) // 4)
        for i in range(count):
            picks = random.sample(imgs, 4)
            canvas = _mosaic_four([Image.open(pp).convert("RGB") for pp in picks])
            boxes, w, h = _mosaic_boxes(picks)
            out_img = output_dir / f"mosaic_{i:03d}.jpg"
            out_lab = output_dir / f"mosaic_{i:03d}.txt"
            canvas.save(out_img, quality=95)
            _write_yolo_labels(out_lab, _xyxy_to_yolo(boxes, w, h))

    # MixUp（生成若干融合图，数量取样与输入图像相同的 1/5）
    if opt.mixup and len(imgs) >= 2:
        count = max(1, len(imgs) // 5)
        for i in range(count):
            p1, p2 = random.sample(imgs, 2)
            im1 = Image.open(p1).convert("RGB")
            im2 = Image.open(p2).convert("RGB")
            # 缩放到相同尺寸
            w = min(im1.size[0], im2.size[0])
            h = min(im1.size[1], im2.size[1])
            im1 = im1.resize((w, h))
            im2 = im2.resize((w, h))
            mix = Image.blend(im1, im2, opt.mixup_alpha)
            # 合并标注（缩放到同尺寸）
            boxes1 = _apply_scale(_yolo_to_xyxy(_read_yolo_labels(p1.with_suffix(".txt")), *im1.size), 1.0)
            boxes2 = _apply_scale(_yolo_to_xyxy(_read_yolo_labels(p2.with_suffix(".txt")), *im2.size), 1.0)
            boxes = boxes1 + boxes2
            out_img = output_dir / f"mixup_{i:03d}.jpg"
            out_lab = output_dir / f"mixup_{i:03d}.txt"
            mix.save(out_img, quality=95)
            _write_yolo_labels(out_lab, _xyxy_to_yolo(boxes, w, h))