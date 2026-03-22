"""
文件上传API测试示例
"""
import requests

# API基础URL
BASE_URL = "http://localhost:8000"

def test_upload_single_file(file_path: str):
    """
    测试单文件上传
    
    Args:
        file_path: 要上传的文件路径
    """
    url = f"{BASE_URL}/api/upload/"
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.split('/')[-1], f, 'application/octet-stream')}
        response = requests.post(url, files=files)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.json()


def test_upload_multiple_files(file_paths: list):
    """
    测试批量文件上传
    
    Args:
        file_paths: 要上传的文件路径列表
    """
    url = f"{BASE_URL}/api/upload/multiple"
    
    files = []
    for file_path in file_paths:
        files.append(('files', (file_path.split('/')[-1], open(file_path, 'rb'), 'application/octet-stream')))
    
    response = requests.post(url, files=files)
    
    # 关闭文件
    for _, file_tuple in files:
        file_tuple[1].close()
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.json()


if __name__ == "__main__":
    # 测试单文件上传
    print("=== 测试单文件上传 ===")
    # test_upload_single_file("test.pdf")  # 替换为实际文件路径
    
    # 测试批量上传
    print("\n=== 测试批量文件上传 ===")
    # test_upload_multiple_files(["test1.pdf", "test2.docx"])  # 替换为实际文件路径






