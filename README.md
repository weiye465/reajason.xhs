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

在Claude Code中使用 `/融稿` 命令，输入笔记ID列表即可。

支持的输入格式：
```
1. 68a9a370000000001b037dc0
2. 68a82fc1000000001d02ab79
3. https://www.xiaohongshu.com/explore/68a82d32000000001d03619c
4. https://www.xiaohongshu.com/explore/68986cc300000000250177ef?xsec_token=ABwgUDiCvPUB3IMGDgwrR8lzqVAda8vFXdYDE5NcCXYPA=&xsec_source=pc_user
```

#### 方式二：直接运行Python脚本

```bash
cd scripts
python xhs_processor.py "笔记ID列表"
```

示例：
```bash
python xhs_processor.py "1. 68a9a370000000001b037dc0 2. 68a82fc1000000001d02ab79"
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

## 常见问题

### Q: API服务连接失败？
A: 确保Docker容器正在运行：
```bash
docker ps
docker start xhs-api  # 如果未运行
```

### Q: OCR识别失败？
A: 检查PaddleOCR是否正确安装：
```bash
pip install --upgrade paddlepaddle paddleocr
```

### Q: 如何查看处理进度？
A: 脚本会实时输出处理状态，包括成功/失败的笔记数量。

## 技术栈

- **爬虫服务**: XHS-Downloader (Docker)
- **OCR引擎**: PaddleOCR
- **开发语言**: Python 3.x
- **集成工具**: Claude Code

## 更新日志

- 2024-01-11: 初始版本发布
  - 实现基础的爬取和OCR功能
  - 支持批量处理多个笔记
  - 智能缓存机制

## 联系方式

如有问题或建议，请提交Issue。