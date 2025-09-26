#!/usr/bin/env python

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_server_running():
    try:
        response = requests.get(BASE_URL)
        print("✅ Server is running")
        return True
    except:
        print("❌ Server is not running. Please run 'start.bat' first")
        return False

def test_generate_plan():
    print("\n📋 Testing plan generation...")
    response = requests.post(f"{BASE_URL}/api/generate-plan")
    if response.status_code == 200:
        data = response.json()
        plan = data.get("plan", {})
        total_cases = plan.get("total_cases", 0)
        print(f"✅ Generated {total_cases} test cases")
        print(f"   Top 10 tests selected for execution")
        return True
    else:
        print(f"❌ Plan generation failed: {response.status_code}")
        return False

def test_execute_tests():
    print("\n🚀 Testing test execution...")
    response = requests.post(f"{BASE_URL}/api/execute-tests")
    if response.status_code == 200:
        print("✅ Test execution started successfully")
        
        for i in range(3):
            time.sleep(2)
            status_response = requests.get(f"{BASE_URL}/api/execution-status")
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"   Status: {status.get('status')} - Progress: {status.get('progress', 0):.1f}%")
        
        print("   (Test execution continues in background...)")
        return True
    else:
        print(f"❌ Test execution failed: {response.status_code}")
        return False

def test_reports():
    print("\n📊 Testing reports endpoint...")
    response = requests.get(f"{BASE_URL}/api/reports")
    if response.status_code == 200:
        data = response.json()
        reports = data.get("reports", [])
        print(f"✅ Found {len(reports)} report(s)")
        return True
    else:
        print(f"❌ Reports endpoint failed: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print("🎮 Multi-Agent Game Tester POC - System Test")
    print("=" * 60)
    
    if not test_server_running():
        print("\n⚠️  Please start the server first:")
        print("   Windows: Run 'start.bat'")
        print("   Linux/Mac: cd backend && python main.py")
        sys.exit(1)
    
    results = []
    results.append(test_generate_plan())
    results.append(test_execute_tests())
    results.append(test_reports())
    
    print("\n" + "=" * 60)
    print("📈 Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✨ All tests passed! The application is working correctly.")
        print("\n📌 Next steps:")
        print("1. Open http://localhost:8000 in your browser")
        print("2. Click 'Generate Test Plan' to create 20+ tests")
        print("3. Click 'Execute Top 10 Tests' to run them")
        print("4. View the generated reports")
    else:
        print("\n⚠️  Some tests failed. Please check the logs above.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()