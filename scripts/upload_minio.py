import os
import mimetypes
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image  # 需要安装: pip install Pillow
from utils.minio_client import minio_client
# 假设这是你原本的压缩工具，如果用了 WebP，其实可以替代这个
from utils.image_utils import compress_image_to_tempfile

# 尝试导入进度条
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


def convert_to_webp_tempfile(local_path, lossless=True):  # <--- 默认改为 True
    """
    将图片转换为 WebP 格式
    :param lossless: True=无损(保留精度,适合UI/图标); False=有损(压缩率高,适合照片)
    """
    try:
        img = Image.open(local_path)

        # 保持透明通道 (RGBA)
        if img.mode in ("P", "L"):
            img = img.convert("RGBA")

        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".webp")
        os.close(tmp_fd)

        if lossless:
            # --- 方案 A: 无损模式 (推荐用于 UI/Icon) ---
            # quality=100 在无损模式下控制的是压缩花费的时间/算法力度，不影响画质，设为 100 获得最小体积
            img.save(tmp_path, "WEBP", lossless=True, quality=100)
        else:
            # --- 方案 B: 有损模式 (推荐用于大背景图/照片) ---
            # quality=75 是默认平衡点
            img.save(tmp_path, "WEBP", quality=75)

        return Path(tmp_path)
    except Exception as e:
        print(f"[WebP Error] {local_path}: {e}")
        return None


def upload_single_file(client, bucket_name, local_path, object_name,
                       compress=False, target_kb=30,
                       to_webp=False):  # <--- 新增参数 to_webp
    """
    处理单个文件上传
    :param to_webp: 是否转换为 WebP 格式
    """
    local_path = Path(local_path)
    tmp_path = None

    # 定义图片后缀列表
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tga'}

    try:
        # 1. 基础处理：路径标准化
        object_name = str(object_name).replace("\\", "/")
        final_path = local_path
        status_tag = "Original"

        # 2. 判断是否需要转 WebP
        # 条件：开启了开关 + 文件后缀是图片
        is_image = local_path.suffix.lower() in image_extensions

        if to_webp and is_image:
            converted_path = convert_to_webp_tempfile(local_path, lossless=True)
            if converted_path:
                tmp_path = converted_path
                final_path = tmp_path

                # --- 关键修改：更改 MinIO 上的对象名后缀 ---
                # 例如 Resources/Icon/sword.png -> Resources/Icon/sword.webp
                p_obj = Path(object_name)
                object_name = str(p_obj.with_suffix('.webp')).replace("\\", "/")

                status_tag = "WebP"

        # 3. 如果没转 WebP，但开启了旧的压缩逻辑 (互斥处理，避免压了又转)
        elif compress:
            # 这里沿用你之前的逻辑
            try:
                compressed_path = compress_image_to_tempfile(local_path, target_kb=target_kb)
                if compressed_path:
                    tmp_path = compressed_path
                    final_path = tmp_path
                    status_tag = "Compressed"
            except Exception as e:
                print(f"[Warning] Compress failed: {e}")

        # 4. 确定 Content-Type
        if status_tag == "WebP":
            # 如果转成了 WebP，类型固定
            content_type = "image/webp"
        else:
            # 否则根据后缀猜测
            content_type, _ = mimetypes.guess_type(local_path)
            if not content_type:
                content_type = "application/octet-stream"

        # 5. 执行上传
        client.fput_object(
            bucket_name,
            object_name,
            str(final_path),
            content_type=content_type
        )

        return True, f"[{status_tag}] {local_path.name} -> {content_type}"

    except Exception as e:
        return False, f"[Error] {local_path.name}: {e}"

    finally:
        # 清理临时文件
        if tmp_path and hasattr(tmp_path, 'exists') and tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass


def upload_folder_to_minio_concurrent(local_dir, bucket_name, prefix="",
                                      compress=False, target_kb=30,
                                      to_webp=False,  # <--- 接收配置
                                      max_workers=20):
    local_dir_p = Path(local_dir)
    if not local_dir_p.exists():
        print(f"Directory not found: {local_dir}")
        return

    # 1. Bucket 检查
    if not minio_client.bucket_exists(bucket_name):
        try:
            minio_client.make_bucket(bucket_name)
        except Exception as e:
            print(f"Failed to create bucket: {e}")
            return

    # 2. 扫描文件
    files = [f for f in local_dir_p.rglob('*') if f.is_file()]
    if not files:
        print("No files found.")
        return

    print(f"Found {len(files)} files. Uploading (WebP={to_webp})...")

    # 3. 线程池上传
    success_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {}
        for file_path in files:
            relative_path = file_path.relative_to(local_dir_p)
            object_name = Path(prefix) / relative_path

            future = executor.submit(
                upload_single_file,
                minio_client,
                bucket_name,
                file_path,
                object_name,
                compress,  # 旧压缩开关
                target_kb,
                to_webp  # 新 WebP 开关
            )
            future_to_file[future] = file_path

        iterator = as_completed(future_to_file)
        if tqdm:
            iterator = tqdm(iterator, total=len(files), unit="img", desc=f"Up to {prefix}")

        for future in iterator:
            success, msg = future.result()
            if success:
                success_count += 1
                # if not tqdm: print(msg) # 调试看日志
            else:
                fail_count += 1
                print(msg)

    print(f"\nCompleted: {prefix}. Success: {success_count}, Fail: {fail_count}\n")


if __name__ == "__main__":
    # 配置你的上传任务列表
    # (本地路径, Bucket名称, MinIO前缀/目标路径)
    tasks = [
        (r"E:/UnrealExporter/output/Hotta/Content/Resources/Icon", "hotta", "Resources/Icon"),
        (r"E:/UnrealExporter/output/Hotta/Content/Resources/UI/shizhuang/Fashion_icon/item_fashion_icon", "hotta",
         "Resources/UI/shizhuang/Fashion_icon/item_fashion_icon"),
        (r"E:/UnrealExporter/output/Hotta/Content/Resources/UI/Artifact/itemicon", "hotta",
         "Resources/UI/Artifact/itemicon"),
        (r"E:/UnrealExporter/output/Hotta/Content/Resources/UI/Artifact/icon", "hotta", "Resources/UI/Artifact/icon"),
    ]

    for local_path, bucket, remote_prefix in tasks:
        upload_folder_to_minio_concurrent(
            local_dir=local_path,
            bucket_name=bucket,
            prefix=remote_prefix,

            # --- 配置区域 ---
            compress=False,  # 旧的压缩逻辑（如果开启 WebP，建议关闭这个，因为 WebP 本身就是压缩）
            to_webp=True,  # <--- 开启 WebP 转换！
            # ----------------

            target_kb=30,
            max_workers=30
        )