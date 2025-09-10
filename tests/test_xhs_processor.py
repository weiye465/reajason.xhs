"""
xhs_processor.py 模块的单元测试
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import xhs_processor
from xhs_processor import (
    check_xhs_api_status,
    download_note_via_api,
    save_metadata_md,
    download_images,
    perform_ocr_on_note,
    generate_content_md,
    process_note,
    generate_merged_md
)


class TestXHSProcessor(unittest.TestCase):
    """测试XHS处理器功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时测试目录
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 创建必要的目录结构
        os.makedirs("xhs_notes", exist_ok=True)
        os.makedirs("ronggao_output", exist_ok=True)
    
    def tearDown(self):
        """清理测试环境"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('requests.get')
    def test_check_xhs_api_status_success(self, mock_get):
        """测试API状态检查 - 成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = check_xhs_api_status()
        self.assertTrue(result)
        mock_get.assert_called_once_with("http://127.0.0.1:5556/docs", timeout=5)
    
    @patch('requests.get')
    def test_check_xhs_api_status_failure(self, mock_get):
        """测试API状态检查 - 失败"""
        mock_get.side_effect = Exception("Connection error")
        
        result = check_xhs_api_status()
        self.assertFalse(result)
    
    @patch('requests.post')
    def test_download_note_via_api_success(self, mock_post):
        """测试通过API下载笔记 - 成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                '作品标题': '测试标题',
                '作者昵称': '测试作者',
                '作品描述': '测试内容'
            }
        }
        mock_post.return_value = mock_response
        
        result = download_note_via_api('test_note_id')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['data']['作品标题'], '测试标题')
        
        # 验证请求参数
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], xhs_processor.XHS_API_URL)
        self.assertIn('url', call_args[1]['json'])
    
    @patch('requests.post')
    def test_download_note_via_api_failure(self, mock_post):
        """测试通过API下载笔记 - 失败"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        result = download_note_via_api('test_note_id')
        self.assertIsNone(result)
    
    def test_save_metadata_md(self):
        """测试保存元数据"""
        note_id = "test_note_001"
        api_data = {
            'data': {
                '作品标题': '测试标题',
                '作者昵称': '测试作者',
                '作者ID': 'author123',
                '发布时间': '2024-01-01 12:00:00',
                '更新时间': '2024-01-02 12:00:00',
                '作品类型': '图文',
                '点赞数量': 100,
                '收藏数量': 50,
                '评论数量': 20,
                '分享数量': 10,
                '作品描述': '这是测试描述内容',
                '标签': ['测试', '标签1', '标签2']
            }
        }
        
        save_metadata_md(note_id, api_data)
        
        # 验证文件是否创建
        metadata_path = Path(f"xhs_notes/{note_id}/metadata.md")
        self.assertTrue(metadata_path.exists())
        
        # 验证文件内容
        content = metadata_path.read_text(encoding='utf-8')
        self.assertIn('测试标题', content)
        self.assertIn('测试作者', content)
        self.assertIn('这是测试描述内容', content)
        self.assertIn('测试, 标签1, 标签2', content)
    
    @patch('requests.get')
    def test_download_images(self, mock_get):
        """测试下载图片"""
        note_id = "test_note_002"
        api_data = {
            'data': {
                '图片链接': [
                    'http://example.com/image1.jpg',
                    'http://example.com/image2.jpg'
                ]
            }
        }
        
        # 模拟图片下载
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'fake_image_data'
        mock_get.return_value = mock_response
        
        download_images(note_id, api_data)
        
        # 验证图片文件是否创建
        image1_path = Path(f"xhs_notes/{note_id}/images/0.jpg")
        image2_path = Path(f"xhs_notes/{note_id}/images/1.jpg")
        
        self.assertTrue(image1_path.exists())
        self.assertTrue(image2_path.exists())
        
        # 验证请求次数
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('xhs_processor.init_ocr')
    @patch('xhs_processor.ocr')
    def test_perform_ocr_on_note(self, mock_ocr_obj, mock_init_ocr):
        """测试OCR处理"""
        note_id = "test_note_003"
        
        # 准备测试图片
        images_dir = Path(f"xhs_notes/{note_id}/images")
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建假图片文件
        (images_dir / "0.jpg").write_bytes(b"fake_image")
        (images_dir / "1.jpg").write_bytes(b"fake_image")
        
        # 模拟OCR结果
        mock_init_ocr.return_value = True
        mock_ocr_instance = MagicMock()
        mock_ocr_instance.ocr.return_value = [
            [
                [[0, 0], [100, 100], "测试文字1", 0.99],
                [[0, 0], [100, 100], "测试文字2", 0.98]
            ]
        ]
        xhs_processor.ocr = mock_ocr_instance
        
        perform_ocr_on_note(note_id)
        
        # 验证OCR结果文件是否创建
        ocr1_path = Path(f"xhs_notes/{note_id}/ocr_results/0.md")
        ocr2_path = Path(f"xhs_notes/{note_id}/ocr_results/1.md")
        
        self.assertTrue(ocr1_path.exists())
        self.assertTrue(ocr2_path.exists())
        
        # 验证OCR内容
        ocr_content = ocr1_path.read_text(encoding='utf-8')
        self.assertIn('测试文字1', ocr_content)
        self.assertIn('测试文字2', ocr_content)
    
    def test_generate_content_md(self):
        """测试生成content.md"""
        note_id = "test_note_004"
        
        # 准备元数据
        metadata_dir = Path(f"xhs_notes/{note_id}")
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        metadata_content = """# 笔记元数据

- **标题**: 测试标题
- **作者**: 测试作者
- **发布时间**: 2024-01-01

## 原始内容

这是原始内容文本
"""
        (metadata_dir / "metadata.md").write_text(metadata_content, encoding='utf-8')
        
        # 准备OCR结果
        ocr_dir = metadata_dir / "ocr_results"
        ocr_dir.mkdir(exist_ok=True)
        
        ocr0_content = """# 图片OCR识别结果

## 识别文本

封面图片的文字内容
"""
        (ocr_dir / "0.md").write_text(ocr0_content, encoding='utf-8')
        
        ocr1_content = """# 图片OCR识别结果

## 识别文本

第一张图片的文字内容
"""
        (ocr_dir / "1.md").write_text(ocr1_content, encoding='utf-8')
        
        # 生成content.md
        generate_content_md(note_id)
        
        # 验证content.md是否创建
        content_path = metadata_dir / "content.md"
        self.assertTrue(content_path.exists())
        
        # 验证内容
        content = content_path.read_text(encoding='utf-8')
        self.assertIn('测试标题', content)
        self.assertIn('测试作者', content)
        self.assertIn('这是原始内容文本', content)
        self.assertIn('封面图片文本', content)
        self.assertIn('封面图片的文字内容', content)
        self.assertIn('图片1文本', content)
        self.assertIn('第一张图片的文字内容', content)
    
    @patch('xhs_processor.download_note_via_api')
    @patch('xhs_processor.download_images')
    @patch('xhs_processor.perform_ocr_on_note')
    def test_process_note_new(self, mock_ocr, mock_download_images, mock_download_api):
        """测试处理新笔记"""
        note_id = "test_note_005"
        task_id = "test_task_001"
        
        # 模拟API返回
        mock_download_api.return_value = {
            'data': {
                '作品标题': '测试标题',
                '作者昵称': '测试作者',
                '作品描述': '测试描述'
            }
        }
        
        # 执行处理
        result = process_note(note_id, task_id)
        
        # 由于没有实际生成content.md，结果应该是None
        # 但应该调用了相关函数
        mock_download_api.assert_called_once_with(note_id)
        mock_download_images.assert_called_once()
        mock_ocr.assert_called_once_with(note_id)
    
    def test_process_note_existing(self):
        """测试处理已存在的笔记"""
        note_id = "test_note_006"
        task_id = "test_task_002"
        
        # 创建已存在的content.md
        note_dir = Path(f"xhs_notes/{note_id}")
        note_dir.mkdir(parents=True, exist_ok=True)
        
        existing_content = "# 已存在的内容\n\n这是已经处理过的笔记"
        (note_dir / "content.md").write_text(existing_content, encoding='utf-8')
        
        # 执行处理
        result = process_note(note_id, task_id)
        
        # 应该直接返回已存在的内容
        self.assertEqual(result, existing_content)
    
    def test_generate_merged_md(self):
        """测试生成合并文档"""
        task_id = "test_task_003"
        note_ids = ["note1", "note2", "note3"]
        contents = [
            "# 笔记1\n内容1",
            "# 笔记2\n内容2",
            None  # 模拟一个失败的笔记
        ]
        
        generate_merged_md(task_id, contents, note_ids)
        
        # 验证文件是否创建
        merged_path = Path(f"ronggao_output/{task_id}/merged.md")
        self.assertTrue(merged_path.exists())
        
        # 验证内容
        merged_content = merged_path.read_text(encoding='utf-8')
        self.assertIn('任务ID: test_task_003', merged_content)
        self.assertIn('成功处理: 2', merged_content)
        self.assertIn('失败处理: 1', merged_content)
        self.assertIn('# 笔记1', merged_content)
        self.assertIn('# 笔记2', merged_content)
        self.assertIn('note1', merged_content)
        self.assertIn('note2', merged_content)
        self.assertIn('note3', merged_content)
    
    @patch('sys.argv', ['xhs_processor.py', ''])
    def test_main_no_input(self):
        """测试主函数 - 无输入"""
        with self.assertRaises(SystemExit) as cm:
            xhs_processor.main()
        
        self.assertEqual(cm.exception.code, 1)
    
    @patch('sys.argv', ['xhs_processor.py', 'invalid_input'])
    def test_main_invalid_input(self):
        """测试主函数 - 无效输入"""
        with self.assertRaises(SystemExit) as cm:
            xhs_processor.main()
        
        self.assertEqual(cm.exception.code, 1)


class TestXHSProcessorIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """清理测试环境"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_full_workflow_simulation(self):
        """模拟完整工作流程"""
        note_id = "68a9a370000000001b037dc0"
        
        # 创建模拟数据结构
        note_dir = Path(f"xhs_notes/{note_id}")
        note_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建元数据
        metadata = """# 笔记元数据

- **标题**: 集成测试标题
- **作者**: 集成测试作者
- **发布时间**: 2024-01-01

## 原始内容

这是集成测试的内容
"""
        (note_dir / "metadata.md").write_text(metadata, encoding='utf-8')
        
        # 创建图片目录
        images_dir = note_dir / "images"
        images_dir.mkdir(exist_ok=True)
        (images_dir / "0.jpg").write_bytes(b"fake_image_0")
        (images_dir / "1.jpg").write_bytes(b"fake_image_1")
        
        # 创建OCR结果
        ocr_dir = note_dir / "ocr_results"
        ocr_dir.mkdir(exist_ok=True)
        
        ocr0 = """# 图片OCR识别结果

## 识别文本

封面图片OCR文本
"""
        (ocr_dir / "0.md").write_text(ocr0, encoding='utf-8')
        
        ocr1 = """# 图片OCR识别结果

## 识别文本

内容图片OCR文本
"""
        (ocr_dir / "1.md").write_text(ocr1, encoding='utf-8')
        
        # 生成content.md
        generate_content_md(note_id)
        
        # 验证完整性
        content_path = note_dir / "content.md"
        self.assertTrue(content_path.exists())
        
        content = content_path.read_text(encoding='utf-8')
        self.assertIn('集成测试标题', content)
        self.assertIn('集成测试作者', content)
        self.assertIn('这是集成测试的内容', content)
        self.assertIn('封面图片OCR文本', content)
        self.assertIn('内容图片OCR文本', content)
        
        # 测试合并功能
        task_id = "integration_test_001"
        contents = [content]
        note_ids = [note_id]
        
        generate_merged_md(task_id, contents, note_ids)
        
        merged_path = Path(f"ronggao_output/{task_id}/merged.md")
        self.assertTrue(merged_path.exists())
        
        merged_content = merged_path.read_text(encoding='utf-8')
        self.assertIn(note_id, merged_content)
        self.assertIn('集成测试标题', merged_content)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)