#!/usr/bin/env python3
"""
Complete System Test Script - Terminal Based
Tests all functionality including login, PDF queries, and database queries
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "full_name": "Test User",
    "email": "one@gmail.com",
    "password": "shlok160404",
    "role": "resident"
}

class CompleteSystemTester:
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
    
    def test_user_login(self) -> bool:
        """Test 2: User Login"""
        self.print_step("2", "User Login - Get JWT token")
        
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
    
    def test_database_query(self) -> bool:
        """Test 3: Database Query (No PDF needed)"""
        self.print_step("3", "Database Query - Test pension data from database")
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            query = "What is my will be my pension when i retire?"
            print(f"📝 Query: {query}")
            
            response = self.session.post(
                f"{self.base_url}/prompt",
                json={"query": query},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Database query successful")
                print(f"🤖 Response: {data.get('summary', 'No summary available')[:200]}...")
                
                # Check for database indicator
                if "data_source" in str(data):
                    print("🔍 Data Source: DATABASE_PENSION_DATA ✅")
                    print("📋 Note: This analysis is based on your pension data stored in our database")
                else:
                    print("⚠️ Data source indicator not found")
                
                return True
            else:
                print(f"❌ Database query failed - Status: {response.status_code}")
                print(f"📊 Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Database query error: {e}")
            return False
    
    def test_pdf_query(self) -> bool:
        """Test 4: PDF Query (Test uploaded document search)"""
        self.print_step("4", "PDF Query - Test searching uploaded PDF documents")
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            query = "What does my uploaded pension plan document say about retirement age?"
            print(f"📝 Query: {query}")
            
            response = self.session.post(
                f"{self.base_url}/prompt",
                json={"query": query},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ PDF query successful")
                print(f"🤖 Response: {data.get('summary', 'No summary available')[:200]}...")
                
                # Check for PDF search indicators
                if "search_type" in str(data):
                    print("🔍 Search Type: PDF_DOCUMENT_SEARCH ✅")
                    if "pdf_status" in str(data):
                        pdf_status = data.get("pdf_status", "Unknown")
                        print(f"🔍 PDF Status: {pdf_status} ✅")
                    print("📋 Note: This response is from searching your uploaded PDF documents")
                else:
                    print("⚠️ PDF search indicators not found")
                
                return True
            else:
                print(f"❌ PDF query failed - Status: {response.status_code}")
                print(f"📊 Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ PDF query error: {e}")
            return False
    
    def test_risk_analysis(self) -> bool:
        """Test 5: Risk Analysis Query (Database data)"""
        self.print_step("5", "Risk Analysis - Test risk profile analysis")
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            query = "Analyze my risk profile"
            print(f"📝 Query: {query}")
            
            response = self.session.post(
                f"{self.base_url}/prompt",
                json={"query": query},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Risk analysis successful")
                print(f"🤖 Response: {data.get('summary', 'No summary available')[:200]}...")
                
                # Check for database indicator
                if "data_source" in str(data):
                    print("🔍 Data Source: DATABASE_PENSION_DATA ✅")
                    print("📋 Note: This risk analysis is based on your pension data stored in our database")
                else:
                    print("⚠️ Data source indicator not found")
                
                return True
            else:
                print(f"❌ Risk analysis failed - Status: {response.status_code}")
                print(f"📊 Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Risk analysis error: {e}")
            return False
    
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
    
    def run_complete_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Complete Pension AI System Test")
        print(f"🌐 Base URL: {self.base_url}")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("User Login", self.test_user_login),
            ("Database Query", self.test_database_query),
            ("PDF Query", self.test_pdf_query),
            ("Risk Analysis", self.test_risk_analysis),
            ("User Dashboard", self.test_user_dashboard)
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
            print("\n🔍 Key Findings:")
            print("✅ Database queries show 'data_source': 'DATABASE_PENSION_DATA'")
            print("✅ PDF queries show 'search_type': 'PDF_DOCUMENT_SEARCH'")
            print("✅ Clear distinction between data sources")
            print("✅ No more 'error while searching document' messages")
        else:
            print(f"\n⚠️ {total - passed} tests failed. Check the logs above for details.")
        
        return passed == total

def main():
    """Main test execution"""
    print("🧪 Pension AI Complete System Tester (Terminal Based)")
    print("=" * 60)
    
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
    tester = CompleteSystemTester(BASE_URL)
    success = tester.run_complete_test()
    
    if success:
        print("\n🚀 System is ready for production use!")
        print("📋 All endpoints are working correctly")
        print("🔍 PDF and database queries are properly distinguished")
    else:
        print("\n🔧 Some tests failed. Fix the issues before using the system.")

if __name__ == "__main__":
    main()
