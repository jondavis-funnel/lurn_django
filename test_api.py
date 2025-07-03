#!/usr/bin/env python
"""Quick test script to verify API endpoints"""

import httpx
import json

BASE_URL = "http://localhost:8000/api"

def test_api():
    print("Testing Django Tutorial API Endpoints...")
    print("=" * 50)
    
    # Test modules endpoint
    print("\n1. Testing Modules Endpoint:")
    response = httpx.get(f"{BASE_URL}/modules/")
    if response.status_code == 200:
        modules = response.json()
        print(f"✓ Found {len(modules)} modules")
        for module in modules:
            lessons_count = module.get('lessons_count', len(module.get('lessons', [])))
            print(f"  - {module['title']} ({lessons_count} lessons)")
    else:
        print(f"✗ Error: {response.status_code}")
    
    # Test lessons endpoint
    print("\n2. Testing Lessons Endpoint:")
    response = httpx.get(f"{BASE_URL}/lessons/")
    if response.status_code == 200:
        lessons = response.json()
        print(f"✓ Found {len(lessons)} lessons")
        for lesson in lessons[:3]:  # Show first 3
            print(f"  - {lesson['title']}")
    else:
        print(f"✗ Error: {response.status_code}")
    
    # Test specific module
    print("\n3. Testing Specific Module:")
    response = httpx.get(f"{BASE_URL}/modules/1/")
    if response.status_code == 200:
        module = response.json()
        print(f"✓ Module: {module['title']}")
        print(f"  Lessons: {len(module.get('lessons', []))}")
        print(f"  Estimated time: {module['estimated_minutes']} minutes")
    else:
        print(f"✗ Error: {response.status_code}")

if __name__ == "__main__":
    test_api()
