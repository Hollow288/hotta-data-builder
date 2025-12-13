import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.image_utils import compress_image_to_tempfile
from utils.minio_client import minio_client

# 尝试导入进度条库，如果没有安装则使用简单的打印
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


def upload_single_file(client, bucket_name, local_path, object_name, compress=False, target_kb=30):
    """
    处理单个文件的上传逻辑（包含可选的压缩逻辑）
    """
    local_path = Path(local_path)
    tmp_path = None

    try:
        # 统一路径分隔符为 / (MinIO/S3 标准)
        object_name = str(object_name).replace("\\", "/")

        final_path = local_path
        is_compressed = False

        # 如果开启压缩
        if compress:
            try:
                # 假设 compress_image_to_tempfile 返回 Path 对象或 None
                tmp_path = compress_image_to_tempfile(local_path, target_kb=target_kb)
                if tmp_path:
                    final_path = tmp_path
                    is_compressed = True
            except Exception as e:
                print(f"[Warning] Compression failed for {local_path.name}, uploading original. Error: {e}")

        # 执行上传
        client.fput_object(bucket_name, object_name, str(final_path))

        # 返回结果信息用于统计或日志
        status = "Compressed" if is_compressed else "Original"
        return True, f"[{status}] {local_path.name}"

    except Exception as e:
        return False, f"[Error] {local_path.name}: {e}"

    finally:
        # 清理压缩产生的临时文件
        if tmp_path and hasattr(tmp_path, 'exists') and tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass


def upload_folder_to_minio_concurrent(local_dir, bucket_name, prefix="", compress=False, target_kb=30, max_workers=20):
    """
    多线程并发上传文件夹到 MinIO
    :param max_workers: 并发线程数，建议设置为 10-50 之间
    """
    local_dir_p = Path(local_dir)
    if not local_dir_p.exists():
        print(f"Directory not found: {local_dir}")
        return

    # 1. 检查/创建 Bucket
    if not minio_client.bucket_exists(bucket_name):
        try:
            minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created.")
        except Exception as e:
            print(f"Failed to create bucket: {e}")
            return

    # 2. 扫描所有文件，准备任务列表
    print(f"Scanning files in {local_dir}...")
    tasks = []

    # 使用 rglob 遍历（相当于 os.walk）
    # 如果只传图片，可以在这里加后缀判断，例如 if file.suffix.lower() in ['.png', '.jpg']
    files = [f for f in local_dir_p.rglob('*') if f.is_file()]

    if not files:
        print("No files found.")
        return

    print(f"Found {len(files)} files. Starting upload with {max_workers} threads...")

    # 3. 使用线程池并发上传
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {}

        for file_path in files:
            # 计算相对路径并生成 Object Name
            relative_path = file_path.relative_to(local_dir_p)
            object_name = Path(prefix) / relative_path

            # 提交任务
            future = executor.submit(
                upload_single_file,
                minio_client,
                bucket_name,
                file_path,
                object_name,
                compress,
                target_kb
            )
            future_to_file[future] = file_path

        # 4. 处理结果 (带进度条)
        success_count = 0
        fail_count = 0

        # 如果有 tqdm 则显示进度条，否则使用普通迭代
        iterator = as_completed(future_to_file)
        if tqdm:
            iterator = tqdm(iterator, total=len(files), unit="file", desc=f"Uploading {prefix}")

        for future in iterator:
            success, message = future.result()
            if success:
                success_count += 1
                # 如果不想看详细日志，可以注释掉下面这行，或者只在出错时打印
                # if not tqdm: print(message)
            else:
                fail_count += 1
                print(message)  # 出错始终打印

    print(f"\nUpload Completed for {prefix}.")
    print(f"Success: {success_count}, Failed: {fail_count}\n")


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

    # 循环执行任务
    for local_path, bucket, remote_prefix in tasks:
        upload_folder_to_minio_concurrent(
            local_dir=local_path,
            bucket_name=bucket,
            prefix=remote_prefix,
            compress=False,  # 如果需要压缩，设为 True
            target_kb=30,  # 压缩目标大小
            max_workers=30  # 线程数，根据网络情况调整
        )