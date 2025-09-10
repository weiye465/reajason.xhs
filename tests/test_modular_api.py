"""
测试PaddleOCR模块化API
重点测试PP-OCRv5_mobile模型
"""

from pathlib import Path
import time
import sys
import os

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

print("="*60)
print("PaddleOCR PP-OCRv5 Mobile 模型测试")
print("="*60)

# 测试图片
img_path = project_root / "xhs_notes/68986cc300000000250177ef/images/0.jpg"

if not img_path.exists():
    print(f"测试图片不存在: {img_path}")
    exit(1)

# 测试1: 使用TextDetection单独测试PP-OCRv5_mobile_det
print("\n1. 测试PP-OCRv5_mobile_det (文本检测)")
print("-"*40)

try:
    from paddleocr import TextDetection
    
    print("初始化PP-OCRv5_mobile_det...")
    start = time.time()
    det_model = TextDetection(
        model_name="PP-OCRv5_mobile_det",
        device="gpu:0"
    )
    init_time = time.time() - start
    print(f"初始化耗时: {init_time:.2f}秒")
    
    # 执行多次检测测试
    print("\n执行文本检测（3次测试）...")
    det_times = []
    box_counts = []
    
    for i in range(3):
        start = time.time()
        det_output = det_model.predict(input=str(img_path), batch_size=1)
        det_time = time.time() - start
        det_times.append(det_time)
        
        # 获取检测框数量
        if det_output and i == 0:
            for res in det_output:
                if hasattr(res, 'json'):
                    json_data = res.json
                    if 'res' in json_data and 'dt_polys' in json_data['res']:
                        boxes = json_data['res']['dt_polys']
                        box_counts.append(len(boxes))
                        if i == 0:
                            print(f"  第{i+1}次: {det_time:.3f}秒, 检测到 {len(boxes)} 个文本框")
                        break
        else:
            print(f"  第{i+1}次: {det_time:.3f}秒")
    
    avg_det_time = sum(det_times) / len(det_times)
    print(f"\n平均检测耗时: {avg_det_time:.3f}秒")
    print(f"最快检测耗时: {min(det_times):.3f}秒")
    
    # 保存检测结果
    if det_output:
        output_dir = project_root / "tests/output_det"
        output_dir.mkdir(exist_ok=True)
        for res in det_output:
            res.save_to_img(save_path=str(output_dir))
            print(f"检测结果已保存到: {output_dir}")
            break
    
except Exception as e:
    print(f"PP-OCRv5_mobile_det错误: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 使用TextRecognition单独测试PP-OCRv5_mobile_rec
print("\n2. 测试PP-OCRv5_mobile_rec (文本识别)")
print("-"*40)

try:
    from paddleocr import TextRecognition
    
    print("初始化PP-OCRv5_mobile_rec...")
    start = time.time()
    rec_model = TextRecognition(
        model_name="PP-OCRv5_mobile_rec",
        device="gpu:0"
    )
    init_time = time.time() - start
    print(f"初始化耗时: {init_time:.2f}秒")
    
    # 注意：TextRecognition需要裁剪后的文本区域
    # 这里直接用整张图片会识别失败
    print("\n执行文本识别（整图测试）...")
    start = time.time()
    rec_output = rec_model.predict(input=str(img_path), batch_size=1)
    rec_time = time.time() - start
    print(f"识别耗时: {rec_time:.3f}秒")
    
    if rec_output:
        for res in rec_output:
            if hasattr(res, 'json'):
                json_data = res.json
                print(f"识别结果: {json_data.get('res', {}).get('rec_text', '无')}")
            break
    
    print("\n注意: TextRecognition模块需要预先裁剪的文本区域，不适合直接处理整图")
    
except Exception as e:
    print(f"PP-OCRv5_mobile_rec错误: {e}")
    import traceback
    traceback.print_exc()

# 测试3: 使用完整的PaddleOCR比较不同版本
print("\n3. 使用PaddleOCR完整流程对比")
print("-"*40)

try:
    from paddleocr import PaddleOCR
    
    configs = [
        {
            "name": "PP-OCRv4 (当前使用)",
            "config": {
                "ocr_version": "PP-OCRv4",
                "use_doc_orientation_classify": False,
                "use_doc_unwarping": False,
                "use_textline_orientation": False,
                "lang": "ch",
                "device": "gpu:0"
            }
        },
        {
            "name": "PP-OCRv5 (最新版本)",
            "config": {
                "ocr_version": "PP-OCRv5",
                "use_doc_orientation_classify": False,
                "use_doc_unwarping": False,
                "use_textline_orientation": False,
                "lang": "ch",
                "device": "gpu:0"
            }
        }
    ]
    
    results = []
    
    for cfg in configs:
        print(f"\n测试 {cfg['name']}...")
        
        # 初始化
        start = time.time()
        ocr = PaddleOCR(**cfg['config'])
        init_time = time.time() - start
        print(f"  初始化: {init_time:.2f}秒")
        
        # 执行OCR（3次）
        ocr_times = []
        text_count = 0
        
        for i in range(3):
            start = time.time()
            result = ocr.predict(input=str(img_path))
            ocr_time = time.time() - start
            ocr_times.append(ocr_time)
            
            # 第一次获取文本数量
            if i == 0 and result and len(result) > 0:
                ocr_result = result[0]
                if hasattr(ocr_result, 'json'):
                    json_data = ocr_result.json
                    if 'res' in json_data and 'rec_texts' in json_data['res']:
                        text_count = len(json_data['res']['rec_texts'])
        
        avg_time = sum(ocr_times) / len(ocr_times)
        min_time = min(ocr_times)
        
        print(f"  平均OCR: {avg_time:.3f}秒")
        print(f"  最快OCR: {min_time:.3f}秒")
        print(f"  识别文本: {text_count}行")
        
        results.append({
            "name": cfg['name'],
            "init": init_time,
            "avg": avg_time,
            "min": min_time,
            "texts": text_count
        })
    
    # 输出对比
    print("\n" + "="*60)
    print("性能对比结果")
    print("="*60)
    
    print(f"\n{'模型':<25} {'初始化(秒)':<12} {'平均(秒)':<12} {'最快(秒)':<12} {'文本行':<10}")
    print("-"*75)
    
    for r in results:
        print(f"{r['name']:<25} {r['init']:<12.2f} {r['avg']:<12.3f} {r['min']:<12.3f} {r['texts']:<10}")
    
    # 速度对比
    if len(results) == 2:
        speedup = results[0]['avg'] / results[1]['avg']
        if speedup > 1:
            print(f"\nPP-OCRv5 比 PP-OCRv4 快 {speedup:.2f}倍")
        else:
            print(f"\nPP-OCRv4 比 PP-OCRv5 快 {1/speedup:.2f}倍")
    
except Exception as e:
    print(f"PaddleOCR对比测试错误: {e}")
    import traceback
    traceback.print_exc()

# 测试4: 尝试通过模型路径直接使用PP-OCRv5_mobile
print("\n4. 探索PP-OCRv5_mobile的正确配置方式")
print("-"*40)

try:
    # 检查模型文件是否已下载
    model_base = Path.home() / ".paddlex/official_models"
    det_model_path = model_base / "PP-OCRv5_mobile_det"
    rec_model_path = model_base / "PP-OCRv5_mobile_rec"
    
    print(f"检查模型文件:")
    print(f"  检测模型: {det_model_path.exists()} - {det_model_path}")
    print(f"  识别模型: {rec_model_path.exists()} - {rec_model_path}")
    
    if det_model_path.exists() and rec_model_path.exists():
        # 尝试使用模型路径
        from paddleocr import PaddleOCR
        
        print("\n尝试使用模型路径配置...")
        try:
            ocr = PaddleOCR(
                det_model_dir=str(det_model_path),
                rec_model_dir=str(rec_model_path),
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang="ch",
                device="gpu:0"
            )
            print("✓ 模型路径配置成功")
            
            # 测试
            start = time.time()
            result = ocr.predict(input=str(img_path))
            ocr_time = time.time() - start
            
            if result and len(result) > 0:
                ocr_result = result[0]
                if hasattr(ocr_result, 'json'):
                    json_data = ocr_result.json
                    if 'res' in json_data and 'rec_texts' in json_data['res']:
                        texts = json_data['res']['rec_texts']
                        print(f"✓ 识别成功: {len(texts)}行文本, 耗时{ocr_time:.3f}秒")
            
        except Exception as e:
            print(f"✗ 模型路径配置失败: {e}")
    
except Exception as e:
    print(f"模型路径测试错误: {e}")

print("\n" + "="*60)
print("测试完成")
print("="*60)