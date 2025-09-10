"""
测试模块初始化文件
"""

import sys
from pathlib import Path

# 将scripts目录添加到Python路径
project_root = Path(__file__).parent.parent
scripts_path = project_root / "scripts"
sys.path.insert(0, str(scripts_path))