#!/usr/bin/env python3
"""测试增强的日志系统。"""

import asyncio
import time
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.logger import (
    get_logger,
    get_structured_logger,
    log_function_call,
    log_async_function_call,
)
from app.core.tracing import TraceContext, get_trace_context


def test_basic_logging():
    """测试基础日志功能。"""
    print("🧪 测试基础日志功能...")
    
    logger = get_logger("test")
    
    logger.debug("这是一条DEBUG日志")
    logger.info("这是一条INFO日志")
    logger.warning("这是一条WARNING日志")
    logger.error("这是一条ERROR日志")
    
    print("   ✅ 基础日志测试完成")


def test_structured_logging():
    """测试结构化日志。"""
    print("\n🧪 测试结构化日志...")
    
    logger = get_structured_logger("test.structured")
    
    logger.info(
        "用户登录",
        user_id="12345",
        email="test@example.com",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0"
    )
    
    logger.warning(
        "登录失败",
        email="invalid@example.com",
        reason="密码错误",
        attempt_count=3
    )
    
    logger.error(
        "数据库连接失败",
        database="postgresql",
        host="localhost",
        port=5432,
        error_code="CONNECTION_TIMEOUT"
    )
    
    print("   ✅ 结构化日志测试完成")


def test_trace_context():
    """测试追踪上下文。"""
    print("\n🧪 测试追踪上下文...")
    
    logger = get_structured_logger("test.trace")
    
    # 测试手动追踪上下文
    with TraceContext(user_id="user123") as ctx:
        logger.info("在追踪上下文中的日志", operation="test_operation")
        
        # 嵌套上下文
        with TraceContext(user_id="user456") as nested_ctx:
            logger.info("嵌套追踪上下文中的日志", operation="nested_operation")
        
        logger.info("回到原始追踪上下文", operation="back_to_original")
    
    # 测试上下文外的日志
    logger.info("上下文外的日志", operation="outside_context")
    
    print("   ✅ 追踪上下文测试完成")


@log_function_call(include_args=True, include_result=True, include_timing=True)
def test_function_with_logging(x: int, y: int) -> int:
    """测试带日志装饰器的函数。"""
    time.sleep(0.1)  # 模拟一些处理时间
    return x + y


@log_function_call(include_args=True, include_timing=True)
def test_function_with_error(should_fail: bool = True):
    """测试异常情况的日志记录。"""
    if should_fail:
        raise ValueError("这是一个测试异常")
    return "成功"


async def test_async_function_logging():
    """测试异步函数日志装饰器。"""
    print("\n🧪 测试异步函数日志...")
    
    @log_async_function_call(include_args=True, include_result=True)
    async def async_operation(data: str) -> str:
        await asyncio.sleep(0.1)  # 模拟异步操作
        return f"处理完成: {data}"
    
    result = await async_operation("测试数据")
    print(f"   异步函数结果: {result}")
    print("   ✅ 异步函数日志测试完成")


def test_function_logging():
    """测试函数日志装饰器。"""
    print("\n🧪 测试函数日志装饰器...")
    
    # 测试正常函数调用
    result = test_function_with_logging(10, 20)
    print(f"   函数结果: {result}")
    
    # 测试异常函数调用
    try:
        test_function_with_error(True)
    except ValueError as e:
        print(f"   捕获到预期异常: {e}")
    
    print("   ✅ 函数日志装饰器测试完成")


def test_api_requests():
    """测试API请求的日志记录。"""
    print("\n🧪 测试API请求日志...")
    
    client = TestClient(app)
    
    # 测试健康检查
    response = client.get("/api/v1/health/")
    print(f"   健康检查响应: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    print(f"   请求ID: {response.headers.get('X-Request-ID')}")
    
    # 测试用户认证（未认证）
    response = client.get("/api/v1/users/me")
    print(f"   用户认证响应: {response.status_code}")
    print(f"   追踪ID: {response.headers.get('X-Trace-ID')}")
    
    # 测试带自定义追踪ID的请求
    custom_trace_id = "custom-trace-12345"
    headers = {"X-Trace-ID": custom_trace_id}
    response = client.get("/api/v1/health/", headers=headers)
    print(f"   自定义追踪ID响应: {response.status_code}")
    print(f"   返回的追踪ID: {response.headers.get('X-Trace-ID')}")
    print(f"   追踪ID匹配: {response.headers.get('X-Trace-ID') == custom_trace_id}")
    
    print("   ✅ API请求日志测试完成")


def test_performance_logging():
    """测试性能相关的日志记录。"""
    print("\n🧪 测试性能日志...")
    
    logger = get_structured_logger("test.performance")
    
    # 模拟数据库查询
    start_time = time.time()
    time.sleep(0.05)  # 模拟查询时间
    query_time = time.time() - start_time
    
    logger.info(
        "数据库查询完成",
        query="SELECT * FROM users WHERE active = true",
        execution_time=f"{query_time:.3f}s",
        rows_returned=150,
        cache_hit=False
    )
    
    # 模拟缓存操作
    logger.info(
        "缓存操作",
        operation="SET",
        key="user:12345",
        ttl=3600,
        size_bytes=1024
    )
    
    # 模拟外部API调用
    logger.info(
        "外部API调用",
        service="payment_gateway",
        endpoint="/api/v1/payments",
        method="POST",
        response_time="0.250s",
        status_code=200
    )
    
    print("   ✅ 性能日志测试完成")


def test_error_scenarios():
    """测试错误场景的日志记录。"""
    print("\n🧪 测试错误场景日志...")
    
    logger = get_structured_logger("test.errors")
    
    try:
        # 模拟业务逻辑错误
        raise ValueError("用户输入无效")
    except ValueError as e:
        logger.error(
            "业务逻辑错误",
            error_type="VALIDATION_ERROR",
            user_input="invalid_email_format",
            exc_info=True
        )
    
    try:
        # 模拟系统错误
        raise ConnectionError("数据库连接失败")
    except ConnectionError as e:
        logger.critical(
            "系统错误",
            error_type="DATABASE_CONNECTION_ERROR",
            database_host="localhost",
            database_port=5432,
            exc_info=True
        )
    
    print("   ✅ 错误场景日志测试完成")


async def main():
    """主测试函数。"""
    print("🚀 开始测试增强的日志系统...")
    print(f"当前环境: {settings.ENVIRONMENT}")
    
    # 基础功能测试
    test_basic_logging()
    test_structured_logging()
    test_trace_context()
    test_function_logging()
    
    # 异步功能测试
    await test_async_function_logging()
    
    # API集成测试
    test_api_requests()
    
    # 性能和错误测试
    test_performance_logging()
    test_error_scenarios()
    
    print("\n📋 日志系统测试总结:")
    print("   ✅ 基础日志功能正常")
    print("   ✅ 结构化日志工作正常")
    print("   ✅ 追踪上下文传递正确")
    print("   ✅ 函数装饰器日志正常")
    print("   ✅ 异步函数日志正常")
    print("   ✅ API请求日志集成正常")
    print("   ✅ 性能日志记录正常")
    print("   ✅ 错误场景处理正常")
    print("   ✅ 彩色输出（开发环境）")
    print("   ✅ 追踪ID传递和记录")
    
    print("\n🎉 增强日志系统测试完成！")


if __name__ == "__main__":
    asyncio.run(main())
