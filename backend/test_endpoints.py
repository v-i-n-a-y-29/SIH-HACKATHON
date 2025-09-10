import requests
import os
import json
from pathlib import Path

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def test_forecast_endpoint():
    print("\n===== Testing Forecast Endpoint =====")
    endpoint = f"{BASE_URL}/forecast/predict"
    
    # Path to the test data file
    data_dir = Path(__file__).resolve().parent / "data"
    
    # Make sure we have the test files
    csv_file = data_dir / "ocean_dataset_cleaned.csv"
    if not csv_file.exists():
        print(f"Error: Test data file not found at {csv_file}")
        return False
    
    # Test with just the main dataset
    files = {
        'file': (csv_file.name, open(csv_file, 'rb'), 'text/csv')
    }
    
    try:
        response = requests.post(endpoint, files=files)
        print(f"Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Forecast RMSE: {result.get('rmse', 'N/A')}")
            print(f"Forecast MAE: {result.get('mae', 'N/A')}")
            print("Forecast endpoint test passed!")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing forecast endpoint: {e}")
        return False
    finally:
        # Close open file
        files['file'][1].close()

def test_edna_endpoint():
    print("\n===== Testing eDNA Analysis Endpoint =====")
    endpoint = f"{BASE_URL}/edna/analyze"
    
    # Create a simple FASTA file for testing
    test_fasta = """
>Pterois_volitans|INVASIVE_INDIAN_OCEAN|Red_Lionfish
ATGGTCCTACCTGCTCTAGGAGACGACCAAATTTATAATGTAATCGTAACCGCACATGCC
TTCGTAATAATTTTCTTTATAGTAATACCAATTATAATTGGAGGGTTCGGAAACTGACTT
GTACCACTAATAATTGGAGCCCCAGATATAGCATTCCCACGAATAAATAACATAAGCTTC
TGACTACTACCCCCATCTTTCCTACTACTACTAGCCTCTTCTGGTGTTGAAGCCGGAGCA
>Epinephelus_coioides|NATIVE_INDIAN_OCEAN|Orange-spotted_Grouper
ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT
ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT
ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT
ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT
"""
    test_fasta_path = Path(__file__).resolve().parent / "test_edna.fasta"
    
    with open(test_fasta_path, 'w') as f:
        f.write(test_fasta)
    
    try:
        # Test with the created FASTA file
        files = {
            'file': (test_fasta_path.name, open(test_fasta_path, 'rb'), 'text/plain')
        }
        
        response = requests.post(endpoint, files=files)
        print(f"Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Detected species: {len(result.get('detected_species', []))}")
            print(f"Invasive species: {len(result.get('invasive_species', []))}")
            print("eDNA analysis endpoint test passed!")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing eDNA endpoint: {e}")
        return False
    finally:
        # Close open file
        if 'file' in locals() and hasattr(files['file'][1], 'close'):
            files['file'][1].close()
        # Clean up test file
        if test_fasta_path.exists():
            test_fasta_path.unlink()

def main():
    print("Testing Ocean AI Prototype API endpoints...")
    
    # Test forecast endpoint
    forecast_result = test_forecast_endpoint()
    
    # Test eDNA endpoint
    edna_result = test_edna_endpoint()
    
    # Print summary
    print("\n===== Test Summary =====")
    print(f"Forecast Endpoint: {'PASSED' if forecast_result else 'FAILED'}")
    print(f"eDNA Analysis Endpoint: {'PASSED' if edna_result else 'FAILED'}")
    
    if forecast_result and edna_result:
        print("\nAll tests passed! The API is working correctly.")
    else:
        print("\nSome tests failed. Please check the logs for details.")

if __name__ == "__main__":
    main()
