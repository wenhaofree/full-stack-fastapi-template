#!/usr/bin/env python3
"""Verify that initial data was created correctly."""

from sqlmodel import Session, select
from app.core.db import engine
from app.models.user import User
from app.core.config import settings

def verify_initial_data():
    """Verify that the initial superuser was created."""
    print("🔍 Verifying initial data...")
    
    with Session(engine) as session:
        # Check if superuser exists
        user = session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()
        
        if user:
            print(f"✅ Superuser found:")
            print(f"   Email: {user.email}")
            print(f"   Full name: {user.full_name}")
            print(f"   Is active: {user.is_active}")
            print(f"   Is superuser: {user.is_superuser}")
            print(f"   User ID: {user.id}")
        else:
            print("❌ Superuser not found!")
            return False
        
        # Count total users
        total_users = len(session.exec(select(User)).all())
        print(f"📊 Total users in database: {total_users}")
        
    print("✅ Initial data verification completed successfully!")
    return True

if __name__ == "__main__":
    verify_initial_data()
