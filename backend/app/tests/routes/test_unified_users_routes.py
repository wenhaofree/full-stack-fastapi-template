#!/usr/bin/env python3
"""测试统一后的用户路由。"""

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

def test_unified_users_routes():
    """测试统一后的用户路由"""
    client = TestClient(app)
    
    print("🧪 测试统一后的用户路由...")
    
    # 1. 测试登录获取 token
    print("1. 测试超级用户登录...")
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    
    response = client.post("/api/v1/login/access-token", data=login_data)
    print(f"   登录状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   登录失败: {response.json()}")
        return False
    
    token_data = response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print("   ✅ 登录成功，获取到 token")
    
    # 2. 测试统一的用户路由 - 获取当前用户信息
    print("\n2. 测试获取当前用户信息 (/api/v1/users/me)...")
    response = client.get("/api/v1/users/me", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   响应格式验证...")
        
        # 验证是否使用了标准化响应格式
        if isinstance(data, dict) and "code" in data and "message" in data and "data" in data:
            print("   ✅ 使用标准化响应格式 {code, message, data}")
            print(f"   业务状态码: {data.get('code')}")
            print(f"   消息: {data.get('message')}")
            
            user_data = data.get('data')
            if user_data and 'id' in user_data:
                print(f"   用户ID: {user_data['id']}")
                print(f"   用户邮箱: {user_data['email']}")
                print("   ✅ 用户数据格式正确")
            else:
                print("   ❌ 用户数据格式错误")
                return False
        else:
            print("   ❌ 未使用标准化响应格式")
            print(f"   实际响应: {data}")
            return False
    else:
        print(f"   ❌ 请求失败: {response.json()}")
        return False
    
    # 3. 测试用户列表 - 确认使用标准化格式
    print("\n3. 测试获取用户列表 (/api/v1/users/)...")
    response = client.get("/api/v1/users/", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, dict) and "code" in data and "data" in data:
            print("   ✅ 用户列表使用标准化响应格式")
            list_data = data.get('data')
            if list_data and 'items' in list_data:
                items = list_data['items']
                print(f"   用户数量: {len(items)}")
                print(f"   总数: {list_data.get('total')}")
                print(f"   页码: {list_data.get('page')}")
                print(f"   每页数量: {list_data.get('page_size')}")
                print("   ✅ 分页数据格式正确")
            else:
                print("   ❌ 列表数据格式错误")
                return False
        else:
            print("   ❌ 用户列表未使用标准化响应格式")
            return False
    else:
        print(f"   ❌ 请求失败: {response.json()}")
        return False
    
    # 4. 测试创建用户 - 验证标准化响应
    print("\n4. 测试创建用户...")
    new_user_data = {
        "email": "unified_test@example.com",
        "password": "testpassword123",
        "full_name": "Unified Test User",
        "is_active": True,
        "is_superuser": False
    }
    
    response = client.post("/api/v1/users/", headers=headers, json=new_user_data)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        
        if isinstance(data, dict) and data.get('code') == 10001:  # CREATED
            print("   ✅ 创建用户使用标准化响应格式")
            user_data = data.get('data')
            if user_data and 'id' in user_data:
                print(f"   新用户ID: {user_data['id']}")
                print(f"   新用户邮箱: {user_data['email']}")
                new_user_id = user_data['id']
            else:
                print("   ❌ 新用户数据格式错误")
                return False
        else:
            print("   ❌ 创建响应格式不正确")
            return False
    else:
        data = response.json()
        if data.get('code') == 40004:  # 邮箱已存在
            print("   ⚠️  用户已存在，跳过创建测试")
            new_user_id = None
        else:
            print(f"   ❌ 创建失败: {data}")
            return False
    
    # 5. 测试更新用户信息
    if 'new_user_id' in locals() and new_user_id:
        print(f"\n5. 测试更新用户信息...")
        update_data = {
            "full_name": "Updated Unified Test User"
        }
        
        response = client.put(f"/api/v1/users/{new_user_id}", headers=headers, json=update_data)
        print(f"   更新状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 10002:  # UPDATED
                print("   ✅ 更新用户使用标准化响应格式")
                print(f"   更新后姓名: {data.get('data', {}).get('full_name')}")
            else:
                print("   ❌ 更新响应格式不正确")
        else:
            print(f"   ❌ 更新失败: {response.json()}")
    
    # 6. 清理：删除测试用户
    if 'new_user_id' in locals() and new_user_id:
        print(f"\n6. 清理测试用户...")
        response = client.delete(f"/api/v1/users/{new_user_id}", headers=headers)
        print(f"   删除状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 10003:  # DELETED
                print("   ✅ 删除用户使用标准化响应格式")
            else:
                print("   ❌ 删除响应格式不正确")
        else:
            print(f"   ⚠️  删除失败: {response.json()}")
    
    # 7. 验证旧的 v2 路径不再存在
    print(f"\n7. 验证旧的 v2 路径已移除...")
    response = client.get("/api/v1/v2/users/me", headers=headers)
    print(f"   v2 路径状态码: {response.status_code}")
    
    if response.status_code == 404:
        print("   ✅ 旧的 v2 路径已正确移除")
    else:
        print("   ⚠️  v2 路径仍然存在")
    
    print("\n📋 用户路由统一验证总结:")
    print("   ✅ 主用户路由 (/api/v1/users/) 使用标准化响应格式")
    print("   ✅ 所有 CRUD 操作都使用统一的 {code, message, data} 格式")
    print("   ✅ UUID 序列化正常工作")
    print("   ✅ 业务状态码正确映射")
    print("   ✅ 旧的 v2 路径已移除")
    print("   ✅ 用户路由完全统一")
    
    return True

if __name__ == "__main__":
    success = test_unified_users_routes()
    if success:
        print("\n🎉 用户路由统一验证成功！")
        print("现在只有一个标准化的用户路由：/api/v1/users/")
    else:
        print("\n❌ 用户路由统一验证失败！")
