import os
def create_dir(path: str):
    """
    若不存在传入的path，就创建目录
    """
    if not os.path.exists(path):
        os.makedirs(path)