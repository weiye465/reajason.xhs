#!/usr/bin/env python3
"""
HTML转PNG图片工具
使用playwright库将HTML文件转换为PNG图片
"""

import asyncio
import os
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("请先安装playwright: pip install playwright")
    print("然后安装浏览器: playwright install chromium")
    exit(1)

async def html_to_png(html_file, output_file):
    """
    将HTML文件转换为PNG图片

    Args:
        html_file: HTML文件路径
        output_file: 输出PNG文件路径
    """
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)

        # 创建新页面，设置一个较大的初始viewport
        page = await browser.new_page(
            viewport={'width': 1200, 'height': 2000},
            device_scale_factor=2  # 2倍分辨率，确保图片清晰
        )

        # 加载HTML文件
        file_url = f"file:///{os.path.abspath(html_file).replace(os.sep, '/')}"
        await page.goto(file_url)

        # 等待页面完全加载
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(1000)  # 额外等待1秒确保渲染完成

        # 获取container元素
        container = await page.query_selector('.container')

        if container:
            # 获取container的边界框
            bounding_box = await container.bounding_box()

            if bounding_box:
                # 截取container元素
                await container.screenshot(
                    path=output_file,
                    type='png'
                )
                print(f"✅ 已生成: {output_file} (尺寸: {bounding_box['width']}x{bounding_box['height']})")
            else:
                print(f"❌ 无法获取container边界: {html_file}")
        else:
            print(f"❌ 未找到container元素: {html_file}")
            # 降级处理：截取整个页面
            await page.screenshot(
                path=output_file,
                full_page=True,
                type='png'
            )
            print(f"⚠️ 已截取整个页面: {output_file}")

        # 关闭浏览器
        await browser.close()

async def main():
    """主函数：转换所有HTML文件"""

    # 获取当前目录
    current_dir = Path(__file__).parent

    # 定义要转换的HTML文件
    html_files = [
        ("封面.html", "封面.png"),
        ("正文图片1_标准版.html", "正文图片1_标准版.png"),
        ("正文图片2_标准版.html", "正文图片2_标准版.png"),
        ("正文图片3_标准版.html", "正文图片3_标准版.png"),
        ("正文图片4_标准版.html", "正文图片4_标准版.png")
    ]

    print("🚀 开始转换HTML到PNG...")
    print("-" * 50)

    # 转换每个文件
    for html_file, png_file in html_files:
        html_path = current_dir / html_file
        png_path = current_dir / png_file

        if html_path.exists():
            print(f"📄 正在转换: {html_file}")
            try:
                await html_to_png(html_path, png_path)
            except Exception as e:
                print(f"❌ 转换失败 {html_file}: {e}")
        else:
            print(f"⚠️ 文件不存在: {html_file}")

    print("-" * 50)
    print("✨ 转换完成！")

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())