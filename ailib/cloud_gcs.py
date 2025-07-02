import os
from google.cloud import storage
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account
import streamlit as st
import os

def init_storage_client():
    project_id = st.secrets["PROJECT_ID"]
    credentials = None
    sa_file_path = st.secrets["SA_KEY_FILE_PATH"]
    auth_type = st.secrets["AUTH_TYPE"]

    if auth_type == "SA" and os.path.exists(sa_file_path):
        credentials = service_account.Credentials.from_service_account_file(sa_file_path, scopes=['https://www.googleapis.com/auth/cloud-platform'])
    else:
        print(f"auth_type:{auth_type} is not SA or sa key file 路径 '{sa_file_path}' 不存在。 Auth by ADC")
    
    storage_client = storage.Client(
        project= project_id,
        credentials=credentials
    )
    return storage_client


def download_gcs_object(gcs_uri: str, local_destination_path: str = None) -> bool:
    """
    从 Google Cloud Storage 下载一个对象到本地文件系统。

    参数:
        gcs_uri (str): GCS 对象的完整 URI，格式为 "gs://bucket-name/path/to/object".
        local_destination_path (str, optional): 本地保存路径，包括文件名。
                                                如果为 None，将使用 GCS 对象的名称，并保存在当前工作目录。

    返回:
        bool: 如果下载成功则返回 True，否则返回 False。
    """
    if not gcs_uri.startswith("gs://"):
        print(f"错误：无效的 GCS URI '{gcs_uri}'。它必须以 'gs://' 开头。")
        return False

    try:
        # 初始化 GCS 客户端
        storage_client = init_storage_client()
        
        # 解析 GCS URI
        path_parts = gcs_uri[5:].split("/", 1)
        if len(path_parts) < 2 or not path_parts[0] or not path_parts[1]:
            print(f"错误：无效的 GCS URI 格式 '{gcs_uri}'。期望格式: gs://bucket-name/object-path")
            return False

        bucket_name = path_parts[0]
        blob_name = path_parts[1]

        # 如果 blob_name 以 '/' 结尾，说明它可能是一个“文件夹”占位符，或者用户错误地指定了
        # download_to_filename 不能下载这样的对象，它需要一个具体的文件名。
        if blob_name.endswith('/'):
            print(f"错误：对象路径 '{blob_name}' 看起来像一个目录。请指定一个具体的文件对象。")
            return False

        # 获取 bucket 和 blob
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # 确定本地目标路径
        if local_destination_path is None:
            local_destination_path = os.path.basename(blob_name)
            if not local_destination_path: # 防止 blob_name 是类似 "some/path/" 后又被错误处理到这里
                print(f"错误：无法从 GCS 路径 '{blob_name}' 推断出本地文件名。")
                return False
        else:
            # 确保目标目录存在
            local_dir = os.path.dirname(local_destination_path)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir)
                print(f"创建目录: {local_dir}")


        print(f"正在下载 gs://{bucket_name}/{blob_name} 到 {local_destination_path}...")

        blob.download_to_filename(local_destination_path)

        print(f"文件成功下载到: {local_destination_path}")
        return True

    except NotFound:
        print(f"错误：在 GCS 上未找到对象 gs://{bucket_name}/{blob_name} 或存储桶不存在。")
        return False
    except Exception as e:
        print(f"下载过程中发生错误: {e}")
        return False

def upload_gcs_object(bucket_name, destination_blob_name, source_file_name) -> bool:
    try:
        # 初始化 GCS 客户端
        storage_client = init_storage_client()

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Optional: set a generation-match precondition to avoid potential race conditions
        # and data corruptions. The request to upload is aborted if the object's
        # generation number does not match your precondition. For a destination
        # object that does not yet exist, set the if_generation_match precondition to 0.
        # If the destination object already exists in your bucket, set instead a
        # generation-match precondition using its generation number.
        generation_match_precondition = 0

        blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

        print(
            f"File {source_file_name} uploaded to {destination_blob_name}."
        )
        return True
    except Exception as e:
        print(f"上传过程中发生错误: {e}")
        return False

def blob_metadata(bucket_name, blob_name):
    print(bucket_name, blob_name)
    
    # 初始化 GCS 客户端
    storage_client = init_storage_client()
    
    bucket = storage_client.bucket(bucket_name)
    # Retrieve a blob, and its metadata, from Google Cloud Storage.
    # Note that `get_blob` differs from `Bucket.blob`, which does not
    # make an HTTP request.
    blob = bucket.get_blob(blob_name)
    return blob

# bucket_name = "gemini-oolongz"
# blob_name = "y"
# blob = blob_metadata(bucket_name, blob_name)
# print(blob)
# download_gcs_object("gs://gemini-oolongz/c", "c")
# upload_gcs_object("gemini-oolongz","c-copy", "c")