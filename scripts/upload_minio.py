import os

from utils.image_utils import compress_image_to_tempfile
from utils.minio_client import minio_client
from pathlib import Path

def upload_folder_to_minio(local_dir, bucket_name, prefix=""):

    # 检查 bucket 是否存在，不存在则创建
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    else:
        print(f"Bucket '{bucket_name}' exists.")

    # 遍历文件夹并上传
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_file_path = os.path.join(root, file)
            # 保持相对路径结构
            relative_path = os.path.relpath(local_file_path, local_dir)
            object_name = os.path.join(prefix, relative_path).replace("\\", "/")  # Windows 兼容
            try:
                minio_client.fput_object(bucket_name, object_name, local_file_path)
                print(f"Uploaded: {local_file_path} -> {bucket_name}/{object_name}")
            except os.error as e:
                print(f"Error uploading {local_file_path}: {e}")

    print("Upload completed.")





def upload_folder_to_minio_compressed(local_dir: str, bucket_name: str, prefix: str = "", target_kb: int = 30):
    """
    遍历 local_dir 上传到 minio，上传前尝试压缩图片到 target_kb（KB）。
    路径结构与文件名保持不变（object name 使用传入的 prefix + 相对路径）。
    """
    local_dir_p = Path(local_dir)
    if not local_dir_p.exists() or not local_dir_p.is_dir():
        raise ValueError(f"{local_dir} 不是有效目录")

    # 检查 bucket 是否存在，不存在则创建
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    else:
        print(f"Bucket '{bucket_name}' exists.")

    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_file_path = Path(root) / file
            relative_path = local_file_path.relative_to(local_dir_p)
            object_name = Path(prefix) / relative_path
            # 统一把 object_name 路径分隔符换成 '/'
            object_name_str = str(object_name).replace("\\", "/")

            # 仅对图片尝试压缩
            tmp_path = None
            try:
                tmp_path = compress_image_to_tempfile(local_file_path, target_kb=target_kb)
                if tmp_path:
                    # 使用压缩后的临时文件上传，但 object_name 保持原名（后缀也保持）
                    minio_client.fput_object(bucket_name, object_name_str, str(tmp_path))
                    print(f"Uploaded (compressed): {local_file_path} -> {bucket_name}/{object_name_str}")
                else:
                    # tmp_path 为 None 表示不需要/无法压缩，直接上传原文件
                    minio_client.fput_object(bucket_name, object_name_str, str(local_file_path))
                    print(f"Uploaded (original): {local_file_path} -> {bucket_name}/{object_name_str}")
            except Exception as e:
                print(f"Error uploading {local_file_path}: {e}")
            finally:
                # 清理由 compress 产生的临时文件
                if tmp_path and tmp_path.exists():
                    try:
                        tmp_path.unlink()
                    except Exception:
                        pass

    print("Upload completed.")


if __name__ == "__main__":
    # upload_folder_to_minio(r"E:\UnrealExporter\output\Hotta\Content\Resources\Icon", "hotta","Resources\Icon")
    # upload_folder_to_minio(r"E:\UnrealExporter\output\Hotta\Content\Resources\UI\shizhuang\Fashion_icon\item_fashion_icon", "hotta",r"Resources\UI\shizhuang\Fashion_icon\item_fashion_icon")
    # upload_folder_to_minio(r"C:\XM\MY\Hotta\Content\Resources\UI\Artifact\itemicon", "hotta",r"Resources\UI\Artifact\itemicon")
    upload_folder_to_minio(r"C:\XM\MY\Hotta\Content\Resources\UI\Artifact\icon", "hotta",r"Resources\UI\Artifact\icon")
    # upload_folder_to_minio_compressed(
    #     r"C:\XM\MY\Hotta\Content\Resources\UI\Artifact\itemicon",
    #     "hotta",
    #     r"Resources\UI\Artifact\icon",
    #     target_kb=10,
    # )