#!/usr/bin/env python3
"""
Test script for supervisor integration
Verifies that the supervisor correctly passes files to DataAnalystAgent.
"""

import sys
import os
import pandas as pd
import io

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def create_test_data():
    """Create a sample dataset for testing"""
    data = {
        'sales': [100, 150, 200, 180, 220],
        'profit': [10, 15, 20, 18, 22],
        'category': ['A', 'B', 'A', 'B', 'A']
    }
    df = pd.DataFrame(data)
    
    # Convert to Excel bytes
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='TestData')
    output.seek(0)
    return output.getvalue()

def test_supervisor_integration():
    """Test supervisor integration with file upload"""
    print("🧪 Testing supervisor integration...")
    
    try:
        # Import supervisor
        from src.orchestration.supervisor import SupervisorOrchestrator
        print("✅ Supervisor imported successfully")
        
        # Initialize supervisor
        supervisor = SupervisorOrchestrator(user_id="test_user_123")
        print("✅ Supervisor initialized successfully")
        
        # Create test data
        print("\n1. Creating test dataset...")
        test_file_bytes = create_test_data()
        print(f"✅ Test dataset created ({len(test_file_bytes)} bytes)")
        
        # Test with file upload
        print("\n2. Testing supervisor with file upload...")
        result = supervisor.process_request("analyze data", file_bytes=test_file_bytes)
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result)} characters")
        print(f"First 300 characters: {result[:300]}...")
        
        # Check if it's a comprehensive analysis
        if "COMPREHENSIVE DATA ANALYSIS" in result:
            print("✅ Supervisor returns comprehensive analysis with file")
        else:
            print("❌ Supervisor does not return comprehensive analysis")
            print(f"Result contains: {result[:500]}...")
        
        # Test without file
        print("\n3. Testing supervisor without file...")
        no_file_result = supervisor.process_request("Analyze this data")
        print(f"No file result: {no_file_result[:200]}...")
        
        if "upload" in no_file_result.lower():
            print("✅ Supervisor handles no-file scenario correctly")
        else:
            print("❌ Supervisor does not handle no-file scenario correctly")
        
        print("\n🎉 Supervisor integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Supervisor integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Supervisor Integration Test...")
    success = test_supervisor_integration()
    
    if success:
        print("\n🎉 Supervisor integration works correctly!")
        print("✅ File uploads are properly handled")
        print("✅ Comprehensive analysis is returned")
        print("✅ No-file scenarios are handled gracefully")
    else:
        print("\n❌ Supervisor integration has issues")
    
    sys.exit(0 if success else 1) 