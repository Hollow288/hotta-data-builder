import os

from PIL import Image, ImageOps
from pathlib import Path
from typing import Optional
import tempfile

def _get_size_kb(path: Path) -> float:
    return path.stat().st_size / 1024.0


def _safe_open_image(path: Path) -> Optional[Image.Image]:
    try:
        img = Image.open(path)
        # 处理方向信息（EXIF），避免压缩后方向错误
        img = ImageOps.exif_transpose(img)
        return img
    except Exception as e:
        print(f"无法打开图片 {path}: {e}")
        return None


def _compress_jpeg_to_target(img: Image.Image, target_kb: int, min_q: int = 20, max_q: int = 95) -> Optional[bytes]:
    """
    使用二分法在 JPEG 质量范围里找出最接近目标大小的图片二进制数据。
    返回 bytes（JPEG 内容），或 None（无法压缩到更小且质量不低于 min_q）。
    """
    from io import BytesIO

    # 先测试 max_q
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=max_q, optimize=True)
    if buf.getbuffer().nbytes / 1024 <= target_kb:
        return buf.getvalue()

    low, high = min_q, max_q
    best = buf.getvalue()
    best_size = len(best)

    # binary search for quality
    while low <= high:
        mid = (low + high) // 2
        buf = BytesIO()
        try:
            img.save(buf, format="JPEG", quality=mid, optimize=True)
        except OSError:
            # Pillow may throw for some extreme combinations; fallback to save without optimize
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=mid)

        size_kb = buf.getbuffer().nbytes / 1024
        # print(f"试验 quality={mid} => {size_kb:.1f}KB")
        if size_kb <= target_kb:
            # 记录为候选（更接近目标的较高质量）
            best = buf.getvalue()
            best_size = len(best)
            # 尝试更高的质量以提高画质（在不超出 target 的前提下）
            low = mid + 1
        else:
            # 太大，降低质量
            high = mid - 1

    # 如果最终 best 仍然 > 原始大小，则还是返回 best（因为我们尽力了）
    return best if best_size > 0 else None


def _compress_png_to_target(img: Image.Image, target_kb: int) -> Optional[bytes]:
    """
    对 PNG 尝试几轮量化与 optimize，返回 bytes（PNG 内容）或 None。
    量化会降低色深（从 256 -> 128 -> 64 -> 32 -> 16）来减小体积。
    """
    from io import BytesIO

    # 先尝试直接 optimize 保存
    buf = BytesIO()
    try:
        img.save(buf, format="PNG", optimize=True)
        if buf.getbuffer().nbytes / 1024 <= target_kb:
            return buf.getvalue()
    except Exception:
        pass

    # 逐步量化
    for colors in (256, 128, 64, 32, 16, 8):
        buf = BytesIO()
        try:
            # 先转换为 P 模式（调色板），以减少文件大小
            img_quant = img.convert("P", palette=Image.ADAPTIVE, colors=colors)
            img_quant.save(buf, format="PNG", optimize=True)
            size_kb = buf.getbuffer().nbytes / 1024
            # print(f"PNG quant colors={colors} => {size_kb:.1f}KB")
            if size_kb <= target_kb:
                return buf.getvalue()
        except Exception:
            continue

    return None


def _compress_webp_to_target(img: Image.Image, target_kb: int, min_q: int = 20, max_q: int = 95) -> Optional[bytes]:
    from io import BytesIO

    buf = BytesIO()
    try:
        img.save(buf, format="WEBP", quality=max_q, method=6)
        if buf.getbuffer().nbytes / 1024 <= target_kb:
            return buf.getvalue()
    except Exception:
        pass

    low, high = min_q, max_q
    best = None
    best_size = 10**9
    while low <= high:
        mid = (low + high) // 2
        buf = BytesIO()
        try:
            img.save(buf, format="WEBP", quality=mid, method=6)
        except Exception:
            low = mid + 1
            continue
        size_kb = buf.getbuffer().nbytes / 1024
        if size_kb <= target_kb:
            # 记录较高质量解
            if len(buf.getvalue()) < best_size:
                best = buf.getvalue()
                best_size = len(best)
            low = mid + 1
        else:
            high = mid - 1

    return best


def compress_image_to_tempfile(src_path: Path, target_kb: int = 30) -> Optional[Path]:
    """
    尝试将 src_path 压缩到接近 target_kb（KB），并把压缩后的内容写入临时文件返回该临时文件路径。
    如果压缩失败或不适合压缩（如不是图片），返回 None。
    注意：调用者在上传后需要删除返回的临时文件。
    """
    if not src_path.exists() or not src_path.is_file():
        return None

    suffix = src_path.suffix.lower()
    img = _safe_open_image(src_path)
    if img is None:
        return None

    orig_kb = _get_size_kb(src_path)
    # 如果已经更小，直接不再压缩（节省 CPU）
    if orig_kb <= target_kb:
        return None  # 表示不需要压缩

    compressed_bytes: Optional[bytes] = None

    try:
        if suffix in (".jpg", ".jpeg"):
            compressed_bytes = _compress_jpeg_to_target(img, target_kb)
        elif suffix == ".png":
            compressed_bytes = _compress_png_to_target(img, target_kb)
        elif suffix == ".webp":
            compressed_bytes = _compress_webp_to_target(img, target_kb)
        else:
            # 其它格式：尝试先以 JPEG 保存（若原文件有透明通道则跳过）
            if img.mode in ("RGBA", "LA") or (hasattr(img, "info") and img.info.get("transparency")):
                # 不安全地转换会导致透明被填充，改为不压缩
                compressed_bytes = None
            else:
                compressed_bytes = _compress_jpeg_to_target(img, target_kb)
    except Exception as e:
        print(f"压缩时出错（{src_path}）：{e}")
        compressed_bytes = None

    if not compressed_bytes:
        return None

    # 写入临时文件，保持后缀
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    tmp_path = Path(tmp_path)
    try:
        # 二进制写入
        tmp_path.write_bytes(compressed_bytes)
        new_kb = _get_size_kb(tmp_path)
        print(f"Compressed {src_path} {orig_kb:.1f}KB -> {new_kb:.1f}KB (target {target_kb}KB)")
        return tmp_path
    except Exception as e:
        print(f"写入临时文件失败：{e}")
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass
        return None
