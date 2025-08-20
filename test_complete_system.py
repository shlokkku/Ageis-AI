#!/usr/bin/env python3
"""
Complete System Test Script for Pension AI API
Tests all functionality without requiring PDF uploads
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "full_name": "Test User",
    "email": "testuser@example.com",
    "password": "testpass123",
    "role": "resident"
}

class PensionAITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.jwt_token = None
        self.user_id = None
        
    def print_step(self, step: str, description: str):
        print(f"\n{'='*60}")
        print(f"🔍 STEP {step}: {description}")
        print(f"{'='*60}")
    
    def test_health_check(self) -> bool:
        """Test 1: Health Check"""
        self.print_step("1", "Health Check - Verify server is running")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed - Server is running")
                print(f"📊 Response: {response.json()}")
                return True
            else:
                print(f"❌ Health check failed - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_user_signup(self) -> bool:
        """Test 2: User Registration"""
        self.print_step("2", "User Registration - Create test user")
        
        try:
            response = self.session.post(
                f"{self.base_url}/signup",
                json=TEST_USER
            )
            
            if response.status_code == 200:
                print("✅ User registration successful")
                print(f"📊 Response: {response.json()}")
                return True
            elif response.status_code == 400 and "already exists" in response.text.lower():
                print("ℹ️ User already exists - continuing with login")
                return True
            else:
                print(f"❌ User registration failed - Status: {response.status_code}")
                print(f"📊 Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ User registration error: {e}")
            return False
    
    def test_user_login(self) -> bool:
        """Test 3: User Login"""
        self.print_step("3", "User Login - Get JWT token")
        
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                data={
                    "username": TEST_USER["email"],
                    "password": TEST_USER["password"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                if self.jwt_token:
                    print("✅ User login successful")
                    print(f"🔑 JWT Token: {self.jwt_token[:50]}...")
                    print(f"👤 User ID: {self.user_id}")
                    print(f"📊 Full Response: {data}")
                    return True
                else:
                    print("❌ JWT token not received")
                    return False
            else:
                print(f"❌ User login failed - Status: {response.status_code}")
                print(f"📊 Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ User login error: {e}")
            return False
    
    def test_pension_query(self, query: str, description: str) -> bool:
        """Test 4: AI Pension Queries"""
        self.print_step("4", f"AI Query: {description}")
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                f"{self.base_url}/prompt",
                json={"query": query},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ AI query successful")
                print(f"📝 Query: {query}")
                print(f"🤖 Response: {data.get('response', 'No response')}")
                return True
            else:
                print(f"❌ AI query failed - Status: {response.status_code}")
                print(f"📊 Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ AI query error: {e}")
            return False
    
    def test_pdf_search_without_pdf(self) -> bool:
        """Test 5: PDF Search (No PDFs exist)"""
        self.print_step("5", "PDF Search - Testing without uploaded PDFs")
        
        return self.test_pension_query(
            "What does my pension plan document say about retirement age?",
            "PDF Search Query (No PDFs exist)"
        )
    
    def test_user_dashboard(self) -> bool:
        """Test 6: User Dashboard"""
        self.print_step("6", "User Dashboard - Get personal pension data")
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            
            response = self.session.get(
                f"{self.base_url}/resident/dashboard",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Dashboard access successful")
                print(f"👤 User: {data.get('user', {}).get('full_name', 'Unknown')}")
                print(f"💰 Annual Income: ₹{data.get('pension_data', {}).get('annual_income', 'N/A'):,}")
                print(f"💾 Current Savings: ₹{data.get('pension_data', {}).get('current_savings', 'N/A'):,}")
                return True
            else:
                print(f"❌ Dashboard access failed - Status: {response.status_code}")
                print(f"📊 Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Dashboard access error: {e}")
            return False
    
    def test_user_profile(self) -> bool:
        """Test 7: User Profile"""
        self.print_step("7", "User Profile - Get current user info")
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            
            response = self.session.get(
                f"{self.base_url}/users/me",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ User profile access successful")
                print(f"👤 Full Name: {data.get('full_name', 'Unknown')}")
                print(f"📧 Email: {data.get('email', 'Unknown')}")
                print(f"🔑 Role: {data.get('role', 'Unknown')}")
                return True
            else:
                print(f"❌ User profile access failed - Status: {response.status_code}")
                print(f"📊 Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ User profile access error: {e}")
            return False
    
    def run_complete_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Complete Pension AI System Test")
        print(f"🌐 Base URL: {self.base_url}")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_signup),
            ("User Login", self.test_user_login),
            ("Basic Pension Query", lambda: self.test_pension_query(
                "What is my current pension savings?", "Basic Pension Data Query"
            )),
            ("Risk Analysis Query", lambda: self.test_pension_query(
                "Analyze my risk profile", "Risk Analysis Query"
            )),
            ("Fraud Detection Query", lambda: self.test_pension_query(
                "Check for any suspicious activity in my pension", "Fraud Detection Query"
            )),
            ("PDF Search (No PDFs)", self.test_pdf_search_without_pdf),
            ("User Dashboard", self.test_user_dashboard),
            ("User Profile", self.test_user_profile)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                print(f"❌ Test '{test_name}' crashed: {e}")
                results.append((test_name, False))
        
        # Summary
        self.print_step("SUMMARY", "Test Results")
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"📊 Test Results: {passed}/{total} tests passed")
        print("\nDetailed Results:")
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        if passed == total:
            print("\n🎉 All tests passed! System is working perfectly.")
        else:
            print(f"\n⚠️ {total - passed} tests failed. Check the logs above for details.")
        
        return passed == total

def main():
    """Main test execution"""
    print("🧪 Pension AI Complete System Tester")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding properly. Status: {response.status_code}")
            return
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("💡 Make sure the server is running with: python -m uvicorn app.main:app --reload")
        return
    
    # Run tests
    tester = PensionAITester(BASE_URL)
    success = tester.run_complete_test()
    
    if success:
        print("\n🚀 Ready to test with Postman!")
        print("📋 Use the JWT token from the login test in your Postman requests")
    else:
        print("\n🔧 Some tests failed. Fix the issues before using Postman.")

if __name__ == "__main__":
    main()

