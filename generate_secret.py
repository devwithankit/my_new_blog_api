"""
Run this once before starting the server:
    python generate_secret.py
"""
import secrets
import os
from pathlib import Path


def generate_secret_key(length: int = 32) -> str:
    """
    secrets.token_hex(32) = 32 bytes = 256 bits entropy
    Cryptographically secure random — OS-level randomness use karta hai
    """
    return secrets.token_hex(length)


def update_env_file(key_name: str, key_value: str, env_path: Path):
    """
    .env file mein key update ya add karo
    """
    lines = []
    key_found = False

    if env_path.exists():
        with open(env_path, "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith(f"{key_name}="):
                lines[i] = f"{key_name}={key_value}\n"
                key_found = True
                break

    if not key_found:
        lines.append(f"{key_name}={key_value}\n")

    with open(env_path, "w") as f:
        f.writelines(lines)


def main():
    env_path = Path(".env")

    print("\n" + "="*60)
    print("       🔐 SECRET KEY GENERATOR")
    print("="*60)

    # Generate karo
    secret_key = generate_secret_key(32)  # 256-bit

    print(f"\n✅ Generated SECRET_KEY (256-bit / 64 chars):")
    print(f"\n   {secret_key}\n")

    # .env mein save karo
    update_env_file("SECRET_KEY", secret_key, env_path)
    print(f"✅ Saved to: {env_path.resolve()}")

    print("\n" + "="*60)
    print("  ⚠️  IMPORTANT — Keep this key PRIVATE:")
    print("  - Never commit .env to Git")
    print("  - Add .env to .gitignore")
    print("  - In production, use environment variables")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()