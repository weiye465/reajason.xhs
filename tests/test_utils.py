"""
utils.py 模块的单元测试
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys
import os

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from utils import (
    generate_task_id,
    parse_note_ids,
    ensure_dir,
    is_note_complete,
    has_metadata,
    has_ocr_results,
    read_content_md,
    format_note_ids_display,
    create_error_log
)


class TestUtils(unittest.TestCase):
    """测试工具函数"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时测试目录
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """清理测试环境"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_generate_task_id(self):
        """测试任务ID生成"""
        task_id = generate_task_id()
        
        # 检查格式：YYYYMMDD-HHMMSS-XXXXXX
        self.assertIsNotNone(task_id)
        parts = task_id.split('-')
        self.assertEqual(len(parts), 3)
        
        # 检查日期部分
        self.assertEqual(len(parts[0]), 8)  # YYYYMMDD
        self.assertTrue(parts[0].isdigit())
        
        # 检查时间部分
        self.assertEqual(len(parts[1]), 6)  # HHMMSS
        self.assertTrue(parts[1].isdigit())
        
        # 检查随机哈希部分
        self.assertEqual(len(parts[2]), 6)  # 6位十六进制
        
        # 测试唯一性
        task_id2 = generate_task_id()
        self.assertNotEqual(task_id, task_id2)
    
    def test_parse_note_ids(self):
        """测试笔记ID解析"""
        # 测试带序号的列表
        input1 = """
        1. 68a9a370000000001b037dc0
        2. 68a82fc1000000001d02ab79
        3. 68a82d32000000001d03619c
        """
        ids1 = parse_note_ids(input1)
        self.assertEqual(len(ids1), 3)
        self.assertIn('68a9a370000000001b037dc0', ids1)
        
        # 测试逗号分隔
        input2 = "68a9a370000000001b037dc0,68a82fc1000000001d02ab79"
        ids2 = parse_note_ids(input2)
        self.assertEqual(len(ids2), 2)
        
        # 测试URL格式
        input3 = "https://www.xiaohongshu.com/explore/68a9a370000000001b037dc0"
        ids3 = parse_note_ids(input3)
        self.assertEqual(len(ids3), 1)
        self.assertEqual(ids3[0], '68a9a370000000001b037dc0')
        
        # 测试去重
        input4 = """
        68a9a370000000001b037dc0
        68a9a370000000001b037dc0
        68a9a370000000001b037dc0
        """
        ids4 = parse_note_ids(input4)
        self.assertEqual(len(ids4), 1)
        
        # 测试无效输入
        input5 = "这是一些无效的文本"
        ids5 = parse_note_ids(input5)
        self.assertEqual(len(ids5), 0)
        
        # 测试混合格式
        input6 = """
        1. 68a9a370000000001b037dc0
        https://www.xiaohongshu.com/explore/68a82fc1000000001d02ab79
        68a82d32000000001d03619c
        """
        ids6 = parse_note_ids(input6)
        self.assertEqual(len(ids6), 3)
    
    def test_ensure_dir(self):
        """测试目录创建"""
        test_path = "test_dir/sub_dir/nested"
        
        # 确保目录不存在
        self.assertFalse(Path(test_path).exists())
        
        # 创建目录
        ensure_dir(test_path)
        
        # 验证目录已创建
        self.assertTrue(Path(test_path).exists())
        self.assertTrue(Path(test_path).is_dir())
        
        # 再次调用不应报错
        ensure_dir(test_path)
        self.assertTrue(Path(test_path).exists())
    
    def test_is_note_complete(self):
        """测试笔记完成状态检查"""
        note_id = "test_note_123"
        
        # 初始状态应为未完成
        self.assertFalse(is_note_complete(note_id))
        
        # 创建content.md文件
        note_dir = f"xhs_notes/{note_id}"
        ensure_dir(note_dir)
        content_path = Path(note_dir) / "content.md"
        content_path.write_text("测试内容", encoding='utf-8')
        
        # 现在应该显示为完成
        self.assertTrue(is_note_complete(note_id))
    
    def test_has_metadata(self):
        """测试元数据存在检查"""
        note_id = "test_note_456"
        
        # 初始状态应为不存在
        self.assertFalse(has_metadata(note_id))
        
        # 创建metadata.md文件
        note_dir = f"xhs_notes/{note_id}"
        ensure_dir(note_dir)
        metadata_path = Path(note_dir) / "metadata.md"
        metadata_path.write_text("# 元数据", encoding='utf-8')
        
        # 现在应该显示为存在
        self.assertTrue(has_metadata(note_id))
    
    def test_has_ocr_results(self):
        """测试OCR结果存在检查"""
        note_id = "test_note_789"
        
        # 初始状态应为不存在
        self.assertFalse(has_ocr_results(note_id))
        
        # 创建OCR结果目录但不放文件
        ocr_dir = f"xhs_notes/{note_id}/ocr_results"
        ensure_dir(ocr_dir)
        self.assertFalse(has_ocr_results(note_id))
        
        # 添加OCR结果文件
        ocr_file = Path(ocr_dir) / "0.md"
        ocr_file.write_text("OCR结果", encoding='utf-8')
        
        # 现在应该显示为存在
        self.assertTrue(has_ocr_results(note_id))
    
    def test_read_content_md(self):
        """测试读取content.md"""
        note_id = "test_note_abc"
        
        # 不存在时应返回None
        self.assertIsNone(read_content_md(note_id))
        
        # 创建content.md
        note_dir = f"xhs_notes/{note_id}"
        ensure_dir(note_dir)
        content_path = Path(note_dir) / "content.md"
        test_content = "# 测试标题\n\n这是测试内容"
        content_path.write_text(test_content, encoding='utf-8')
        
        # 读取内容
        result = read_content_md(note_id)
        self.assertEqual(result, test_content)
    
    def test_format_note_ids_display(self):
        """测试格式化显示笔记ID列表"""
        # 测试空列表
        result1 = format_note_ids_display([])
        self.assertEqual(result1, "无")
        
        # 测试单个ID
        ids2 = ["68a9a370000000001b037dc0"]
        result2 = format_note_ids_display(ids2)
        self.assertIn("1. 68a9a370000000001b037dc0", result2)
        
        # 测试多个ID
        ids3 = [
            "68a9a370000000001b037dc0",
            "68a82fc1000000001d02ab79",
            "68a82d32000000001d03619c"
        ]
        result3 = format_note_ids_display(ids3)
        lines = result3.split('\n')
        self.assertEqual(len(lines), 3)
        self.assertIn("1. 68a9a370000000001b037dc0", lines[0])
        self.assertIn("2. 68a82fc1000000001d02ab79", lines[1])
        self.assertIn("3. 68a82d32000000001d03619c", lines[2])
    
    def test_create_error_log(self):
        """测试错误日志创建"""
        task_id = "test_task_123"
        error_msg = "这是一个测试错误"
        
        # 创建错误日志
        create_error_log(task_id, error_msg)
        
        # 验证日志文件存在
        log_path = Path(f"ronggao_output/{task_id}/error.log")
        self.assertTrue(log_path.exists())
        
        # 验证日志内容
        log_content = log_path.read_text(encoding='utf-8')
        self.assertIn(error_msg, log_content)
        self.assertIn(datetime.now().strftime("%Y-%m-%d"), log_content)
        
        # 测试追加日志
        error_msg2 = "第二个错误"
        create_error_log(task_id, error_msg2)
        
        log_content2 = log_path.read_text(encoding='utf-8')
        self.assertIn(error_msg, log_content2)
        self.assertIn(error_msg2, log_content2)
        
        # 确保有两行日志
        lines = log_content2.strip().split('\n')
        self.assertEqual(len(lines), 2)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)