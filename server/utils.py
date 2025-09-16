import json
import os
import re
from filelock import FileLock

def load_json(file_path):
    """Load a JSON file and return its content as a dictionary."""
    lock = FileLock(file_path + ".lock")
    with lock:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

def save_json(file_path, data):
    """Safely save a dictionary to a JSON file with atomic write."""
    lock = FileLock(file_path + ".lock")
    tmp_path = file_path + ".tmp"

    with lock:
        # 写到临时文件
        with open(tmp_path, 'w', encoding='utf-8') as tmp_file:
            json.dump(data, tmp_file, indent=4, ensure_ascii=False)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())

        # 原子替换
        os.replace(tmp_path, file_path)

def safe_video_id(video_id):
    """验证video_id格式，防止路径遍历攻击"""
    if not re.match(r'^[a-zA-Z0-9_-]+$', video_id):
        return False
    return video_id
