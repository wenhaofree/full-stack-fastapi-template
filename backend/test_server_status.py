#!/usr/bin/env python3
"""测试服务器状态。"""

import requests
import time

def test_server():
    """测试服务器是否正常响应。"""
    print("🧪 测试服务器状态...")
    
    try:
        # 测试健康检查接口
        print("1. 测试健康检查接口...")
        response = requests.get("http://127.0.0.1:8000/api/v1/health/", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        print("   ✅ 服务器正常响应")
        
        # 测试DEBUG接口
        print("\n2. 测试DEBUG接口...")
        user_data = {
            "email": "server_test@example.com",
            "password": "test123",
            "full_name": "Server Test User",
            "age": 30
        }
        
        response = requests.post("http://127.0.0.1:8000/api/v1/debug/users", json=user_data, timeout=5)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   用户ID: {result.get('id')}")
            print("   ✅ DEBUG接口正常")
        else:
            print(f"   响应: {response.text}")
        
    except requests.exceptions.ConnectRefused:
        print("   ❌ 服务器连接被拒绝，可能服务器未启动")
    except requests.exceptions.Timeout:
        print("   ❌ 请求超时，服务器可能卡住了")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")

if __name__ == "__main__":
    test_server()
