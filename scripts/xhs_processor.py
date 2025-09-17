"""
小红书笔记处理主脚本
集成XHS-Downloader API和PaddleOCR
"""

import sys
import json
import requests
import time
import os
from pathlib import Path
from datetime import datetime

# 导入工具函数
from utils import (
    generate_task_id,
    parse_note_ids,
    ensure_dir,
    is_note_complete,
    has_metadata,
    has_ocr_results,
    read_content_md,
    format_note_ids_display,
    create_error_log,
    get_project_path
)

# 配置
XHS_API_URL = "http://127.0.0.1:5556/xhs/detail"
XHS_API_TIMEOUT = 60  # API超时时间（秒）

# OCR配置 - 延迟导入，避免未安装时报错
ocr = None


def init_ocr():
    """初始化OCR引擎"""
    global ocr
    if ocr is None:
        try:
            from paddleocr import PaddleOCR
            import paddle
            
            # 检查GPU是否可用
            use_gpu = paddle.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0
            device = 'gpu:0' if use_gpu else 'cpu'
            
            print(f"正在初始化OCR引擎 (PP-OCRv5, 设备: {device})...")
            
            # 使用PP-OCRv4 Mobile轻量级模型，速度更快
            ocr = PaddleOCR(
                ocr_version='PP-OCRv5',  # 使用v5版本
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang='ch',
                device=device  # 指定设备
            )
            print(f"OCR引擎初始化完成 (PP-OCRv5, {'GPU加速' if use_gpu else 'CPU模式'})")
        except ImportError:
            print("警告：PaddleOCR未安装，OCR功能将不可用")
            print("请运行: pip install paddlepaddle paddleocr")
            return False
    return True


def check_xhs_api_status():
    """
    检查XHS-Downloader API服务是否运行
    
    Returns:
        bool: True表示服务正常，False表示服务不可用
    """
    try:
        # 尝试访问API文档页面
        response = requests.get("http://127.0.0.1:5556/docs", timeout=5)
        if response.status_code == 200:
            print("✓ XHS-Downloader API服务正常")
            return True
    except:
        pass
    
    print("✗ XHS-Downloader API服务未运行")
    print("请先启动Docker服务：")
    print("  docker run --name xhs-api -d -p 5556:5556 \\")
    print("    -v xhs_downloader_volume:/app/Volume \\")
    print("    joeanamier/xhs-downloader python main.py api")
    return False


def download_note_via_api(note_id_or_url):
    """
    通过XHS-Downloader API获取笔记数据
    
    Args:
        note_id_or_url: 笔记ID或完整URL（必须包含xsec_token参数）
    
    Returns:
        dict: API返回的数据，失败返回None
    """
    print(f"  → 调用API获取笔记数据...")
    
    # 判断是ID还是URL
    if note_id_or_url.startswith('http'):
        url = note_id_or_url
        # 检查URL是否包含必需的token参数
        if 'xsec_token=' not in url:
            print(f"  ⚠️  警告: URL缺少xsec_token参数，可能无法正确获取数据")
            print(f"     正确格式示例: https://www.xiaohongshu.com/explore/xxxxx?xsec_token=xxxxx")
    else:
        # 如果只是ID，构建基础URL（注意：可能无法正常工作）
        print(f"  ⚠️  警告: 仅提供ID可能无法获取数据，建议使用完整的带token的URL")
        print(f"     正确格式: https://www.xiaohongshu.com/explore/{note_id_or_url}?xsec_token=xxxxx")
        url = f"https://www.xiaohongshu.com/explore/{note_id_or_url}"
    
    # 构建请求数据
    data = {
        "url": url,
        "download": False,  # 先不下载文件，只获取数据
        "skip": False
    }
    
    try:
        response = requests.post(
            XHS_API_URL,
            json=data,
            timeout=XHS_API_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            # 检查是否有数据
            if result.get('data'):
                print(f"  ✓ 成功获取笔记数据")
                return result
            else:
                print(f"  ✗ API返回失败: {result.get('message', '未知错误')}")
                return None
        else:
            print(f"  ✗ API返回错误状态码: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"  ✗ API请求超时")
        return None
    except requests.exceptions.ConnectionError:
        print(f"  ✗ 无法连接到API服务")
        return None
    except Exception as e:
        print(f"  ✗ API调用失败: {e}")
        return None


def save_metadata_md(note_id, api_data):
    """
    保存笔记元数据为MD格式
    
    Args:
        note_id: 笔记ID
        api_data: API返回的数据
    """
    # 使用工具函数获取正确路径
    path = get_project_path("xhs_notes", note_id)
    ensure_dir(path)
    
    # 从API响应中提取数据
    data = api_data.get('data', {})
    
    # 构建元数据内容
    md_content = f"""# 笔记元数据

- **ID**: {note_id}
- **标题**: {data.get('作品标题', '无标题')}
- **作者**: {data.get('作者昵称', '未知')}
- **作者ID**: {data.get('作者ID', '未知')}
- **发布时间**: {data.get('发布时间', '未知')}
- **更新时间**: {data.get('更新时间', '未知')}
- **作品类型**: {data.get('作品类型', '未知')}
- **点赞数量**: {data.get('点赞数量', 0)}
- **收藏数量**: {data.get('收藏数量', 0)}
- **评论数量**: {data.get('评论数量', 0)}
- **分享数量**: {data.get('分享数量', 0)}
- **作品链接**: https://www.xiaohongshu.com/explore/{note_id}

## 原始内容

{data.get('作品描述', '（无描述）')}
"""
    
    # 保存文件
    with open(f"{path}/metadata.md", 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"  ✓ 元数据已保存")


def download_images(note_id, api_data):
    """
    下载笔记的所有图片
    
    Args:
        note_id: 笔记ID
        api_data: API返回的数据
    """
    images_dir = get_project_path("xhs_notes", note_id, "images")
    ensure_dir(images_dir)
    
    # 获取图片链接列表
    data = api_data.get('data', {})
    # API返回的字段是"下载地址"
    image_urls = data.get('下载地址', [])
    
    if not image_urls:
        print(f"  ⚠ 未找到图片链接")
        return
    
    print(f"  → 下载 {len(image_urls)} 张图片...")
    
    # 下载每张图片
    for idx, url in enumerate(image_urls):
        img_path = f"{images_dir}/{idx}.jpg"
        
        # 如果文件已存在，跳过
        if Path(img_path).exists():
            print(f"    ✓ 图片 {idx}.jpg 已存在")
            continue
        
        try:
            # 下载图片
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                print(f"    ✓ 下载图片 {idx}.jpg")
            else:
                print(f"    ✗ 图片 {idx}.jpg 下载失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"    ✗ 图片 {idx}.jpg 下载失败: {e}")
        
        # 添加短暂延迟，避免请求过快
        time.sleep(0.5)


def perform_ocr_on_note(note_id):
    """
    对笔记的所有图片执行OCR识别
    
    Args:
        note_id: 笔记ID
    """
    if not init_ocr():
        return
    
    images_dir = get_project_path("xhs_notes", note_id, "images")
    ocr_dir = get_project_path("xhs_notes", note_id, "ocr_results")
    ensure_dir(ocr_dir)
    
    # 获取所有图片文件
    image_files = sorted(Path(images_dir).glob("*.jpg"))
    
    if not image_files:
        print(f"  ⚠ 未找到图片文件")
        return
    
    print(f"  → OCR识别 {len(image_files)} 张图片...")
    
    for img_file in image_files:
        ocr_md_path = f"{ocr_dir}/{img_file.stem}.md"
        
        # 如果OCR结果已存在，跳过
        if Path(ocr_md_path).exists():
            print(f"    ✓ {img_file.name} OCR结果已存在")
            continue
        
        print(f"    → 识别 {img_file.name}...")
        
        try:
            # 执行OCR (使用predict方法)
            result = ocr.predict(input=str(img_file))
            
            # 提取识别的文本
            text_lines = []
            
            # 处理PaddleOCR返回的结果
            if result and len(result) > 0:
                ocr_result = result[0]
                
                # 新版PaddleOCR 3.2.0：通过json属性访问识别结果
                if hasattr(ocr_result, 'json'):
                    json_data = ocr_result.json
                    if 'res' in json_data and 'rec_texts' in json_data['res']:
                        text_lines = json_data['res']['rec_texts']
                        print(f"    ✓ {img_file.name} OCR完成，识别到 {len(text_lines)} 行文本")
                    else:
                        print(f"    ✗ {img_file.name} OCR结果格式异常")
                else:
                    print(f"    ✗ {img_file.name} OCR返回格式不支持")
            
            # 保存OCR结果为MD格式
            md_content = f"""# 图片OCR识别结果

- **图片文件**: images/{img_file.name}
- **识别时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **识别引擎**: PaddleOCR

## 识别文本

{chr(10).join(text_lines) if text_lines else '（未识别到文字）'}
"""
            
            with open(ocr_md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"    ✓ {img_file.name} OCR完成")
            
        except Exception as e:
            print(f"    ✗ {img_file.name} OCR失败: {e}")


def generate_content_md(note_id):
    """
    生成整合的content.md文件
    
    Args:
        note_id: 笔记ID
    """
    print(f"  → 生成content.md...")
    
    # 读取metadata
    metadata_path = get_project_path("xhs_notes", note_id, "metadata.md")
    if not Path(metadata_path).exists():
        print(f"  ✗ 元数据文件不存在")
        return
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = f.read()
    
    # 提取标题和内容
    import re
    title_match = re.search(r'\*\*标题\*\*: (.+)', metadata)
    title = title_match.group(1) if title_match else '无标题'
    
    content_match = re.search(r'## 原始内容\n\n(.+?)(?=\n##|\Z)', metadata, re.DOTALL)
    content = content_match.group(1).strip() if content_match else ''
    
    # 提取作者和时间信息
    author_match = re.search(r'\*\*作者\*\*: (.+)', metadata)
    author = author_match.group(1) if author_match else '未知'
    
    time_match = re.search(r'\*\*发布时间\*\*: (.+)', metadata)
    pub_time = time_match.group(1) if time_match else '未知'
    
    # 构建content.md
    md_lines = [
        f"# {title}",
        "",
        "## 元信息",
        f"- **作者**: {author}",
        f"- **发布时间**: {pub_time}",
        "",
        "## 正文内容",
        "",
        content if content else "（无正文内容）",
        "",
        "## 图片文本"
    ]
    
    # 添加OCR结果
    ocr_dir = get_project_path("xhs_notes", note_id, "ocr_results")
    if Path(ocr_dir).exists():
        ocr_files = sorted(Path(ocr_dir).glob("*.md"))
        
        for ocr_file in ocr_files:
            idx = ocr_file.stem
            
            # 读取OCR文件
            with open(ocr_file, 'r', encoding='utf-8') as f:
                ocr_content = f.read()
            
            # 提取识别文本
            text_match = re.search(r'## 识别文本\n\n(.+)', ocr_content, re.DOTALL)
            if text_match:
                text = text_match.group(1).strip()
                
                # 添加到content.md
                if idx == "0":
                    md_lines.append(f"\n### 封面图片文本")
                else:
                    md_lines.append(f"\n### 图片{idx}文本")
                
                md_lines.append("")
                md_lines.append(text)
    else:
        md_lines.append("\n（无OCR识别结果）")
    
    # 保存content.md
    content_path = get_project_path("xhs_notes", note_id, "content.md")
    with open(content_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    
    print(f"  ✓ content.md已生成")


def process_note(note_id_or_url, task_id):
    """
    处理单个笔记的完整流程
    
    Args:
        note_id_or_url: 笔记ID或URL
        task_id: 任务ID
    
    Returns:
        str: 处理后的content内容，失败返回None
    """
    # 提取笔记ID用于文件存储
    if note_id_or_url.startswith('http'):
        # 从URL中提取笔记ID
        import re
        match = re.search(r'[0-9a-f]{24}', note_id_or_url.lower())
        if match:
            note_id = match.group()
        else:
            print(f"\n✗ 无法从URL提取笔记ID: {note_id_or_url}")
            return None
    else:
        note_id = note_id_or_url
    
    print(f"\n处理笔记: {note_id}")
    
    # 检查是否已完整处理
    if is_note_complete(note_id):
        print(f"  ✓ 笔记已处理，读取现有数据")
        return read_content_md(note_id)
    
    try:
        # 1. 获取笔记数据
        if not has_metadata(note_id):
            api_result = download_note_via_api(note_id_or_url)
            if not api_result:
                error_msg = f"笔记 {note_id} 获取数据失败"
                create_error_log(task_id, error_msg)
                return None
            
            # 保存元数据
            save_metadata_md(note_id, api_result)
            
            # 下载图片
            download_images(note_id, api_result)
        else:
            print(f"  ✓ 元数据已存在")
        
        # 2. OCR处理
        if not has_ocr_results(note_id):
            perform_ocr_on_note(note_id)
        else:
            print(f"  ✓ OCR结果已存在")
        
        # 3. 生成content.md
        generate_content_md(note_id)
        
        print(f"  ✓ 笔记处理完成")
        return read_content_md(note_id)
        
    except Exception as e:
        error_msg = f"笔记 {note_id} 处理失败: {e}"
        print(f"  ✗ 处理失败: {e}")
        create_error_log(task_id, error_msg)
        return None


def generate_merged_md(task_id, contents, note_ids):
    """
    生成合并的MD文件
    
    Args:
        task_id: 任务ID
        contents: 内容列表
        note_ids: 笔记ID列表
    """
    output_dir = get_project_path("ronggao_output", task_id)
    ensure_dir(output_dir)
    
    # 统计信息
    success_count = len([c for c in contents if c is not None])
    
    # 构建合并文档
    merged_content = f"""# 融稿素材合并文档

## 任务信息

- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **任务ID**: {task_id}
- **处理笔记数**: {len(note_ids)}
- **成功处理**: {success_count}
- **失败处理**: {len(note_ids) - success_count}

## 笔记ID列表

{format_note_ids_display(note_ids)}

---

"""
    
    # 添加每个笔记的内容
    valid_contents = [c for c in contents if c is not None]
    if valid_contents:
        merged_content += "\n\n---\n\n".join(valid_contents)
    else:
        merged_content += "\n⚠ 没有成功处理的笔记内容\n"
    
    # 保存文件
    merged_path = Path(output_dir) / "merged.md"
    with open(merged_path, 'w', encoding='utf-8') as f:
        f.write(merged_content)
    
    print(f"\n✓ 合并文档已生成: ronggao_output/{task_id}/merged.md")


def main():
    """主函数"""
    print("=" * 50)
    print("小红书融稿工具 - 数据处理模块")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("\n错误：请提供笔记ID列表")
        print("用法：python xhs_processor.py \"笔记ID列表\"")
        print("\n示例：")
        print('  python xhs_processor.py "1. 68a9a370000000001b037dc0"')
        sys.exit(1)
    
    # 获取输入
    note_ids_input = sys.argv[1]
    
    # 解析笔记ID或URL
    note_items = parse_note_ids(note_ids_input)
    
    if not note_items:
        print("\n错误：未找到有效的笔记ID或URL")
        print("请确保输入包含24位的笔记ID或小红书URL")
        sys.exit(1)
    
    print(f"\n找到 {len(note_items)} 个笔记:")
    for i, item in enumerate(note_items, 1):
        if item.startswith('http'):
            # 从URL提取ID显示
            import re
            match = re.search(r'[0-9a-f]{24}', item.lower())
            if match:
                print(f"  {i}. {match.group()} (带token)")
        else:
            print(f"  {i}. {item}")
    
    # 检查API服务状态
    if not check_xhs_api_status():
        sys.exit(1)
    
    # 生成任务ID
    task_id = generate_task_id()
    print(f"\n任务ID: {task_id}")
    
    # 处理每个笔记
    print("\n" + "=" * 50)
    print("开始处理笔记")
    print("=" * 50)
    
    all_contents = []
    for note_item in note_items:
        content = process_note(note_item, task_id)
        all_contents.append(content)
    
    # 生成合并文件
    print("\n" + "=" * 50)
    print("生成合并文档")
    print("=" * 50)
    
    generate_merged_md(task_id, all_contents, note_items)
    
    # 输出统计
    success_count = len([c for c in all_contents if c is not None])
    fail_count = len(note_items) - success_count
    
    print("\n" + "=" * 50)
    print("处理完成")
    print("=" * 50)
    print(f"✓ 任务ID: {task_id}")
    print(f"✓ 成功处理: {success_count} 个笔记")
    if fail_count > 0:
        print(f"✗ 失败处理: {fail_count} 个笔记")
        print(f"  查看错误日志: ronggao_output/{task_id}/error.log")
    print(f"✓ 输出目录: ronggao_output/{task_id}/")
    
    # 返回任务ID供后续步骤使用
    return task_id


if __name__ == "__main__":
    main()