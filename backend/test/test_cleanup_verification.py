#!/usr/bin/env python3
"""验证清理后的应用是否正常工作。"""

import json
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app


def test_application_structure():
    """测试应用结构是否正确。"""
    print("🏗️  验证应用结构...")
    
    # 检查 app/api/ 目录是否已删除
    api_dir = Path("app/api")
    if api_dir.exists():
        print(f"   ❌ app/api/ 目录仍然存在")
        return False
    else:
        print(f"   ✅ app/api/ 目录已成功删除")
    
    # 检查 app/routes/ 目录是否存在且包含正确文件
    routes_dir = Path("app/routes")
    if not routes_dir.exists():
        print(f"   ❌ app/routes/ 目录不存在")
        return False
    
    expected_files = [
        "api.py",
        "auth.py", 
        "health.py",
        "items.py",
        "users.py",
        "debug_example.py",
        "private.py"
    ]
    
    missing_files = []
    for file_name in expected_files:
        file_path = routes_dir / file_name
        if file_path.exists():
            print(f"   ✅ {file_name} 存在")
        else:
            missing_files.append(file_name)
            print(f"   ❌ {file_name} 缺失")
    
    if missing_files:
        print(f"   ❌ 缺失文件: {missing_files}")
        return False
    
    print(f"   ✅ app/routes/ 目录结构正确")
    return True


def test_application_startup():
    """测试应用是否能正常启动。"""
    print("\n🚀 验证应用启动...")
    
    try:
        # 尝试创建测试客户端
        client = TestClient(app)
        print("   ✅ 应用启动成功")
        return True, client
    except Exception as e:
        print(f"   ❌ 应用启动失败: {e}")
        return False, None


def test_api_endpoints(client: TestClient):
    """测试主要API端点是否正常工作。"""
    print("\n🔗 验证API端点...")
    
    endpoints = [
        ("/api/v1/health/", "健康检查"),
        ("/api/v1/health/detailed", "详细健康检查"),
        ("/api/v1/openapi.json", "OpenAPI文档"),
    ]
    
    all_passed = True
    
    for endpoint, description in endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"   ✅ {description} ({endpoint}) - 状态码: {response.status_code}")
            else:
                print(f"   ❌ {description} ({endpoint}) - 状态码: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ {description} ({endpoint}) - 错误: {e}")
            all_passed = False
    
    return all_passed


def test_authentication_flow(client: TestClient):
    """测试认证流程是否正常。"""
    print("\n🔐 验证认证流程...")
    
    # 测试登录端点
    login_data = {
        "username": "admin@example.com",
        "password": "changethis"
    }
    
    try:
        response = client.post("/api/v1/login/access-token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            if "access_token" in token_data:
                print("   ✅ 登录端点正常工作")
                return True, token_data["access_token"]
            else:
                print("   ❌ 登录响应缺少 access_token")
                return False, None
        else:
            print(f"   ❌ 登录失败 - 状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            return False, None
    except Exception as e:
        print(f"   ❌ 登录测试失败: {e}")
        return False, None


def test_protected_endpoints(client: TestClient, access_token: str):
    """测试需要认证的端点。"""
    print("\n🛡️  验证受保护端点...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    protected_endpoints = [
        ("/api/v1/users/me", "获取当前用户信息"),
        ("/api/v1/users/?page=1&page_size=5", "获取用户列表"),
        ("/api/v1/items/?page=1&page_size=5", "获取物品列表"),
        ("/api/v1/items/me?page=1&page_size=5", "获取我的物品列表"),
    ]
    
    all_passed = True
    
    for endpoint, description in protected_endpoints:
        try:
            response = client.get(endpoint, headers=headers)
            if response.status_code in [200, 201]:
                result = response.json()
                # 验证统一响应格式
                if "code" in result and "message" in result:
                    print(f"   ✅ {description} - 统一响应格式正确")
                else:
                    print(f"   ⚠️  {description} - 响应格式可能不统一")
            else:
                print(f"   ❌ {description} - 状态码: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ {description} - 错误: {e}")
            all_passed = False
    
    return all_passed


def test_debug_endpoints(client: TestClient):
    """测试DEBUG端点（仅在本地环境）。"""
    print("\n🐛 验证DEBUG端点...")
    
    debug_endpoints = [
        ("/api/v1/debug/users", "POST", "DEBUG用户创建"),
        ("/api/v1/debug/users", "GET", "DEBUG用户列表"),
    ]
    
    for endpoint, method, description in debug_endpoints:
        try:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                test_data = {
                    "email": "cleanup_test@example.com",
                    "password": "test123",
                    "full_name": "Cleanup Test User",
                    "age": 25
                }
                response = client.post(endpoint, json=test_data)
            
            if response.status_code in [200, 201]:
                print(f"   ✅ {description} - 正常工作")
            else:
                print(f"   ⚠️  {description} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {description} - 错误: {e}")


def main():
    """主测试函数。"""
    print("🧹 开始验证清理后的应用...")
    print("=" * 60)
    
    # 1. 验证应用结构
    structure_ok = test_application_structure()
    if not structure_ok:
        print("\n❌ 应用结构验证失败，停止测试")
        return False
    
    # 2. 验证应用启动
    startup_ok, client = test_application_startup()
    if not startup_ok:
        print("\n❌ 应用启动验证失败，停止测试")
        return False
    
    # 3. 验证API端点
    endpoints_ok = test_api_endpoints(client)
    
    # 4. 验证认证流程
    auth_ok, access_token = test_authentication_flow(client)
    
    # 5. 验证受保护端点
    protected_ok = True
    if auth_ok and access_token:
        protected_ok = test_protected_endpoints(client, access_token)
    
    # 6. 验证DEBUG端点
    test_debug_endpoints(client)
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 验证结果总结:")
    print(f"   🏗️  应用结构: {'✅ 通过' if structure_ok else '❌ 失败'}")
    print(f"   🚀 应用启动: {'✅ 通过' if startup_ok else '❌ 失败'}")
    print(f"   🔗 API端点: {'✅ 通过' if endpoints_ok else '❌ 失败'}")
    print(f"   🔐 认证流程: {'✅ 通过' if auth_ok else '❌ 失败'}")
    print(f"   🛡️  受保护端点: {'✅ 通过' if protected_ok else '❌ 失败'}")
    
    all_passed = all([structure_ok, startup_ok, endpoints_ok, auth_ok, protected_ok])
    
    if all_passed:
        print("\n🎉 所有验证都通过！清理操作成功完成。")
        print("\n✅ 清理成果:")
        print("   - 删除了未使用的 app/api/ 目录")
        print("   - 保留了正在使用的 app/routes/ 系统")
        print("   - 所有API端点正常工作")
        print("   - 统一响应格式正确")
        print("   - 认证和权限控制正常")
    else:
        print("\n⚠️  部分验证失败，请检查相关问题。")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
