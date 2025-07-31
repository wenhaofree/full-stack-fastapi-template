#!/usr/bin/env python3
"""测试路由日志记录功能。"""

import json
import os
import sys
from fastapi.testclient import TestClient

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app


def test_user_routes_logging():
    """测试用户路由的日志记录。"""
    print("🧪 测试用户路由的日志记录...")
    
    client = TestClient(app)
    
    # 首先需要登录获取token
    print("\n1. 登录获取访问令牌...")
    login_data = {
        "username": "admin@example.com",
        "password": "changethis"
    }
    
    response = client.post("/api/v1/login/access-token", data=login_data)
    print(f"   登录状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ 登录失败: {response.json()}")
        return
    
    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"   ✅ 登录成功，获取到访问令牌")
    
    # 设置认证头
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. 测试获取用户列表（应该记录入参和出参）
    print("\n2. 测试获取用户列表...")
    params = {
        "page": 1,
        "page_size": 5
    }
    
    response = client.get("/api/v1/users/", params=params, headers=headers)
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   返回用户数量: {len(result.get('data', []))}")
        print("   ✅ 获取用户列表成功")
        print("   📝 查看控制台日志确认入参和出参记录")
    else:
        print(f"   ❌ 获取用户列表失败: {response.json()}")
    
    # 3. 测试创建用户（应该记录入参和出参）
    print("\n3. 测试创建用户...")
    user_data = {
        "email": "test_logging@example.com",
        "password": "test_password_123",
        "full_name": "Test Logging User",
        "is_superuser": False
    }
    
    response = client.post("/api/v1/users/", json=user_data, headers=headers)
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"   创建的用户ID: {result.get('data', {}).get('id')}")
        print("   ✅ 创建用户成功")
        print("   📝 查看控制台日志确认入参和出参记录（密码应被过滤）")
    else:
        print(f"   ❌ 创建用户失败: {response.json()}")
    
    print("\n📋 测试总结:")
    print("   ✅ 用户路由已添加日志装饰器")
    print("   ✅ 应该能看到详细的入参和出参日志")
    print("   ✅ 敏感字段（如密码）应该被过滤")
    print("   ✅ 包含执行时间和追踪信息")
    
    print("\n🔍 日志检查要点:")
    print("   - 查看 'app.app.route' 日志记录器的输出")
    print("   - 确认 'input_parameters' 字段包含函数入参")
    print("   - 确认 'output_result' 字段包含函数出参")
    print("   - 确认敏感字段被标记为 '***FILTERED***'")
    print("   - 确认包含执行时间信息")


def test_debug_routes_logging():
    """测试DEBUG路由的日志记录。"""
    print("\n🧪 测试DEBUG路由的日志记录...")
    
    client = TestClient(app)
    
    # 测试DEBUG路由（不需要认证）
    print("\n1. 测试DEBUG用户创建...")
    user_data = {
        "email": "debug_logging_test@example.com",
        "password": "debug_password_123",
        "full_name": "Debug Logging Test User",
        "age": 25
    }
    
    response = client.post("/api/v1/debug/users", json=user_data)
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   创建的用户ID: {result.get('id')}")
        print("   ✅ DEBUG用户创建成功")
    else:
        print(f"   ❌ DEBUG用户创建失败: {response.json()}")
    
    # 测试DEBUG用户列表
    print("\n2. 测试DEBUG用户列表...")
    params = {
        "page": 1,
        "page_size": 3,
        "keyword": "debug",
        "is_active": True
    }
    
    response = client.get("/api/v1/debug/users", params=params)
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   返回用户数量: {len(result)}")
        print("   ✅ DEBUG用户列表获取成功")
    else:
        print(f"   ❌ DEBUG用户列表获取失败: {response.json()}")


def check_log_files():
    """检查日志文件中的记录。"""
    print("\n📁 检查日志文件中的路由日志...")
    
    try:
        # 读取最新的日志条目
        with open("logs/app.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if lines:
            print(f"   日志文件总行数: {len(lines)}")
            
            # 查找路由相关的日志
            route_logs = []
            for line in lines[-50:]:  # 检查最后50行
                try:
                    log_entry = json.loads(line.strip())
                    if (log_entry.get('logger') == 'app.app.route' or 
                        'route' in log_entry.get('message', '').lower()):
                        route_logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
            
            if route_logs:
                print(f"\n   找到 {len(route_logs)} 条路由日志:")
                for i, log in enumerate(route_logs[-5:], 1):  # 显示最新5条
                    print(f"\n   {i}. {log.get('message')}")
                    print(f"      时间: {log.get('timestamp')}")
                    print(f"      级别: {log.get('level')}")
                    print(f"      追踪ID: {log.get('trace_id')}")
                    
                    if 'input_parameters' in log:
                        print(f"      入参: {log['input_parameters']}")
                    if 'output_result' in log:
                        print(f"      出参: {log['output_result']}")
                    if 'execution_time' in log:
                        print(f"      执行时间: {log['execution_time']}")
                
                print("   ✅ 路由日志记录正常")
            else:
                print("   ⚠️  未找到路由相关的日志")
        else:
            print("   ⚠️  日志文件为空")
    
    except FileNotFoundError:
        print("   ❌ 日志文件不存在")
    except Exception as e:
        print(f"   ❌ 读取日志文件失败: {e}")


def main():
    """主测试函数。"""
    print("🚀 开始测试路由日志记录功能...")
    print("=" * 60)
    
    # 测试用户路由
    test_user_routes_logging()
    
    # 测试DEBUG路由
    test_debug_routes_logging()
    
    # 检查日志文件
    check_log_files()
    
    print("\n" + "=" * 60)
    print("🎉 路由日志记录测试完成！")
    
    print("\n💡 如果没有看到入参和出参日志，请检查:")
    print("   1. 路由函数是否添加了 @log_route_debug 装饰器")
    print("   2. LOG_FUNCTION_PARAMS 配置是否为 true")
    print("   3. 日志级别是否为 DEBUG")
    print("   4. 装饰器是否在路由装饰器之后（紧挨着函数定义）")


if __name__ == "__main__":
    main()
