# 小红书融稿工具

一个专业的小红书笔记融稿工具，通过赛马机制从多篇爆款中提取最优内容，生成高质量的图片文本和正文。

## 软件更新说明

如果需要更新软件，请按照以下步骤操作：

1. 从 git main 分支拉取最新代码
   ```bash
   git pull origin main
   ```

2. 只需要更新以下文件和文件夹：
   - `.claude/commands` 文件夹
   - `scripts` 文件夹下的所有文件
   - `README.md` 文件

其他文件和文件夹（如 `xhs_notes`、`ronggao_output` 等）保持不变即可。

## 功能特点

- 🔍 **智能爬取**：通过XHS-Downloader API获取笔记数据，无需手动配置Cookie
- 🖼️ **无水印下载**：自动下载高清无水印图片
- 📝 **OCR识别**：使用PaddleOCR识别图片中的文字内容
- 🏇 **赛马选优**：将内容拆分成小单元，从多篇爆款中筛选最优表达
- ✨ **两步生成**：先生成图片文本，再生成标题正文，两者同等重要
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
        ├── images.md               # 融合的图片文本
        └── content.md              # 最终标题+正文
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
- **images.md**: AI生成的融合图片文本
- **content.md**: AI生成的标题和正文
- **error.log**: 错误日志（如有）

## 工作流程

### 数据处理阶段
1. **解析输入**：识别并提取笔记ID
2. **数据获取**：通过API获取笔记信息
3. **图片下载**：下载所有无水印图片
4. **OCR识别**：识别图片中的文字
5. **内容整合**：生成merged.md合并文档

### AI融稿阶段
6. **生成图片文本**：通过赛马机制从爆款中选优，生成images.md
7. **生成标题正文**：基于图片文本和爆款风格，生成content.md

## 注意事项

- 首次运行PaddleOCR会自动下载模型（约100MB）
- XHS-Downloader 2.2版本后无需手动配置Cookie
- 已处理的笔记会自动跳过，避免重复处理
- 支持断点续传和增量更新


## 核心特性

### 赛马机制
本工具的核心是"赛马选优"机制：
- 将内容拆分成小单元（如每个问题）
- 在多篇爆款中横向对比
- 筛选每个单元最优的表达方式
- 重新组装成高质量内容
- 保证85%以上的相似度，同时保留差异化

### 两步生成策略
1. **生成图片文本**：从merged.md的图片文本部分，通过赛马机制生成融合版
2. **生成标题正文**：从merged.md的正文内容部分，通过赛马机制生成融合版
   - 注意：标题正文主要基于merged.md中的正文内容生成，而非images.md
   - 图片和正文同等重要，各自承载不同的信息价值

## 技术架构

### 核心组件

- **xhs_processor.py**: 主处理脚本，协调整个工作流
- **utils.py**: 工具函数（路径管理、输入解析、错误日志等）
- **XHS-Downloader API**: Docker服务（端口5556），处理数据获取
- **PaddleOCR**: PP-OCRv4模型，GPU加速将OCR时间从48秒降至0.3秒


## 开发说明

- **路径管理**：使用`get_project_path()`确保正确的相对路径
- **OCR结果**：PaddleOCR 3.2.0中通过`json['res']['rec_texts']`访问文本
- **GPU检测**：自动检测并使用GPU（如可用）
- **错误处理**：错误记录到`ronggao_output/{task_id}/error.log`
- **缓存机制**：已处理的笔记自动跳过，检查`content.md`是否存在
