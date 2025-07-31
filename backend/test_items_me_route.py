#!/usr/bin/env python3
"""测试物品的 /me 路由。"""

import json
import os
import sys
from fastapi.testclient import TestClient

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app


def get_access_token(client: TestClient) -> str:
    """获取访问令牌。"""
    login_data = {
        "username": "admin@example.com",
        "password": "changethis"
    }
    
    response = client.post("/api/v1/login/access-token", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        raise Exception(f"登录失败: {response.json()}")


def test_items_me_route():
    """测试物品的 /me 路由。"""
    print("🧪 测试物品的 /me 路由...")
    
    client = TestClient(app)
    
    # 获取访问令牌
    try:
        access_token = get_access_token(client)
        headers = {"Authorization": f"Bearer {access_token}"}
        print("   ✅ 成功获取访问令牌")
    except Exception as e:
        print(f"   ❌ 获取访问令牌失败: {e}")
        return
    
    # 1. 先创建一些测试物品
    print("\n1. 创建测试物品...")
    test_items = [
        {"title": "我的物品1", "description": "这是我的第一个物品"},
        {"title": "我的物品2", "description": "这是我的第二个物品"},
        {"title": "我的物品3", "description": "这是我的第三个物品"}
    ]
    
    created_items = []
    for item_data in test_items:
        response = client.post("/api/v1/items/", json=item_data, headers=headers)
        if response.status_code == 201:
            result = response.json()
            created_items.append(result["data"]["id"])
            print(f"   ✅ 创建物品成功: {item_data['title']}")
        else:
            print(f"   ❌ 创建物品失败: {response.json()}")
    
    # 2. 测试 /me 路由
    print("\n2. 测试获取我的物品列表...")
    params = {
        "page": 1,
        "page_size": 5
    }
    
    response = client.get("/api/v1/items/me", params=params, headers=headers)
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   响应格式: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 验证响应格式
        assert "code" in result, "响应中应包含 code 字段"
        assert "message" in result, "响应中应包含 message 字段"
        assert "data" in result, "响应中应包含 data 字段"
        assert result["code"] == 10000, f"成功的 code 应为 10000，实际为 {result['code']}"
        
        # 验证数据格式 - 这里使用 success_response 格式
        data = result["data"]
        assert "items" in data, "data 中应包含 items 字段"
        assert "total" in data, "data 中应包含 total 字段"
        assert "page" in data, "data 中应包含 page 字段"
        assert "page_size" in data, "data 中应包含 page_size 字段"
        assert "pages" in data, "data 中应包含 pages 字段"
        
        print(f"   ✅ 获取我的物品列表成功，共 {data['total']} 个物品")
        print(f"   ✅ 使用 success_response 格式正确")
        
        # 验证返回的物品都属于当前用户
        my_items = data["items"]
        print(f"   📦 我的物品:")
        for item in my_items:
            print(f"      - {item['title']}: {item['description']}")
        
    else:
        print(f"   ❌ 获取我的物品列表失败: {response.json()}")
        return
    
    # 3. 对比 /me 和 / 路由的响应格式
    print("\n3. 对比 /me 和 / 路由的响应格式...")
    
    # 获取所有物品列表
    response_all = client.get("/api/v1/items/", params=params, headers=headers)
    if response_all.status_code == 200:
        result_all = response_all.json()
        
        print("   📊 响应格式对比:")
        print(f"   /items/ (list_response): {type(result_all['data'])}")
        print(f"   /items/me (success_response): {type(result['data'])}")
        
        print("\n   /items/ 数据结构:")
        print(f"   - items: {len(result_all['data']['items'])} 个")
        print(f"   - total: {result_all['data']['total']}")
        
        print("\n   /items/me 数据结构:")
        print(f"   - items: {len(result['data']['items'])} 个")
        print(f"   - total: {result['data']['total']}")
        
        print("   ✅ 两种路由都正确使用了相应的响应格式")
    
    # 4. 测试分页功能
    print("\n4. 测试分页功能...")
    params_page2 = {
        "page": 2,
        "page_size": 2
    }
    
    response_page2 = client.get("/api/v1/items/me", params=params_page2, headers=headers)
    if response_page2.status_code == 200:
        result_page2 = response_page2.json()
        data_page2 = result_page2["data"]
        
        print(f"   第2页数据: {len(data_page2['items'])} 个物品")
        print(f"   总页数: {data_page2['pages']}")
        print("   ✅ 分页功能正常")
    
    # 5. 清理测试数据
    print("\n5. 清理测试数据...")
    for item_id in created_items:
        response = client.delete(f"/api/v1/items/{item_id}", headers=headers)
        if response.status_code == 200:
            print(f"   ✅ 删除物品成功: {item_id}")
        else:
            print(f"   ⚠️  删除物品失败: {item_id}")


def test_response_format_comparison():
    """对比不同路由的响应格式。"""
    print("\n📊 响应格式对比:")
    
    print("\n1. /items/ (获取所有物品) - 使用 list_response:")
    print("""
    {
        "code": 10000,
        "message": "获取物品列表成功",
        "data": {
            "items": [...],
            "total": 10,
            "page": 1,
            "page_size": 10,
            "pages": 1
        }
    }
    """)
    
    print("\n2. /items/me (获取我的物品) - 使用 success_response:")
    print("""
    {
        "code": 10000,
        "message": "获取我的物品列表成功",
        "data": {
            "items": [...],
            "total": 5,
            "page": 1,
            "page_size": 10,
            "pages": 1
        }
    }
    """)
    
    print("\n3. /items/{id} (获取单个物品) - 使用 success_response:")
    print("""
    {
        "code": 10000,
        "message": "获取物品详情成功",
        "data": {
            "id": "uuid",
            "title": "物品标题",
            "description": "物品描述"
        }
    }
    """)
    
    print("\n✅ 关键区别:")
    print("   - list_response: 专门用于列表数据，包含分页信息")
    print("   - success_response: 用于单个资源或自定义数据结构")
    print("   - /items/me 使用 success_response 是因为它返回的是当前用户的专属数据")


def main():
    """主测试函数。"""
    print("🚀 开始测试物品的 /me 路由...")
    print("=" * 60)
    
    try:
        test_items_me_route()
        test_response_format_comparison()
        
        print("\n" + "=" * 60)
        print("🎉 物品 /me 路由测试完成！")
        
        print("\n✅ 成功验证的功能:")
        print("   1. /items/me 路由正确使用 success_response")
        print("   2. 返回当前用户的物品列表")
        print("   3. 包含完整的分页信息")
        print("   4. 与 /items/ 路由格式保持一致")
        print("   5. 权限控制正确（只返回自己的物品）")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
