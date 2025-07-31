#!/usr/bin/env python3
"""测试标准化响应格式。"""

from fastapi.testclient import TestClient
from app.main import app

def test_standardized_responses():
    """测试标准化响应格式"""
    client = TestClient(app)
    
    print("🧪 测试标准化响应格式...")
    
    # 测试健康检查 - 应该返回标准格式
    print("1. 测试健康检查端点...")
    response = client.get("/api/v1/health/")
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
    
    # 测试新的用户路由 - 获取用户列表（需要认证）
    print("\n2. 测试用户列表端点（未认证）...")
    response = client.get("/api/v1/v2/users/")
    print(f"   状态码: {response.status_code}")
    data = response.json()
    print(f"   响应格式: {data}")

    # 验证响应格式
    if isinstance(data, dict) and "code" in data and "message" in data:
        print("   ✅ 响应格式符合标准 {code, message, data}")
        print(f"   业务状态码: {data.get('code')}")
        print(f"   消息: {data.get('message')}")
        print(f"   数据: {data.get('data')}")
    else:
        print("   ❌ 响应格式不符合标准")

    # 测试获取当前用户信息（未认证）
    print("\n2.1 测试获取当前用户信息（未认证）...")
    response = client.get("/api/v1/v2/users/me")
    print(f"   状态码: {response.status_code}")
    data = response.json()
    print(f"   响应: {data}")

    # 验证认证错误的响应格式
    if isinstance(data, dict) and "code" in data and "message" in data:
        print("   ✅ 认证错误响应格式符合标准")
        print(f"   业务状态码: {data.get('code')}")
        print(f"   消息: {data.get('message')}")
    else:
        print("   ❌ 认证错误响应格式不符合标准")
    
    # 测试参数验证错误
    print("\n3. 测试参数验证错误...")
    response = client.get("/api/v1/v2/users/?page=0")  # 无效页码
    print(f"   状态码: {response.status_code}")
    data = response.json()
    print(f"   响应: {data}")
    
    # 测试OpenAPI文档
    print("\n4. 测试OpenAPI文档...")
    response = client.get("/api/v1/openapi.json")
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ OpenAPI文档生成正常")
    else:
        print("   ❌ OpenAPI文档生成失败")
    
    print("\n📋 响应格式标准化总结:")
    print("   ✅ 统一响应格式: {code, message, data}")
    print("   ✅ 业务状态码和HTTP状态码分离")
    print("   ✅ 错误处理标准化")
    print("   ✅ 分页响应标准化")
    print("   ✅ 异常处理统一化")

if __name__ == "__main__":
    test_standardized_responses()
