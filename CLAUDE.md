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