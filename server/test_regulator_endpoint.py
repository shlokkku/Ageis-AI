#!/usr/bin/env python3
"""
Test script for regulator dashboard endpoint
"""

import requests
import json

def test_regulator_login():
    """Test regulator login"""
    print("🔐 Testing regulator login...")
    
    login_data = {
        "username": "regulator1@example.com",
        "password": "password-123"
    }
    
    try:
        response = requests.post("http://localhost:8000/login", data=login_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful! Token: {data['access_token'][:20]}...")
            return data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_regulator_dashboard(token):
    """Test regulator dashboard endpoint"""
    print("\n📊 Testing regulator dashboard...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("http://localhost:8000/regulator/dashboard", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Regulator dashboard successful!")
            print(f"📈 Total users: {data.get('total_users', 'N/A')}")
            print(f"💰 Portfolio summary: {data.get('portfolio_summary', 'N/A')}")
            print(f"🎯 Risk distribution: {data.get('risk_distribution', 'N/A')}")
            print(f"🌍 Geographic analysis: {len(data.get('geographic_analysis', {}))} regions")
            return True
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False

def test_users_all(token):
    """Test users/all endpoint"""
    print("\n👥 Testing users/all endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("http://localhost:8000/users/all", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Users/all successful!")
            print(f"📊 Total users: {data.get('total_count', 'N/A')}")
            print(f"👤 Sample users: {[u['full_name'] for u in data.get('users', [])[:3]]}")
            return True
        else:
            print(f"❌ Users/all failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Users/all error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Regulator Dashboard Endpoints")
    print("=" * 50)
    
    # Test login
    token = test_regulator_login()
    if not token:
        print("❌ Cannot proceed without valid token")
        return
    
    # Test dashboard
    dashboard_ok = test_regulator_dashboard(token)
    
    # Test users/all
    users_ok = test_users_all(token)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   🔐 Login: {'✅ PASS' if token else '❌ FAIL'}")
    print(f"   📊 Dashboard: {'✅ PASS' if dashboard_ok else '❌ FAIL'}")
    print(f"   👥 Users/All: {'✅ PASS' if users_ok else '❌ FAIL'}")
    
    if token and dashboard_ok and users_ok:
        print("\n🎉 All tests passed! Regulator dashboard is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the backend server.")

if __name__ == "__main__":
    main()
