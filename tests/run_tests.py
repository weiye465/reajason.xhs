"""
测试运行器
用于执行所有测试并生成报告
"""

import unittest
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始运行单元测试")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试模块
    test_modules = [
        'test_utils',
        'test_xhs_processor'
    ]
    
    for module in test_modules:
        try:
            tests = loader.loadTestsFromName(module)
            suite.addTests(tests)
            print(f"✓ 加载测试模块: {module}")
        except Exception as e:
            print(f"✗ 加载测试模块失败 {module}: {e}")
    
    # 运行测试
    print("\n" + "=" * 60)
    print("执行测试用例")
    print("=" * 60 + "\n")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出统计
    print("\n" + "=" * 60)
    print("测试结果统计")
    print("=" * 60)
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    # 详细的失败信息
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            print(f"    {traceback[:200]}...")
    
    if result.errors:
        print("\n出错的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            print(f"    {traceback[:200]}...")
    
    # 返回是否全部通过
    return result.wasSuccessful()


def run_specific_test(test_name):
    """运行特定的测试"""
    print(f"运行测试: {test_name}")
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_integration_test():
    """运行集成测试"""
    print("=" * 60)
    print("运行集成测试")
    print("=" * 60)
    
    # 检查Docker服务
    import requests
    try:
        response = requests.get("http://127.0.0.1:5556/docs", timeout=5)
        if response.status_code == 200:
            print("✓ XHS-Downloader API服务正常")
        else:
            print("✗ XHS-Downloader API服务异常")
            return False
    except:
        print("✗ 无法连接到XHS-Downloader API服务")
        print("  请确保Docker容器正在运行")
        return False
    
    # 测试真实笔记ID（如果需要）
    from test_config import TEST_NOTE_IDS
    print(f"\n可用的测试笔记ID:")
    for i, note_id in enumerate(TEST_NOTE_IDS, 1):
        print(f"  {i}. {note_id}")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='运行测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--integration', action='store_true', help='运行集成测试')
    parser.add_argument('--test', type=str, help='运行特定测试')
    
    args = parser.parse_args()
    
    success = True
    
    if args.integration:
        success = run_integration_test()
    elif args.test:
        success = run_specific_test(args.test)
    else:
        # 默认运行所有测试
        success = run_all_tests()
    
    # 设置退出码
    sys.exit(0 if success else 1)