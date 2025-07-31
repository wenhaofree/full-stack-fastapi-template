#!/usr/bin/env python3
"""简单测试路由日志装饰器。"""

import asyncio
import logging
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.logger_config import setup_professional_logging
from app.core.route_logging import log_route_debug


async def test_decorator_directly():
    """直接测试装饰器功能。"""
    print("🧪 直接测试路由日志装饰器...")
    
    # 设置日志
    setup_professional_logging()
    
    # 创建一个测试函数
    @log_route_debug(include_args=True, include_result=True, include_timing=True)
    async def test_function(user_id: int, name: str, email: str = "test@example.com"):
        """测试函数。"""
        print(f"   执行测试函数: user_id={user_id}, name={name}, email={email}")
        
        # 模拟一些处理
        await asyncio.sleep(0.1)
        
        # 返回结果
        return {
            "id": user_id,
            "name": name,
            "email": email,
            "status": "success",
            "password": "secret123"  # 这个应该被过滤
        }
    
    print("\n1. 调用测试函数...")
    result = await test_function(123, "Test User", "user@example.com")
    print(f"   函数返回结果: {result}")
    
    print("\n2. 测试带异常的情况...")
    
    @log_route_debug(include_args=True, include_result=True, include_timing=True)
    async def test_error_function(value: int):
        """测试异常函数。"""
        if value < 0:
            raise ValueError("值不能为负数")
        return {"value": value, "doubled": value * 2}
    
    try:
        await test_error_function(-1)
    except ValueError as e:
        print(f"   捕获到预期异常: {e}")
    
    print("\n✅ 装饰器直接测试完成")


def test_with_fastapi():
    """使用FastAPI测试。"""
    print("\n🌐 使用FastAPI测试路由日志...")
    
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # 测试DEBUG路由
    print("\n1. 测试DEBUG路由...")
    user_data = {
        "email": "simple_test@example.com",
        "password": "test_password_123",
        "full_name": "Simple Test User",
        "age": 30
    }
    
    response = client.post("/api/v1/debug/users", json=user_data)
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 200:
        print("   ✅ DEBUG路由调用成功")
    else:
        print(f"   ❌ DEBUG路由调用失败: {response.json()}")
    
    # 测试用户路由
    print("\n2. 测试用户路由（需要认证）...")
    
    # 先登录
    login_data = {
        "username": "admin@example.com",
        "password": "changethis"
    }
    
    login_response = client.post("/api/v1/login/access-token", data=login_data)
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 测试获取用户列表
        response = client.get("/api/v1/users/?page=1&page_size=3", headers=headers)
        print(f"   状态码: {response.status_code}")
        print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
        
        if response.status_code == 200:
            print("   ✅ 用户路由调用成功")
        else:
            print(f"   ❌ 用户路由调用失败: {response.json()}")
    else:
        print("   ❌ 登录失败，跳过用户路由测试")


def check_logs():
    """检查日志输出。"""
    print("\n📋 检查日志输出...")
    
    # 检查控制台日志（应该能看到彩色输出）
    print("   控制台日志应该显示:")
    print("   - 路由函数开始: xxx")
    print("   - 路由函数完成: xxx")
    print("   - 包含 input_parameters 和 output_result")
    print("   - 敏感字段被标记为 ***FILTERED***")
    
    # 检查文件日志
    try:
        with open("logs/app.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        route_logs = []
        for line in lines[-20:]:  # 检查最后20行
            if '"logger": "app.route"' in line:
                route_logs.append(line.strip())
        
        if route_logs:
            print(f"\n   在日志文件中找到 {len(route_logs)} 条路由日志:")
            for i, log in enumerate(route_logs[-3:], 1):  # 显示最新3条
                print(f"   {i}. {log[:100]}...")
            print("   ✅ 文件日志记录正常")
        else:
            print("   ⚠️  在日志文件中未找到路由日志")
    
    except Exception as e:
        print(f"   ❌ 检查日志文件失败: {e}")


async def main():
    """主函数。"""
    print("🚀 开始简单路由日志测试...")
    print("=" * 50)
    
    # 直接测试装饰器
    await test_decorator_directly()
    
    # 使用FastAPI测试
    test_with_fastapi()
    
    # 检查日志
    check_logs()
    
    print("\n" + "=" * 50)
    print("🎉 简单路由日志测试完成！")
    
    print("\n💡 如果看到路由日志，说明装饰器工作正常")
    print("💡 如果没有看到，可能需要检查:")
    print("   1. 装饰器导入是否正确")
    print("   2. 日志级别配置")
    print("   3. 装饰器顺序")


if __name__ == "__main__":
    asyncio.run(main())
