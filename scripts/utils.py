"""
工具函数模块
用于融稿命令的通用功能
"""

import hashlib
import re
import os
from datetime import datetime
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_project_path(*paths):
    """
    获取相对于项目根目录的路径
    
    Args:
        *paths: 路径组件
    
    Returns:
        str: 完整路径
    """
    return os.path.join(PROJECT_ROOT, *paths)


def generate_task_id():
    """
    生成唯一的任务ID
    格式: 年月日-时分秒-随机MD5前6位
    例如: 20250911-143025-a3b5c7
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    # 使用当前时间戳生成MD5，取前6位
    random_str = str(datetime.now().timestamp()).encode()
    random_hash = hashlib.md5(random_str).hexdigest()[:6]
    return f"{timestamp}-{random_hash}"


def parse_note_ids(input_str):
    """
    解析用户输入的笔记ID列表或URL
    支持多种输入格式：
    - 带序号的列表：1. xxxxx 2. yyyyy
    - 逗号分隔：xxxxx,yyyyy
    - 换行分隔
    - URL格式：https://www.xiaohongshu.com/explore/xxxxx
    - 带token的URL：https://www.xiaohongshu.com/explore/xxxxx?xsec_token=xxx
    
    Args:
        input_str: 用户输入的字符串
    
    Returns:
        list: 笔记ID或URL列表（去重）
    """
    results = []
    
    # 首先尝试提取完整的URL（包含xsec_token的）
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?:\?[^\s<>"{}|\\^`\[\]]*)?'
    urls = re.findall(url_pattern, input_str)
    
    for url in urls:
        if 'xiaohongshu.com' in url or 'xhslink.com' in url:
            results.append(url)
    
    # 如果没有找到URL，尝试提取笔记ID
    if not results:
        # 使用正则表达式匹配24位十六进制字符串（小红书笔记ID格式）
        pattern = r'[0-9a-f]{24}'
        ids = re.findall(pattern, input_str.lower())
        results = list(set(ids))
    
    # 去重并返回
    return list(set(results))


def ensure_dir(path):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def is_note_complete(note_id):
    """
    检查笔记是否已完整处理
    通过检查content.md文件是否存在来判断
    
    Args:
        note_id: 笔记ID
    
    Returns:
        bool: True表示已处理，False表示未处理
    """
    content_path = Path(get_project_path("xhs_notes", note_id, "content.md"))
    return content_path.exists()


def has_metadata(note_id):
    """
    检查是否已有笔记元数据
    
    Args:
        note_id: 笔记ID
    
    Returns:
        bool: True表示存在元数据
    """
    metadata_path = Path(get_project_path("xhs_notes", note_id, "metadata.md"))
    return metadata_path.exists()


def has_ocr_results(note_id):
    """
    检查是否已有OCR识别结果
    
    Args:
        note_id: 笔记ID
    
    Returns:
        bool: True表示存在OCR结果
    """
    ocr_dir = Path(get_project_path("xhs_notes", note_id, "ocr_results"))
    if not ocr_dir.exists():
        return False
    
    # 检查是否有.md文件
    md_files = list(ocr_dir.glob("*.md"))
    return len(md_files) > 0


def read_content_md(note_id):
    """
    读取笔记的content.md文件
    
    Args:
        note_id: 笔记ID
    
    Returns:
        str: content.md的内容，如果不存在返回None
    """
    content_path = Path(get_project_path("xhs_notes", note_id, "content.md"))
    if content_path.exists():
        with open(content_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def format_note_ids_display(note_items):
    """
    格式化显示笔记ID或URL列表
    
    Args:
        note_items: 笔记ID或URL列表
    
    Returns:
        str: 格式化的字符串
    """
    if not note_items:
        return "无"
    
    formatted = []
    for i, item in enumerate(note_items, 1):
        if item.startswith('http'):
            # 从URL提取ID显示
            match = re.search(r'[0-9a-f]{24}', item.lower())
            if match:
                formatted.append(f"  {i}. {match.group()} (URL)")
            else:
                formatted.append(f"  {i}. {item[:50]}...")  # 截断显示
        else:
            formatted.append(f"  {i}. {item}")
    
    return "\n".join(formatted)


def create_error_log(task_id, error_msg):
    """
    创建错误日志
    
    Args:
        task_id: 任务ID
        error_msg: 错误信息
    """
    error_path = get_project_path("ronggao_output", task_id, "error.log")
    ensure_dir(get_project_path("ronggao_output", task_id))
    
    with open(error_path, 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {error_msg}\n")


if __name__ == "__main__":
    # 测试代码
    print("测试工具函数...")
    
    # 测试任务ID生成
    task_id = generate_task_id()
    print(f"生成的任务ID: {task_id}")
    
    # 测试笔记ID解析
    test_input = """
    1. 68a9a370000000001b037dc0
    2. 68a82fc1000000001d02ab79
    https://www.xiaohongshu.com/explore/68a82d32000000001d03619c
    """
    ids = parse_note_ids(test_input)
    print(f"解析的笔记ID: {ids}")
    print(f"格式化显示:\n{format_note_ids_display(ids)}")