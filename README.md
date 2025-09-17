# 小红书融稿工具

一个用于批量处理小红书笔记内容的自动化工具，支持爬取、OCR识别、内容分析和融稿生成。

## 功能特点

- 🔍 **智能爬取**：通过XHS-Downloader API获取笔记数据，无需手动配置Cookie
- 🖼️ **无水印下载**：自动下载高清无水印图片
- 📝 **OCR识别**：使用PaddleOCR识别图片中的文字内容
- 🎯 **内容分析**：AI智能拆解笔记爆点、钩子等关键要素
- ✨ **融稿生成**：基于多篇笔记生成高质量融合稿件
- 💾 **智能缓存**：已处理的笔记自动跳过，支持增量更新

## 项目结构

```
20250910-323/
├── .claude/
│   └── commands/
│       └── 融稿.md                 # Claude Code命令配置
├── scripts/
│   ├── xhs_processor.py           # 主处理脚本
│   └── utils.py                   # 工具函数
├── xhs_notes/                     # 笔记数据存储目录
│   └── {note_id}/                 # 按笔记ID组织
│       ├── metadata.md            # 笔记元数据
│       ├── images/                # 下载的图片
│       ├── ocr_results/           # OCR识别结果
│       └── content.md             # 整合内容
└── ronggao_output/                # 输出目录
    └── {task_id}/                 # 按任务ID组织
        ├── merged.md               # 合并的笔记内容
        ├── analysis.md             # AI分析结果
        └── final.md                # 最终融稿
```

## 快速开始

### 1. 环境准备

#### 启动XHS-Downloader服务

```bash
# 拉取Docker镜像
docker pull joeanamier/xhs-downloader

# 启动API服务
docker run --name xhs-api -d \
  -p 5556:5556 \
  -v xhs_downloader_volume:/app/Volume \
  joeanamier/xhs-downloader python main.py api

# 验证服务状态
curl http://127.0.0.1:5556/docs
```

#### 安装Python依赖

```bash
# 安装PaddleOCR
pip install paddlepaddle paddleocr

# 安装其他依赖
pip install requests pillow
```

### 2. 使用方法

#### 方式一：通过Claude Code命令

在Claude Code中使用 `/融稿` 命令，输入笔记URL列表即可。

**重要：输入格式必须是包含xsec_token的完整URL！**

正确的输入格式示例：

```
1. https://www.xiaohongshu.com/explore/68237be30000000022006481?xsec_token=ABJYasJ70HCCgHE_d6HEa7hx1CQoUWEUkfRp3AiainXKA=
2. https://www.xiaohongshu.com/explore/68986cc300000000250177ef?xsec_token=ABwgUDiCvPUB3IMGDgwrR8lzqVAda8vFXdYDE5NcCXYPA=&xsec_source=pc_user
3. https://www.xiaohongshu.com/explore/689d8a57000000001d016e4b?xsec_token=ABCdefg123456789...
```

⚠️ **注意**：
- 必须使用完整的小红书URL，包含`xsec_token`参数
- 不支持仅输入笔记ID
- URL可以从浏览器地址栏直接复制

#### 方式二：直接运行Python脚本

```bash
cd scripts
python xhs_processor.py "URL列表"
```

示例：

```bash
# 必须使用包含xsec_token的完整URL
python xhs_processor.py "https://www.xiaohongshu.com/explore/68237be30000000022006481?xsec_token=ABJYasJ70HCCgHE_d6HEa7hx1CQoUWEUkfRp3AiainXKA="
```

### 3. 输出说明

处理完成后，会在 `ronggao_output/{task_id}/` 目录下生成：

- **merged.md**: 所有笔记内容的合并文档
- **error.log**: 错误日志（如有）

后续可基于merged.md进行：

- AI内容拆解分析
- 融稿生成

## 工作流程

1. **解析输入**：识别并提取笔记ID
2. **数据获取**：通过API获取笔记信息
3. **图片下载**：下载所有无水印图片
4. **OCR识别**：识别图片中的文字
5. **内容整合**：生成结构化MD文档
6. **合并输出**：生成最终的合并文档

## 注意事项

- 首次运行PaddleOCR会自动下载模型（约100MB）
- XHS-Downloader 2.2版本后无需手动配置Cookie
- 已处理的笔记会自动跳过，避免重复处理
- 支持断点续传和增量更新


# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **XiaoHongShu (小红书) Notes Processing Tool** that automates the extraction and processing of content from XiaoHongShu social media platform. The tool downloads images, performs OCR to extract text, and generates merged content documents.

## Key Architecture

### Core Components

- **xhs_processor.py**: Main processing script that orchestrates the entire workflow - API calls, image downloads, OCR processing, and content generation
- **utils.py**: Utility functions for path management, input parsing, error logging, and display formatting
- **XHS-Downloader API**: Docker-based service (port 5556) that handles the actual data fetching from XiaoHongShu

### Data Flow

1. Parse input (note IDs or URLs) → 2. Fetch data via API → 3. Download images → 4. OCR text extraction → 5. Generate merged content

### Performance Configuration

- Uses **PP-OCRv4 Mobile** model for optimal speed/accuracy balance
- **GPU acceleration** enabled (CUDA 11.8) - reduces OCR time from 48s to 0.3s per image
- Smart caching mechanism to skip already processed notes

## Common Commands

### Running the Main Script

```bash
# Process single note
python scripts/xhs_processor.py "68986cc300000000250177ef"

# Process multiple notes
python scripts/xhs_processor.py "1. 68986cc300000000250177ef 2. 689d8a57000000001d016e4b"

# Process with URL (including token)
python scripts/xhs_processor.py "https://www.xiaohongshu.com/explore/689d8a57000000001d016e4b?xsec_token=ABC..."
```

### Testing

```bash
# Run all tests
cd tests && python run_tests.py --all

# Run specific test module
python run_tests.py --test test_utils

# Run integration tests only
python run_tests.py --integration
```

### Docker Setup

```bash
# Start XHS-Downloader service
setup_docker.bat
```

## Directory Structure

- `xhs_notes/{note_id}/` - Stores downloaded content per note
  - `metadata.md` - Note metadata
  - `images/` - Downloaded images
  - `ocr_results/` - OCR text for each image
  - `content.md` - Combined content
- `ronggao_output/{task_id}/` - Output directory for merged documents
- `scripts/` - Main processing scripts
- `tests/` - Test suite

## Critical Configuration

### OCR Engine Setup

The project uses PaddleOCR with specific optimizations:

- Model: `PP-OCRv4` (not v5 - v4 is 3.5x faster)
- Device: `gpu:0` if available, falls back to CPU
- Disabled features for speed: `use_doc_orientation_classify=False`, `use_doc_unwarping=False`

### API Service Requirements

- XHS-Downloader must be running on `http://localhost:5556`
- Check service status before processing: `curl http://localhost:5556/api/test`

## Error Handling

- All errors are logged to `ronggao_output/{task_id}/error.log`
- The processor continues with remaining notes even if one fails
- Already processed notes are automatically skipped (check for existing `content.md`)

## Input Format Support

The tool accepts multiple input formats:

1. Plain note ID: `68986cc300000000250177ef`
2. Numbered list: `1. ID1 2. ID2`
3. URL: `https://www.xiaohongshu.com/explore/NOTE_ID`
4. URL with token: `https://www.xiaohongshu.com/explore/NOTE_ID?xsec_token=...`

## Development Notes

- **Path Management**: All paths use `get_project_path()` from utils.py to ensure correct relative paths
- **OCR Results**: In PaddleOCR 3.2.0, text is accessed via `json['res']['rec_texts']` not direct attributes
- **Testing**: Mock data is provided in test_config.py for offline testing
- **GPU Check**: The script automatically detects and uses GPU if available via `paddle.device.get_device()`
