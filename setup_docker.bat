@echo off
echo ====================================
echo XHS-Downloader Docker 设置脚本
echo ====================================
echo.

echo 检查Docker服务状态...
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker服务未运行！
    echo.
    echo 请先启动Docker Desktop，然后重新运行此脚本。
    echo.
    pause
    exit /b 1
)

echo [✓] Docker服务正在运行
echo.

echo 步骤1: 拉取XHS-Downloader镜像...
docker pull joeanamier/xhs-downloader
if %errorlevel% neq 0 (
    echo [错误] 镜像拉取失败！
    pause
    exit /b 1
)
echo [✓] 镜像拉取成功
echo.

echo 步骤2: 检查是否存在旧容器...
docker stop xhs-api > nul 2>&1
docker rm xhs-api > nul 2>&1
echo [✓] 清理完成
echo.

echo 步骤3: 启动XHS-Downloader API服务...
docker run --name xhs-api -d -p 5556:5556 -v xhs_downloader_volume:/app/Volume joeanamier/xhs-downloader python main.py api
if %errorlevel% neq 0 (
    echo [错误] 容器启动失败！
    pause
    exit /b 1
)
echo [✓] API服务已启动
echo.

echo 等待服务启动...
timeout /t 5 > nul

echo 步骤4: 验证服务状态...
curl -s http://127.0.0.1:5556/docs > nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 服务可能还在启动中，请稍后手动验证
    echo 访问: http://127.0.0.1:5556/docs
) else (
    echo [✓] 服务运行正常！
    echo.
    echo API文档地址: http://127.0.0.1:5556/docs
)

echo.
echo ====================================
echo 设置完成！
echo ====================================
echo.
echo 有用的Docker命令：
echo   查看容器状态: docker ps
echo   查看容器日志: docker logs xhs-api
echo   停止容器: docker stop xhs-api
echo   启动容器: docker start xhs-api
echo   重启容器: docker restart xhs-api
echo.
pause