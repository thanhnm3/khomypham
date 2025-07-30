#!/usr/bin/env python
"""
Script kiểm tra deployment status
"""

import requests
import os
import sys

def check_deployment():
    """Kiểm tra deployment"""
    url = "https://khomypham.onrender.com/"
    
    print(f"🔍 Checking deployment at: {url}")
    
    try:
        # Test basic connection
        response = requests.get(url, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Deployment is working!")
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot connect to server")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Server is taking too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_health_endpoint():
    """Kiểm tra health endpoint"""
    url = "https://khomypham.onrender.com/health/"
    
    print(f"\n🔍 Checking health endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ Health Status: {response.status_code}")
        print(f"✅ Response: {response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")

if __name__ == '__main__':
    print("🚀 Deployment Check Tool")
    print("=" * 50)
    
    success = check_deployment()
    check_health_endpoint()
    
    if success:
        print("\n✅ Deployment is working correctly!")
        print("🌐 URL: https://khomypham.onrender.com/")
        print("👤 Admin: https://khomypham.onrender.com/admin/")
    else:
        print("\n❌ Deployment has issues!")
        print("🔧 Check Render.com logs for more details") 