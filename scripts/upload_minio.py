import os

from utils.minio_client import minio_client




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


if __name__ == "__main__":
    # upload_folder_to_minio(r"E:\UnrealExporter\output\Hotta\Content\Resources\Icon", "hotta","Resources\Icon")
    # upload_folder_to_minio(r"E:\UnrealExporter\output\Hotta\Content\Resources\UI\shizhuang\Fashion_icon\item_fashion_icon", "hotta",r"Resources\UI\shizhuang\Fashion_icon\item_fashion_icon")
    upload_folder_to_minio(r"C:\XM\MY\Hotta\Content\Resources\UI\Artifact\itemicon", "hotta",r"Resources\UI\Artifact\itemicon")