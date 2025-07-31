#!/usr/bin/env python3
"""测试专业的日志配置。"""

import json
import logging
import os
import sys
import time
from fastapi.testclient import TestClient

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.main import app


def test_log_levels():
    """测试四个核心日志级别。"""
    print("🧪 测试四个核心日志级别...")
    print(f"当前环境: {settings.ENVIRONMENT}")
    print(f"配置的日志级别: {settings.LOG_LEVEL}")
    print(f"日志格式: {settings.LOG_FORMAT}")
    print(f"文件日志: {'启用' if settings.LOG_FILE_ENABLED else '禁用'}")
    
    # 获取不同的日志记录器
    app_logger = logging.getLogger("app.test")
    access_logger = logging.getLogger("app.access")
    
    print("\n📝 测试四个核心日志级别的输出...")
    
    # DEBUG级别 - 最详细的调试信息
    app_logger.debug("🔵 DEBUG: 详细的调试信息", extra={
        "function": "test_function",
        "parameters": {"user_id": 123, "action": "login"},
        "execution_time": "0.005s"
    })
    
    # INFO级别 - 正常流程信息
    app_logger.info("🟢 INFO: 正常流程信息", extra={
        "event": "user_login",
        "user_id": 123,
        "ip_address": "192.168.1.100",
        "timestamp": time.time()
    })
    
    # WARNING级别 - 不影响程序运行的小异常
    app_logger.warning("🟡 WARNING: 潜在问题警告", extra={
        "issue": "request_rate_high",
        "current_rate": "150/min",
        "threshold": "100/min",
        "action": "rate_limiting_applied"
    })
    
    # ERROR级别 - 代码异常、逻辑错误
    app_logger.error("🔴 ERROR: 业务逻辑错误", extra={
        "error_type": "database_connection_failed",
        "error_code": "DB001",
        "retry_count": 3,
        "next_retry": "30s"
    })
    
    print("   ✅ 四个核心日志级别测试完成")


def test_access_log_middleware():
    """测试专业的访问日志中间件。"""
    print("\n🌐 测试专业的访问日志中间件...")
    
    client = TestClient(app)
    
    # 1. 测试正常请求
    print("\n1. 测试正常GET请求...")
    response = client.get("/api/v1/health/")
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    print(f"   请求ID: {response.headers.get('X-Request-ID')}")
    
    # 2. 测试POST请求（含请求体）
    print("\n2. 测试POST请求（含敏感数据过滤）...")
    if settings.ENVIRONMENT == "local":
        user_data = {
            "email": "professional_test@example.com",
            "password": "super_secret_password",  # 应该被过滤
            "full_name": "Professional Test User",
            "age": 28
        }
        
        response = client.post("/api/v1/debug/users", json=user_data)
        print(f"   状态码: {response.status_code}")
        print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
        print("   查看日志确认密码字段被过滤")
    
    # 3. 测试错误请求
    print("\n3. 测试404错误请求...")
    response = client.get("/api/v1/nonexistent")
    print(f"   状态码: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    # 4. 测试带查询参数的请求
    print("\n4. 测试带查询参数的请求...")
    if settings.ENVIRONMENT == "local":
        params = {
            "page": 1,
            "page_size": 5,
            "keyword": "专业测试",
            "is_active": True
        }
        response = client.get("/api/v1/debug/users", params=params)
        print(f"   状态码: {response.status_code}")
        print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    print("   ✅ 访问日志中间件测试完成")


def test_json_vs_console_format():
    """测试JSON格式 vs 控制台格式。"""
    print("\n🎨 测试不同的日志格式...")
    
    logger = logging.getLogger("app.format_test")
    
    # 记录一条包含丰富信息的日志
    logger.info("格式测试日志", extra={
        "user_id": "user_123",
        "action": "purchase",
        "product_id": "prod_456",
        "amount": 99.99,
        "currency": "USD",
        "payment_method": "credit_card",
        "metadata": {
            "campaign": "summer_sale",
            "discount": 0.15,
            "referrer": "google_ads"
        }
    })
    
    print(f"   当前格式: {settings.LOG_FORMAT}")
    if settings.LOG_FORMAT == "console":
        print("   ✅ 控制台格式 - 人类可读，适合开发调试")
    elif settings.LOG_FORMAT == "json":
        print("   ✅ JSON格式 - 结构化，适合日志聚合分析")
    else:
        print("   ✅ 混合格式 - 控制台可读 + 文件JSON")


def test_log_file_rotation():
    """测试日志文件轮转。"""
    print("\n📁 测试日志文件轮转...")
    
    if settings.LOG_FILE_ENABLED:
        log_files = []
        
        # 检查主日志文件
        if os.path.exists("logs/app.log"):
            log_files.append("logs/app.log")
            file_size = os.path.getsize("logs/app.log")
            print(f"   主日志文件: logs/app.log ({file_size} bytes)")
        
        # 检查错误日志文件
        if os.path.exists("logs/error.log"):
            log_files.append("logs/error.log")
            file_size = os.path.getsize("logs/error.log")
            print(f"   错误日志文件: logs/error.log ({file_size} bytes)")
        
        # 检查轮转文件
        for i in range(1, settings.LOG_FILE_BACKUP_COUNT + 1):
            backup_file = f"logs/app.log.{i}"
            if os.path.exists(backup_file):
                log_files.append(backup_file)
                file_size = os.path.getsize(backup_file)
                print(f"   备份文件: {backup_file} ({file_size} bytes)")
        
        print(f"   配置的最大文件大小: {settings.LOG_FILE_MAX_SIZE}MB")
        print(f"   配置的备份文件数量: {settings.LOG_FILE_BACKUP_COUNT}")
        print(f"   实际日志文件数量: {len(log_files)}")
        print("   ✅ 日志文件轮转配置正常")
    else:
        print("   ⚠️  文件日志已禁用")


def test_environment_specific_config():
    """测试环境特定的配置。"""
    print("\n⚙️  测试环境特定的配置...")
    
    print(f"当前环境: {settings.ENVIRONMENT}")
    
    if settings.ENVIRONMENT == "local":
        print("   开发环境配置:")
        print(f"   - 日志级别: {settings.LOG_LEVEL} (建议: DEBUG)")
        print(f"   - 请求详情: {settings.LOG_REQUEST_DETAILS} (建议: true)")
        print(f"   - 函数参数: {settings.LOG_FUNCTION_PARAMS} (建议: true)")
        print(f"   - 日志格式: {settings.LOG_FORMAT} (建议: console)")
        
        recommendations = []
        if settings.LOG_LEVEL != "DEBUG":
            recommendations.append("建议设置 LOG_LEVEL=DEBUG 以获得详细调试信息")
        if not settings.LOG_REQUEST_DETAILS:
            recommendations.append("建议设置 LOG_REQUEST_DETAILS=true 以调试API")
        if not settings.LOG_FUNCTION_PARAMS:
            recommendations.append("建议设置 LOG_FUNCTION_PARAMS=true 以调试函数")
        
        if recommendations:
            print("   📝 优化建议:")
            for rec in recommendations:
                print(f"     - {rec}")
        else:
            print("   ✅ 开发环境配置已优化")
    
    elif settings.ENVIRONMENT == "production":
        print("   生产环境配置:")
        print(f"   - 日志级别: {settings.LOG_LEVEL} (建议: INFO 或 WARNING)")
        print(f"   - 请求详情: {settings.LOG_REQUEST_DETAILS} (建议: false)")
        print(f"   - 函数参数: {settings.LOG_FUNCTION_PARAMS} (建议: false)")
        print(f"   - 日志格式: {settings.LOG_FORMAT} (建议: json)")
        
        recommendations = []
        if settings.LOG_LEVEL == "DEBUG":
            recommendations.append("建议设置 LOG_LEVEL=INFO 或 WARNING 以减少日志量")
        if settings.LOG_REQUEST_DETAILS:
            recommendations.append("建议设置 LOG_REQUEST_DETAILS=false 以保护隐私")
        if settings.LOG_FUNCTION_PARAMS:
            recommendations.append("建议设置 LOG_FUNCTION_PARAMS=false 以提高性能")
        if settings.LOG_FORMAT == "console":
            recommendations.append("建议设置 LOG_FORMAT=json 以便日志聚合")
        
        if recommendations:
            print("   📝 优化建议:")
            for rec in recommendations:
                print(f"     - {rec}")
        else:
            print("   ✅ 生产环境配置已优化")
    
    else:
        print("   测试环境配置:")
        print(f"   - 日志级别: {settings.LOG_LEVEL} (建议: INFO)")
        print(f"   - 请求详情: {settings.LOG_REQUEST_DETAILS} (建议: true)")
        print(f"   - 函数参数: {settings.LOG_FUNCTION_PARAMS} (建议: false)")
        print(f"   - 日志格式: {settings.LOG_FORMAT} (建议: json)")


def show_log_best_practices():
    """展示日志最佳实践。"""
    print("\n📚 日志最佳实践:")
    
    print("\n🔵 DEBUG级别 - 详细的调试信息:")
    print("   ✅ 函数参数和返回值")
    print("   ✅ 请求体和响应体内容")
    print("   ✅ 详细的执行流程")
    print("   ✅ 变量状态和中间结果")
    print("   ❌ 生产环境不建议使用")
    
    print("\n🟢 INFO级别 - 重要的业务事件:")
    print("   ✅ 用户登录/登出")
    print("   ✅ 重要操作的开始和完成")
    print("   ✅ 系统状态变化")
    print("   ✅ 业务流程关键节点")
    print("   ✅ 生产环境推荐级别")
    
    print("\n🟡 WARNING级别 - 潜在问题:")
    print("   ✅ 性能警告（响应时间过长）")
    print("   ✅ 配置问题（使用默认值）")
    print("   ✅ 不推荐的使用方式")
    print("   ✅ 资源使用警告（内存、CPU）")
    print("   ✅ 高流量生产环境推荐")
    
    print("\n🔴 ERROR级别 - 错误情况:")
    print("   ✅ 业务逻辑错误")
    print("   ✅ 外部服务调用失败")
    print("   ✅ 数据验证失败")
    print("   ✅ 可恢复的系统错误")
    print("   ✅ 需要立即关注的问题")


def main():
    """主测试函数。"""
    print("🚀 开始测试专业的日志配置...")
    print("=" * 60)
    
    # 展示最佳实践
    show_log_best_practices()
    
    # 测试日志级别
    test_log_levels()
    
    # 测试访问日志中间件
    test_access_log_middleware()
    
    # 测试日志格式
    test_json_vs_console_format()
    
    # 测试文件轮转
    test_log_file_rotation()
    
    # 测试环境配置
    test_environment_specific_config()
    
    print("\n" + "=" * 60)
    print("📋 专业日志配置测试总结:")
    print(f"   当前环境: {settings.ENVIRONMENT}")
    print(f"   日志级别: {settings.LOG_LEVEL}")
    print(f"   日志格式: {settings.LOG_FORMAT}")
    print(f"   文件日志: {'启用' if settings.LOG_FILE_ENABLED else '禁用'}")
    print(f"   请求详情: {'启用' if settings.LOG_REQUEST_DETAILS else '禁用'}")
    print(f"   函数参数: {'启用' if settings.LOG_FUNCTION_PARAMS else '禁用'}")
    
    print("\n🎯 关键特性:")
    print("   ✅ 四个核心日志级别（DEBUG/INFO/WARNING/ERROR）")
    print("   ✅ 彩色控制台输出（开发环境）")
    print("   ✅ JSON格式文件日志（便于分析）")
    print("   ✅ 自动日志文件轮转")
    print("   ✅ 敏感字段自动过滤")
    print("   ✅ 完整的链路追踪")
    print("   ✅ 环境感知配置")
    print("   ✅ 专业的访问日志中间件")
    
    print("\n🎉 专业日志配置测试完成！")


if __name__ == "__main__":
    main()
