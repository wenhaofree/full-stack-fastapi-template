#!/usr/bin/env python3
"""Verify that all documentation files are created and accessible."""

import os
from pathlib import Path

def check_documentation():
    """Check if all documentation files exist."""
    print("📚 验证项目文档...")
    
    docs = [
        ("PROJECT_OVERVIEW.md", "项目总览"),
        ("DEVELOPMENT_GUIDE.md", "开发指南"),
        ("QUICK_START.md", "快速开始"),
        ("ARCHITECTURE.md", "架构文档"),
        ("README.md", "项目说明"),
    ]
    
    missing_docs = []
    existing_docs = []
    
    for doc_file, description in docs:
        if Path(doc_file).exists():
            size = Path(doc_file).stat().st_size
            existing_docs.append((doc_file, description, size))
            print(f"✅ {doc_file} ({description}) - {size} bytes")
        else:
            missing_docs.append((doc_file, description))
            print(f"❌ {doc_file} ({description}) - 缺失")
    
    print(f"\n📊 文档统计:")
    print(f"   存在: {len(existing_docs)} 个文档")
    print(f"   缺失: {len(missing_docs)} 个文档")
    
    if missing_docs:
        print(f"\n⚠️  缺失的文档:")
        for doc_file, description in missing_docs:
            print(f"   - {doc_file} ({description})")
        return False
    
    print(f"\n✅ 所有文档都已创建完成!")
    
    # 检查项目结构
    print(f"\n🏗️  验证项目结构...")
    
    directories = [
        "app/models",
        "app/schemas", 
        "app/services",
        "app/routes",
        "app/dependencies",
        "app/exceptions",
        "app/middleware",
        "app/core",
    ]
    
    for directory in directories:
        if Path(directory).exists():
            files = list(Path(directory).glob("*.py"))
            print(f"✅ {directory}/ - {len(files)} 个文件")
        else:
            print(f"❌ {directory}/ - 目录不存在")
    
    return True

if __name__ == "__main__":
    success = check_documentation()
    if success:
        print(f"\n🎉 项目重构和文档创建完成!")
        print(f"📖 开始阅读 PROJECT_OVERVIEW.md 了解项目结构")
        print(f"🚀 使用 QUICK_START.md 快速开始开发")
    else:
        print(f"\n❌ 发现问题，请检查缺失的文件")
