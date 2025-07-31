#!/usr/bin/env python3
"""增强日志系统使用示例。"""

import asyncio
import time
from typing import List, Dict, Any

from app.core.logger import (
    get_logger,
    get_structured_logger,
    log_function_call,
    log_async_function_call,
)
from app.core.tracing import TraceContext


# 示例1: 基础日志使用
def basic_logging_example():
    """基础日志使用示例。"""
    logger = get_logger("example.basic")
    
    logger.debug("调试信息：开始处理用户请求")
    logger.info("用户请求处理开始")
    logger.warning("检测到潜在的性能问题")
    logger.error("处理过程中发生错误")


# 示例2: 结构化日志使用
def structured_logging_example():
    """结构化日志使用示例。"""
    logger = get_structured_logger("example.structured")
    
    # 用户登录日志
    logger.info(
        "用户登录",
        user_id="user_12345",
        email="john.doe@example.com",
        login_method="password",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        session_id="sess_abcdef123456"
    )
    
    # 数据库操作日志
    logger.info(
        "数据库查询执行",
        query_type="SELECT",
        table="users",
        execution_time="0.045s",
        rows_affected=1,
        cache_hit=False
    )
    
    # 业务操作日志
    logger.info(
        "订单创建",
        order_id="order_789",
        customer_id="user_12345",
        total_amount=99.99,
        currency="USD",
        payment_method="credit_card",
        items_count=3
    )


# 示例3: 追踪上下文使用
def trace_context_example():
    """追踪上下文使用示例。"""
    logger = get_structured_logger("example.trace")
    
    # 模拟用户请求处理
    with TraceContext(user_id="user_12345") as ctx:
        logger.info("开始处理用户请求", operation="user_request")
        
        # 模拟数据库操作
        with TraceContext(user_id="user_12345") as db_ctx:
            logger.info("执行数据库查询", operation="db_query", table="orders")
            time.sleep(0.01)  # 模拟查询时间
            logger.info("数据库查询完成", rows_returned=5)
        
        # 模拟外部API调用
        with TraceContext(user_id="user_12345") as api_ctx:
            logger.info("调用外部API", operation="external_api", service="payment_gateway")
            time.sleep(0.02)  # 模拟API调用时间
            logger.info("外部API调用完成", status_code=200)
        
        logger.info("用户请求处理完成", operation="user_request", status="success")


# 示例4: 函数装饰器使用
@log_function_call(include_args=True, include_result=True, include_timing=True)
def calculate_order_total(items: List[Dict[str, Any]]) -> float:
    """计算订单总金额（带日志装饰器）。"""
    total = 0.0
    for item in items:
        total += item.get('price', 0.0) * item.get('quantity', 1)
    
    # 模拟一些处理时间
    time.sleep(0.01)
    
    return total


@log_function_call(include_args=True, include_timing=True)
def process_payment(order_id: str, amount: float, payment_method: str) -> bool:
    """处理支付（带日志装饰器）。"""
    logger = get_structured_logger("example.payment")
    
    logger.info(
        "开始处理支付",
        order_id=order_id,
        amount=amount,
        payment_method=payment_method
    )
    
    # 模拟支付处理
    time.sleep(0.05)
    
    # 模拟支付成功
    success = True
    
    logger.info(
        "支付处理完成",
        order_id=order_id,
        status="success" if success else "failed"
    )
    
    return success


# 示例5: 异步函数装饰器使用
@log_async_function_call(include_args=True, include_result=True, include_timing=True)
async def send_notification(user_id: str, message: str, channel: str = "email") -> bool:
    """发送通知（异步函数带日志装饰器）。"""
    logger = get_structured_logger("example.notification")
    
    logger.info(
        "准备发送通知",
        user_id=user_id,
        channel=channel,
        message_length=len(message)
    )
    
    # 模拟异步发送过程
    await asyncio.sleep(0.1)
    
    # 模拟发送成功
    success = True
    
    logger.info(
        "通知发送完成",
        user_id=user_id,
        channel=channel,
        status="sent" if success else "failed"
    )
    
    return success


# 示例6: 错误处理和异常日志
def error_handling_example():
    """错误处理和异常日志示例。"""
    logger = get_structured_logger("example.error")
    
    try:
        # 模拟业务逻辑错误
        user_input = "invalid_email_format"
        if "@" not in user_input:
            raise ValueError(f"无效的邮箱格式: {user_input}")
    
    except ValueError as e:
        logger.error(
            "用户输入验证失败",
            error_type="VALIDATION_ERROR",
            user_input=user_input,
            error_message=str(e),
            exc_info=True
        )
    
    try:
        # 模拟系统错误
        raise ConnectionError("无法连接到数据库")
    
    except ConnectionError as e:
        logger.critical(
            "系统连接错误",
            error_type="CONNECTION_ERROR",
            service="database",
            error_message=str(e),
            exc_info=True
        )


# 示例7: 性能监控日志
def performance_monitoring_example():
    """性能监控日志示例。"""
    logger = get_structured_logger("example.performance")
    
    # 监控数据库查询性能
    start_time = time.time()
    time.sleep(0.03)  # 模拟查询时间
    query_time = time.time() - start_time
    
    logger.info(
        "数据库查询性能",
        query="SELECT * FROM orders WHERE user_id = ?",
        execution_time=f"{query_time:.3f}s",
        rows_returned=25,
        index_used=True,
        cache_hit=False
    )
    
    # 监控缓存操作
    logger.info(
        "缓存操作",
        operation="GET",
        key="user:12345:profile",
        hit=True,
        ttl_remaining=3600,
        size_bytes=1024
    )
    
    # 监控外部服务调用
    logger.info(
        "外部服务调用",
        service="payment_gateway",
        endpoint="/api/v1/charge",
        method="POST",
        response_time="0.250s",
        status_code=200,
        retry_count=0
    )


# 示例8: 完整的业务流程日志
async def complete_business_flow_example():
    """完整的业务流程日志示例。"""
    logger = get_structured_logger("example.business_flow")
    
    # 模拟电商订单处理流程
    with TraceContext(user_id="user_12345") as ctx:
        logger.info("开始处理订单", operation="order_processing")
        
        # 1. 验证用户
        logger.info("验证用户身份", step="user_validation")
        await asyncio.sleep(0.01)
        
        # 2. 计算订单总额
        items = [
            {"name": "商品A", "price": 29.99, "quantity": 2},
            {"name": "商品B", "price": 19.99, "quantity": 1},
        ]
        total = calculate_order_total(items)
        logger.info("订单总额计算完成", total_amount=total, items_count=len(items))
        
        # 3. 处理支付
        payment_success = process_payment("order_789", total, "credit_card")
        
        if payment_success:
            # 4. 发送确认通知
            await send_notification(
                "user_12345", 
                f"您的订单 order_789 已确认，总金额 ${total}",
                "email"
            )
            
            logger.info(
                "订单处理完成",
                operation="order_processing",
                order_id="order_789",
                status="success",
                total_amount=total
            )
        else:
            logger.error(
                "订单处理失败",
                operation="order_processing",
                order_id="order_789",
                status="payment_failed",
                total_amount=total
            )


async def main():
    """主函数，运行所有示例。"""
    print("🚀 增强日志系统使用示例")
    print("=" * 50)
    
    print("\n1. 基础日志示例")
    basic_logging_example()
    
    print("\n2. 结构化日志示例")
    structured_logging_example()
    
    print("\n3. 追踪上下文示例")
    trace_context_example()
    
    print("\n4. 函数装饰器示例")
    items = [
        {"name": "商品A", "price": 29.99, "quantity": 2},
        {"name": "商品B", "price": 19.99, "quantity": 1},
    ]
    total = calculate_order_total(items)
    print(f"   计算结果: ${total}")
    
    print("\n5. 异步函数装饰器示例")
    result = await send_notification("user_12345", "测试消息", "email")
    print(f"   发送结果: {result}")
    
    print("\n6. 错误处理示例")
    error_handling_example()
    
    print("\n7. 性能监控示例")
    performance_monitoring_example()
    
    print("\n8. 完整业务流程示例")
    await complete_business_flow_example()
    
    print("\n✅ 所有示例执行完成！")
    print("\n📋 查看日志文件:")
    print("   - logs/app.log (结构化JSON格式)")
    print("   - logs/error.log (错误日志)")
    print("\n🎯 在生产环境中，这些日志可以:")
    print("   - 导入到ELK Stack进行分析")
    print("   - 通过追踪ID跟踪完整请求链路")
    print("   - 监控应用性能和错误率")
    print("   - 生成业务指标和报告")


if __name__ == "__main__":
    asyncio.run(main())
