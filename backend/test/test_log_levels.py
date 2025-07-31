#!/usr/bin/env python3
"""测试不同日志级别的配置。"""

import os
import sys
import time
from fastapi.testclient import TestClient

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.logger import get_logger, get_structured_logger
from app.main import app


def test_log_level_configuration():
    """测试日志级别配置。"""
    print("🧪 测试日志级别配置...")
    print(f"当前环境: {settings.ENVIRONMENT}")
    print(f"配置的日志级别: {settings.LOG_LEVEL}")
    print(f"请求详细日志: {settings.LOG_REQUEST_DETAILS}")
    print(f"函数参数日志: {settings.LOG_FUNCTION_PARAMS}")
    
    # 测试不同级别的日志
    logger = get_logger("test.levels")
    struct_logger = get_structured_logger("test.levels.structured")
    
    print("\n📝 测试各个日志级别的输出...")
    
    # DEBUG级别
    logger.debug("这是DEBUG级别的日志")
    struct_logger.debug("这是结构化DEBUG日志", test_param="debug_value", user_id="test_user")
    
    # INFO级别
    logger.info("这是INFO级别的日志")
    struct_logger.info("这是结构化INFO日志", operation="test_info", status="success")
    
    # WARNING级别
    logger.warning("这是WARNING级别的日志")
    struct_logger.warning("这是结构化WARNING日志", warning_type="test_warning", severity="medium")
    
    # ERROR级别
    logger.error("这是ERROR级别的日志")
    struct_logger.error("这是结构化ERROR日志", error_type="test_error", error_code="E001")
    
    # CRITICAL级别
    logger.critical("这是CRITICAL级别的日志")
    struct_logger.critical("这是结构化CRITICAL日志", critical_issue="system_failure", impact="high")
    
    print("   ✅ 日志级别测试完成")


def test_api_with_different_log_levels():
    """测试API在不同日志级别下的行为。"""
    print("\n🌐 测试API在不同日志级别下的行为...")
    
    client = TestClient(app)
    
    # 测试健康检查
    print("\n1. 测试健康检查接口...")
    response = client.get("/api/v1/health/")
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    # 测试DEBUG路由（如果存在）
    if settings.ENVIRONMENT == "local":
        print("\n2. 测试DEBUG路由...")
        
        # 测试创建用户
        user_data = {
            "email": "log_level_test@example.com",
            "password": "test_password_123",
            "full_name": "Log Level Test User",
            "age": 30
        }
        
        response = client.post("/api/v1/debug/users", json=user_data)
        print(f"   创建用户状态码: {response.status_code}")
        print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
        
        # 测试登录
        login_data = {
            "email": "admin@example.com",
            "password": "admin123"
        }
        
        response = client.post("/api/v1/debug/login", json=login_data)
        print(f"   登录状态码: {response.status_code}")
        print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
        
        # 测试健康检查（INFO级别）
        response = client.get("/api/v1/debug/health")
        print(f"   DEBUG健康检查状态码: {response.status_code}")
        print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    print("   ✅ API日志级别测试完成")


def test_log_level_filtering():
    """测试日志级别过滤效果。"""
    print("\n🔍 测试日志级别过滤效果...")
    
    # 获取当前配置的日志级别
    current_level = settings.LOG_LEVEL
    print(f"当前日志级别: {current_level}")
    
    # 日志级别优先级
    log_levels = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50
    }
    
    current_level_value = log_levels.get(current_level, 20)
    
    print(f"\n根据当前日志级别 {current_level}，应该显示的日志:")
    for level, value in log_levels.items():
        if value >= current_level_value:
            print(f"   ✅ {level} 级别日志应该显示")
        else:
            print(f"   ❌ {level} 级别日志应该被过滤")
    
    print("\n实际测试各级别日志输出:")
    logger = get_logger("test.filtering")
    
    print("   发送DEBUG日志...")
    logger.debug("DEBUG级别测试日志")
    
    print("   发送INFO日志...")
    logger.info("INFO级别测试日志")
    
    print("   发送WARNING日志...")
    logger.warning("WARNING级别测试日志")
    
    print("   发送ERROR日志...")
    logger.error("ERROR级别测试日志")
    
    print("   发送CRITICAL日志...")
    logger.critical("CRITICAL级别测试日志")
    
    print("   ✅ 日志级别过滤测试完成")


def test_configuration_impact():
    """测试配置对日志行为的影响。"""
    print("\n⚙️  测试配置对日志行为的影响...")
    
    print(f"LOG_REQUEST_DETAILS = {settings.LOG_REQUEST_DETAILS}")
    if settings.LOG_REQUEST_DETAILS:
        print("   ✅ 应该记录请求体和响应体详细信息")
    else:
        print("   ❌ 不会记录请求体和响应体详细信息")
    
    print(f"LOG_FUNCTION_PARAMS = {settings.LOG_FUNCTION_PARAMS}")
    if settings.LOG_FUNCTION_PARAMS:
        print("   ✅ 应该记录函数参数和返回值")
    else:
        print("   ❌ 不会记录函数参数和返回值")
    
    # 测试路由装饰器的行为
    if settings.ENVIRONMENT == "local":
        print("\n测试路由装饰器配置影响...")
        client = TestClient(app)
        
        # 调用一个DEBUG路由来观察日志行为
        response = client.get("/api/v1/debug/health")
        print(f"   DEBUG路由调用状态码: {response.status_code}")
        print("   查看控制台输出以确认参数记录行为")
    
    print("   ✅ 配置影响测试完成")


def show_log_level_examples():
    """展示不同日志级别的使用示例。"""
    print("\n📚 日志级别使用示例:")
    
    print("\n🔵 DEBUG级别 - 详细的调试信息:")
    print("   - 函数参数和返回值")
    print("   - 请求体和响应体内容")
    print("   - 详细的执行流程")
    print("   - 变量状态和中间结果")
    
    print("\n🟢 INFO级别 - 重要的业务事件:")
    print("   - 用户登录/登出")
    print("   - 重要操作的开始和完成")
    print("   - 系统状态变化")
    print("   - 业务流程关键节点")
    
    print("\n🟡 WARNING级别 - 潜在问题:")
    print("   - 性能警告")
    print("   - 配置问题")
    print("   - 不推荐的使用方式")
    print("   - 资源使用警告")
    
    print("\n🔴 ERROR级别 - 错误情况:")
    print("   - 业务逻辑错误")
    print("   - 外部服务调用失败")
    print("   - 数据验证失败")
    print("   - 可恢复的系统错误")
    
    print("\n🚨 CRITICAL级别 - 严重错误:")
    print("   - 系统崩溃")
    print("   - 数据库连接失败")
    print("   - 安全问题")
    print("   - 服务不可用")


def main():
    """主测试函数。"""
    print("🚀 开始测试日志级别配置...")
    print("=" * 60)
    
    # 显示使用示例
    show_log_level_examples()
    
    # 测试配置
    test_log_level_configuration()
    
    # 测试日志级别过滤
    test_log_level_filtering()
    
    # 测试API行为
    test_api_with_different_log_levels()
    
    # 测试配置影响
    test_configuration_impact()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"   当前环境: {settings.ENVIRONMENT}")
    print(f"   日志级别: {settings.LOG_LEVEL}")
    print(f"   请求详细日志: {'启用' if settings.LOG_REQUEST_DETAILS else '禁用'}")
    print(f"   函数参数日志: {'启用' if settings.LOG_FUNCTION_PARAMS else '禁用'}")
    
    print("\n🎯 配置建议:")
    if settings.ENVIRONMENT == "local":
        print("   开发环境建议:")
        print("   - LOG_LEVEL=DEBUG (查看所有日志)")
        print("   - LOG_REQUEST_DETAILS=true (调试API)")
        print("   - LOG_FUNCTION_PARAMS=true (调试函数)")
    elif settings.ENVIRONMENT == "production":
        print("   生产环境建议:")
        print("   - LOG_LEVEL=INFO 或 WARNING (减少日志量)")
        print("   - LOG_REQUEST_DETAILS=false (保护隐私)")
        print("   - LOG_FUNCTION_PARAMS=false (提高性能)")
    else:
        print("   测试环境建议:")
        print("   - LOG_LEVEL=INFO (平衡调试和性能)")
        print("   - LOG_REQUEST_DETAILS=false (简化日志)")
        print("   - LOG_FUNCTION_PARAMS=false (提高性能)")
    
    print("\n🎉 日志级别配置测试完成！")


if __name__ == "__main__":
    main()
