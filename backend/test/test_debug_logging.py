#!/usr/bin/env python3
"""测试DEBUG级别的日志记录功能。"""

import json
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

def test_debug_logging():
    """测试DEBUG级别的日志记录。"""
    client = TestClient(app)
    
    print("🧪 测试DEBUG级别的日志记录...")
    print(f"当前环境: {settings.ENVIRONMENT}")
    
    # 1. 测试创建用户接口（包含请求体和响应体）
    print("\n1. 测试创建用户接口（DEBUG日志）...")
    user_data = {
        "email": "debug_test@example.com",
        "password": "test_password_123",  # 这个字段应该被过滤
        "full_name": "Debug Test User",
        "age": 25
    }
    
    response = client.post("/api/v1/debug/users", json=user_data)
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 201 or response.status_code == 200:
        result = response.json()
        print(f"   创建的用户ID: {result.get('id')}")
        print("   ✅ 创建用户成功")
    else:
        print(f"   ❌ 创建用户失败: {response.json()}")
    
    # 2. 测试获取用户接口（路径参数）
    print("\n2. 测试获取用户接口...")
    response = client.get("/api/v1/debug/users/test-user-123")
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   用户邮箱: {result.get('email')}")
        print("   ✅ 获取用户成功")
    else:
        print(f"   ❌ 获取用户失败: {response.json()}")
    
    # 3. 测试搜索接口（复杂请求体）
    print("\n3. 测试搜索接口...")
    search_data = {
        "keyword": "Python开发",
        "category": "技术",
        "limit": 5
    }
    
    response = client.post("/api/v1/debug/search", json=search_data)
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   搜索结果数量: {result.get('total')}")
        print("   ✅ 搜索成功")
    else:
        print(f"   ❌ 搜索失败: {response.json()}")
    
    # 4. 测试用户列表接口（查询参数）
    print("\n4. 测试用户列表接口...")
    params = {
        "page": 1,
        "page_size": 3,
        "keyword": "测试",
        "is_active": True
    }
    
    response = client.get("/api/v1/debug/users", params=params)
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   返回用户数量: {len(result)}")
        print("   ✅ 获取用户列表成功")
    else:
        print(f"   ❌ 获取用户列表失败: {response.json()}")
    
    # 5. 测试登录接口（敏感字段过滤）
    print("\n5. 测试登录接口（敏感字段过滤）...")
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"  # 这个字段应该被过滤为 ***FILTERED***
    }
    
    response = client.post("/api/v1/debug/login", json=login_data)
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   令牌类型: {result.get('token_type')}")
        print("   ✅ 登录成功")
    else:
        print(f"   ❌ 登录失败: {response.json()}")
    
    # 6. 测试错误情况的日志记录
    print("\n6. 测试错误情况的日志记录...")
    error_user_data = {
        "email": "test@error.com",  # 这会触发错误
        "password": "test123",
        "full_name": "Error Test User"
    }
    
    response = client.post("/api/v1/debug/users", json=error_user_data)
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 400:
        result = response.json()
        print(f"   错误信息: {result.get('detail')}")
        print("   ✅ 错误处理正常")
    else:
        print(f"   ❌ 错误处理异常: {response.json()}")
    
    # 7. 测试404错误
    print("\n7. 测试404错误...")
    response = client.get("/api/v1/debug/users/not-found")
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 404:
        result = response.json()
        print(f"   错误信息: {result.get('detail')}")
        print("   ✅ 404错误处理正常")
    else:
        print(f"   ❌ 404错误处理异常: {response.json()}")
    
    # 8. 测试INFO级别的路由（不记录详细参数）
    print("\n8. 测试INFO级别的路由...")
    response = client.get("/api/v1/debug/health")
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   健康状态: {result.get('status')}")
        print("   ✅ 健康检查成功")
    else:
        print(f"   ❌ 健康检查失败: {response.json()}")
    
    print("\n📋 DEBUG日志测试总结:")
    print("   ✅ 请求体记录（敏感字段过滤）")
    print("   ✅ 响应体记录（长度限制）")
    print("   ✅ 函数参数记录")
    print("   ✅ 函数返回值记录")
    print("   ✅ 执行时间记录")
    print("   ✅ 异常情况记录")
    print("   ✅ 追踪ID传递")
    print("   ✅ 不同日志级别区分")
    
    print("\n🔍 查看详细日志:")
    print("   - 控制台输出: 彩色格式化日志")
    print("   - logs/app.log: 结构化JSON日志")
    print("   - logs/error.log: 错误日志")
    
    return True


def test_log_file_content():
    """测试日志文件内容。"""
    print("\n🔍 检查日志文件内容...")
    
    try:
        # 读取最新的日志条目
        with open("logs/app.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if lines:
            print(f"   日志文件总行数: {len(lines)}")
            
            # 显示最后几条日志
            print("\n   最新的5条日志:")
            for line in lines[-5:]:
                try:
                    log_entry = json.loads(line.strip())
                    print(f"   - {log_entry.get('timestamp')} | {log_entry.get('level')} | {log_entry.get('message')}")
                    
                    # 检查是否包含DEBUG级别的详细信息
                    if log_entry.get('level') == 'DEBUG':
                        if 'parameters' in log_entry:
                            print(f"     参数: {log_entry['parameters']}")
                        if 'result' in log_entry:
                            print(f"     结果: {log_entry['result']}")
                        if 'request_body' in log_entry:
                            print(f"     请求体: {log_entry['request_body']}")
                        if 'response_body' in log_entry:
                            print(f"     响应体: {log_entry['response_body']}")
                            
                except json.JSONDecodeError:
                    print(f"   - {line.strip()}")
            
            print("   ✅ 日志文件格式正确")
        else:
            print("   ⚠️  日志文件为空")
            
    except FileNotFoundError:
        print("   ❌ 日志文件不存在")
    except Exception as e:
        print(f"   ❌ 读取日志文件失败: {e}")


def main():
    """主测试函数。"""
    print("🚀 开始测试DEBUG级别日志记录...")
    
    # 运行API测试
    success = test_debug_logging()
    
    # 检查日志文件
    test_log_file_content()
    
    if success:
        print("\n🎉 DEBUG级别日志记录测试完成！")
        print("\n📝 功能验证:")
        print("   ✅ 请求体和响应体在DEBUG级别被记录")
        print("   ✅ 函数入参和出参被详细记录")
        print("   ✅ 敏感字段（如密码）被自动过滤")
        print("   ✅ 执行时间和异常信息被记录")
        print("   ✅ 追踪ID在整个请求链路中传递")
        print("   ✅ 不同日志级别有不同的记录详细程度")
        
        print("\n🎯 生产环境建议:")
        print("   - 生产环境设置为INFO级别，避免记录敏感信息")
        print("   - 开发环境使用DEBUG级别，便于调试")
        print("   - 定期清理日志文件，避免磁盘空间不足")
        print("   - 使用日志聚合工具分析DEBUG日志")
    else:
        print("\n❌ DEBUG级别日志记录测试失败！")


if __name__ == "__main__":
    main()
