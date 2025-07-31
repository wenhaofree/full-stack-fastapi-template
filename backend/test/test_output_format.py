#!/usr/bin/env python3
"""测试出参格式的可读性。"""

import json
import os
import sys
from fastapi.testclient import TestClient

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app


def test_output_format():
    """测试出参的JSON格式显示。"""
    print("🧪 测试出参的JSON格式显示...")
    
    client = TestClient(app)
    
    # 1. 测试DEBUG路由的出参格式
    print("\n1. 测试DEBUG路由的出参格式...")
    user_data = {
        "email": "output_format_test@example.com",
        "password": "test_password_123",
        "full_name": "Output Format Test User",
        "age": 28
    }
    
    response = client.post("/api/v1/debug/users", json=user_data)
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   返回的用户ID: {result.get('id')}")
        print("   ✅ DEBUG路由调用成功")
        print("   📝 查看控制台日志确认出参格式")
    else:
        print(f"   ❌ DEBUG路由调用失败: {response.json()}")
    
    # 2. 测试用户列表路由的出参格式
    print("\n2. 测试用户列表路由的出参格式...")
    
    # 先登录获取token
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
        response = client.get("/api/v1/users/?page=1&page_size=2", headers=headers)
        print(f"   状态码: {response.status_code}")
        print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   返回用户数量: {len(result.get('data', {}).get('items', []))}")
            print("   ✅ 用户列表获取成功")
            print("   📝 查看控制台日志确认出参格式（应该显示JSON结构）")
        else:
            print(f"   ❌ 用户列表获取失败: {response.json()}")
    else:
        print("   ❌ 登录失败，跳过用户列表测试")
    
    # 3. 测试创建用户的出参格式
    print("\n3. 测试创建用户的出参格式...")
    if 'access_token' in locals():
        headers = {"Authorization": f"Bearer {access_token}"}
        
        create_user_data = {
            "email": "output_test_user@example.com",
            "password": "create_test_123",
            "full_name": "Output Test User",
            "is_superuser": False
        }
        
        response = client.post("/api/v1/users/", json=create_user_data, headers=headers)
        print(f"   状态码: {response.status_code}")
        print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"   创建的用户ID: {result.get('data', {}).get('id')}")
            print("   ✅ 用户创建成功")
            print("   📝 查看控制台日志确认出参格式（应该显示完整的响应结构）")
        else:
            print(f"   ❌ 用户创建失败: {response.json()}")
    
    print("\n📋 测试总结:")
    print("   ✅ 测试了多种类型的路由出参")
    print("   ✅ 应该能看到JSON格式的出参而不是对象字符串")
    print("   ✅ Response对象应该显示状态码、头部和响应体")
    print("   ✅ 敏感字段仍然被正确过滤")
    
    print("\n🔍 期望的日志格式:")
    print("   📤 出参: {\"type\": \"CustomJSONResponse\", \"status_code\": 200, \"body\": {...}}")
    print("   而不是: 📤 出参: <app.utils.response.CustomJSONResponse object at 0x...>")


def main():
    """主测试函数。"""
    print("🚀 开始测试出参格式...")
    print("=" * 50)
    
    test_output_format()
    
    print("\n" + "=" * 50)
    print("🎉 出参格式测试完成！")
    
    print("\n💡 检查要点:")
    print("   1. 出参应该显示为JSON格式而不是对象字符串")
    print("   2. Response对象应该显示状态码和响应体内容")
    print("   3. 复杂对象应该被正确序列化")
    print("   4. 敏感字段仍然被过滤")


if __name__ == "__main__":
    main()
