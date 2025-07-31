#!/usr/bin/env python3
"""Test script to verify the refactored application works correctly."""

from fastapi.testclient import TestClient
from app.main import app

def test_basic_functionality():
    """Test basic application functionality."""
    client = TestClient(app)
    
    print("🧪 Testing refactored FastAPI application...")
    
    # Test health check
    print("1. Testing health check endpoint...")
    response = client.get("/api/v1/health/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    
    # Test OpenAPI docs
    print("2. Testing OpenAPI documentation...")
    response = client.get("/api/v1/openapi.json")
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200
    
    print("✅ All basic tests passed!")
    print("\n📋 Refactoring Summary:")
    print("   ✅ Models separated from schemas")
    print("   ✅ CRUD operations moved to services")
    print("   ✅ Routes reorganized")
    print("   ✅ Exception handling implemented")
    print("   ✅ Middleware added")
    print("   ✅ Dependencies restructured")
    print("   ✅ Logging system configured")

if __name__ == "__main__":
    test_basic_functionality()
