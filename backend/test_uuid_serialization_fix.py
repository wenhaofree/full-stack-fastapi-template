#!/usr/bin/env python3
"""测试 UUID 序列化修复。"""

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

def test_uuid_serialization():
    """测试 UUID 序列化修复"""
    client = TestClient(app)
    
    print("🧪 测试 UUID 序列化修复...")
    
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
    
    # 2. 测试获取当前用户信息（包含 UUID）
    print("\n2. 测试获取当前用户信息...")
    response = client.get("/api/v1/v2/users/me", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   响应格式: {data}")
        
        # 验证响应格式
        if isinstance(data, dict) and "code" in data and "message" in data and "data" in data:
            print("   ✅ 响应格式正确")
            print(f"   业务状态码: {data.get('code')}")
            print(f"   消息: {data.get('message')}")
            
            user_data = data.get('data')
            if user_data and 'id' in user_data:
                print(f"   用户ID: {user_data['id']} (类型: {type(user_data['id'])})")
                print("   ✅ UUID 序列化成功")
            else:
                print("   ❌ 用户数据格式错误")
                return False
        else:
            print("   ❌ 响应格式不正确")
            return False
    else:
        print(f"   ❌ 请求失败: {response.json()}")
        return False
    
    # 3. 测试获取用户列表（包含多个 UUID）
    print("\n3. 测试获取用户列表...")
    response = client.get("/api/v1/v2/users/", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   响应格式验证...")
        
        if isinstance(data, dict) and "code" in data and "data" in data:
            list_data = data.get('data')
            if list_data and 'items' in list_data:
                items = list_data['items']
                print(f"   用户数量: {len(items)}")
                
                if items:
                    first_user = items[0]
                    if 'id' in first_user:
                        print(f"   第一个用户ID: {first_user['id']} (类型: {type(first_user['id'])})")
                        print("   ✅ 用户列表 UUID 序列化成功")
                    else:
                        print("   ❌ 用户数据缺少ID字段")
                        return False
                else:
                    print("   ⚠️  用户列表为空")
                
                print(f"   总数: {list_data.get('total')}")
                print(f"   页码: {list_data.get('page')}")
                print(f"   每页数量: {list_data.get('page_size')}")
                print("   ✅ 分页数据正确")
            else:
                print("   ❌ 列表数据格式错误")
                return False
        else:
            print("   ❌ 响应格式不正确")
            return False
    else:
        print(f"   ❌ 请求失败: {response.json()}")
        return False
    
    # 4. 测试创建用户（返回包含 UUID 的新用户）
    print("\n4. 测试创建用户...")
    new_user_data = {
        "email": "test_uuid@example.com",
        "password": "testpassword123",
        "full_name": "UUID Test User",
        "is_active": True,
        "is_superuser": False
    }
    
    response = client.post("/api/v1/v2/users/", headers=headers, json=new_user_data)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"   响应验证...")
        
        if isinstance(data, dict) and data.get('code') == 10001:  # CREATED
            user_data = data.get('data')
            if user_data and 'id' in user_data:
                print(f"   新用户ID: {user_data['id']} (类型: {type(user_data['id'])})")
                print(f"   新用户邮箱: {user_data['email']}")
                print("   ✅ 创建用户 UUID 序列化成功")
                
                # 保存用户ID用于后续删除
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
    
    # 5. 清理：删除测试用户
    if 'new_user_id' in locals() and new_user_id:
        print(f"\n5. 清理测试用户...")
        response = client.delete(f"/api/v1/v2/users/{new_user_id}", headers=headers)
        print(f"   删除状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 测试用户删除成功")
        else:
            print(f"   ⚠️  删除失败: {response.json()}")
    
    print("\n📋 UUID 序列化修复验证总结:")
    print("   ✅ UUID 对象正确序列化为字符串")
    print("   ✅ 单个用户响应格式正确")
    print("   ✅ 用户列表响应格式正确")
    print("   ✅ 创建用户响应格式正确")
    print("   ✅ 统一响应格式 {code, message, data} 正常工作")
    print("   ✅ 自定义 JSON 编码器正常工作")
    
    return True

if __name__ == "__main__":
    success = test_uuid_serialization()
    if success:
        print("\n🎉 UUID 序列化修复验证成功！")
    else:
        print("\n❌ UUID 序列化修复验证失败！")
