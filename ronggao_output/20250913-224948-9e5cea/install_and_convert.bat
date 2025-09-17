@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    HTML转PNG图片 - 自动安装和转换
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)
echo ✅ Python已安装

echo.
echo [2/3] 安装必要的依赖包...
echo 正在安装playwright...
pip install playwright -q
if %errorlevel% neq 0 (
    echo ❌ playwright安装失败
    pause
    exit /b 1
)

echo 正在安装Chromium浏览器...
playwright install chromium
if %errorlevel% neq 0 (
    echo ❌ Chromium安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

echo.
echo [3/3] 开始转换HTML文件为PNG...
python html_to_png.py
if %errorlevel% neq 0 (
    echo ❌ 转换过程出错
    pause
    exit /b 1
)

echo.
echo ========================================
echo    ✨ 所有文件转换完成！
echo    生成的PNG文件：
echo    - 封面.png
echo    - 正文图片1.png
echo    - 正文图片2.png
echo ========================================
echo.
pause