#!/usr/bin/env python3
"""
Generate secure secrets for production deployment
"""
import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_password(length=16):
    """Generate a secure password"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    print("🔐 Secure Secrets for Knowledge Assistant")
    print("=" * 45)
    print(f"SECRET_KEY={generate_secret_key()}")
    print(f"POSTGRES_PASSWORD={generate_password()}")
    print(f"REDIS_PASSWORD={generate_password()}")
    print(f"JWT_SECRET={generate_secret_key()}")
    print()
    print("⚠️  IMPORTANT: Add these to your .env file and keep them secure!")
    print("⚠️  Never commit these secrets to version control!")