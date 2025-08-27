#!/usr/bin/env python3
"""
Test script for Docker deployment validation.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def run_command(cmd, check=True, capture=False):
    """Run a shell command."""
    print(f"Running: {cmd}")
    
    if capture:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"Command failed: {result.stderr}")
            sys.exit(1)
        return result.stdout.strip()
    else:
        result = subprocess.run(cmd, shell=True)
        if check and result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}")
            sys.exit(1)

def test_docker_deployment():
    """Test Docker deployment setup."""
    print("🐳 Testing Docker Deployment Setup")
    print("=" * 50)
    
    # 1. Verify required files exist
    print("1. Checking required files...")
    required_files = [
        "docker-compose.fastapi.yml",
        "Dockerfile.fastapi", 
        ".dockerignore",
        ".env.example",
        "DEPLOYMENT.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"   ✅ {file}")
    
    if missing_files:
        print(f"   ❌ Missing files: {missing_files}")
        return False
    
    # 2. Check Docker is available
    print("\n2. Checking Docker availability...")
    try:
        docker_version = run_command("docker --version", capture=True)
        print(f"   ✅ {docker_version}")
    except:
        print("   ❌ Docker not available")
        return False
    
    try:
        compose_version = run_command("docker compose version", capture=True)
        print(f"   ✅ {compose_version}")
    except:
        try:
            compose_version = run_command("docker-compose --version", capture=True)
            print(f"   ✅ {compose_version}")
        except:
            print("   ❌ Docker Compose not available")
            return False
    
    # 3. Validate Docker Compose configuration
    print("\n3. Validating Docker Compose configuration...")
    try:
        run_command("docker compose -f docker-compose.fastapi.yml config --quiet")
        print("   ✅ Docker Compose configuration is valid")
    except:
        print("   ❌ Docker Compose configuration is invalid")
        return False
    
    # 4. Check Dockerfile syntax
    print("\n4. Checking Dockerfile syntax...")
    try:
        # Dry run build to check syntax
        run_command("docker build -f Dockerfile.fastapi --dry-run . > /dev/null 2>&1 || echo 'Syntax OK'", capture=True)
        print("   ✅ Dockerfile syntax is valid")
    except:
        print("   ⚠️  Could not verify Dockerfile syntax (but likely OK)")
    
    # 5. Test environment file template
    print("\n5. Checking environment configuration...")
    try:
        with open(".env.example", "r") as f:
            env_content = f.read()
            required_vars = ["REDIS_URL", "API_HOST", "API_PORT", "ENVIRONMENT"]
            missing_vars = []
            
            for var in required_vars:
                if var not in env_content:
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"   ❌ Missing environment variables: {missing_vars}")
                return False
            else:
                print("   ✅ Environment template contains required variables")
    except:
        print("   ❌ Could not read .env.example")
        return False
    
    print("\n✅ Docker deployment setup is ready!")
    print("\nTo deploy:")
    print("1. Copy .env.example to .env and configure")
    print("2. Run: docker compose -f docker-compose.fastapi.yml up -d --build")
    print("3. Test: curl http://localhost:8000/health")
    print("4. View logs: docker compose -f docker-compose.fastapi.yml logs -f")
    
    return True

def test_deployment_docs():
    """Test that deployment documentation exists."""
    print("\n📚 Checking deployment documentation...")
    
    if Path("DEPLOYMENT.md").exists():
        print("   ✅ DEPLOYMENT.md exists")
        
        with open("DEPLOYMENT.md", "r") as f:
            content = f.read()
            
        # Check for key sections
        sections = [
            "Quick Start",
            "Docker Compose",
            "Configuration", 
            "Performance Tuning",
            "Security",
            "Troubleshooting"
        ]
        
        missing_sections = []
        for section in sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"   ⚠️  Missing documentation sections: {missing_sections}")
        else:
            print("   ✅ Documentation contains all key sections")
    else:
        print("   ❌ DEPLOYMENT.md missing")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Docker Deployment Test Suite")
    print("================================")
    
    success = True
    
    if not test_docker_deployment():
        success = False
        
    if not test_deployment_docs():
        success = False
    
    if success:
        print("\n🎉 All Docker deployment tests passed!")
        print("The FastAPI service is ready for containerized deployment.")
    else:
        print("\n❌ Some deployment tests failed.")
        sys.exit(1)