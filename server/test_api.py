#!/usr/bin/env python3
"""
Test script for Pension AI API endpoints
Run this script to test the API functionality
"""

import requests
import json
import os
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

class PensionAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_id = None
        self.role = None
    
    def test_health(self) -> bool:
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            print(f"✅ Health check: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Service: {data.get('service')}")
                print(f"   Version: {data.get('version')}")
                return True
            return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_signup(self) -> bool:
        """Test user signup"""
        try:
            signup_data = {
                "full_name": "Test User",
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "role": "resident"
            }
            
            response = requests.post(
                f"{self.base_url}/signup",
                json=signup_data
            )
            
            print(f"✅ Signup: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   User ID: {data.get('id')}")
                print(f"   Role: {data.get('role')}")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                print("   User already exists (continuing with login)")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Signup failed: {e}")
            return False
    
    def test_login(self) -> bool:
        """Test user login"""
        try:
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = requests.post(
                f"{self.base_url}/login",
                data=login_data
            )
            
            print(f"✅ Login: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user_id')
                self.role = data.get('role')
                print(f"   User ID: {self.user_id}")
                print(f"   Role: {self.role}")
                print(f"   Token: {self.token[:20]}...")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def test_prompt(self) -> bool:
        """Test AI prompt endpoint"""
        if not self.token:
            print("❌ No token available for prompt test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            prompt_data = {
                "query": "What's my current pension status?"
            }
            
            response = requests.post(
                f"{self.base_url}/prompt",
                json=prompt_data,
                headers=headers
            )
            
            print(f"✅ Prompt: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Summary: {data.get('summary', 'No summary')[:100]}...")
                print(f"   User ID: {data.get('metadata', {}).get('user_id')}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Prompt failed: {e}")
            return False
    
    def test_output(self) -> bool:
        """Test output endpoint"""
        if not self.token:
            print("❌ No token available for output test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(
                f"{self.base_url}/output",
                headers=headers
            )
            
            print(f"✅ Output: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Total users: {data.get('total_users')}")
                print(f"   Categories: {len(data.get('data', []))}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Output failed: {e}")
            return False
    
    def test_dashboard_analytics(self) -> bool:
        """Test dashboard analytics endpoint"""
        if not self.token:
            print("❌ No token available for analytics test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(
                f"{self.base_url}/dashboard/analytics",
                headers=headers
            )
            
            print(f"✅ Dashboard Analytics: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Role: {data.get('role')}")
                if data.get('role') == 'resident':
                    print(f"   User ID: {data.get('user_id')}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Dashboard analytics failed: {e}")
            return False
    
    def test_user_dashboard(self) -> bool:
        """Test user dashboard endpoint"""
        if not self.token or not self.user_id:
            print("❌ No token or user ID available for user dashboard test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(
                f"{self.base_url}/users/{self.user_id}/dashboard",
                headers=headers
            )
            
            print(f"✅ User Dashboard: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   User: {data.get('user', {}).get('full_name')}")
                print(f"   Role: {data.get('user', {}).get('role')}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ User dashboard failed: {e}")
            return False
    
    def test_me(self) -> bool:
        """Test /users/me endpoint"""
        if not self.token:
            print("❌ No token available for /users/me test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=headers
            )
            
            print(f"✅ /users/me: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   User: {data.get('full_name')}")
                print(f"   Email: {data.get('email')}")
                print(f"   Role: {data.get('role')}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ /users/me failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all API tests"""
        print("🚀 Starting Pension AI API Tests")
        print("=" * 50)
        
        results = {}
        
        # Test health endpoint
        results['health'] = self.test_health()
        print()
        
        # Test signup
        results['signup'] = self.test_signup()
        print()
        
        # Test login
        results['login'] = self.test_login()
        print()
        
        if results['login']:
            # Test authenticated endpoints
            results['prompt'] = self.test_prompt()
            print()
            
            results['output'] = self.test_output()
            print()
            
            results['dashboard_analytics'] = self.test_dashboard_analytics()
            print()
            
            results['user_dashboard'] = self.test_user_dashboard()
            print()
            
            results['me'] = self.test_me()
            print()
        
        # Summary
        print("=" * 50)
        print("📊 Test Results Summary:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        passed = sum(results.values())
        total = len(results)
        print(f"\nOverall: {passed}/{total} tests passed")
        
        return results

def main():
    """Main function to run tests"""
    tester = PensionAPITester()
    results = tester.run_all_tests()
    
    if all(results.values()):
        print("\n🎉 All tests passed! The API is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the API configuration.")
        return 1

if __name__ == "__main__":
    exit(main())
