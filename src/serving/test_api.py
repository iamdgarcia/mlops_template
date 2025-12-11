"""
Test script for the Fraud Detection API

This script tests the serving API with various transaction scenarios
to ensure proper functionality and performance.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


class FraudDetectionAPITester:
    """Test client for the Fraud Detection API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_health(self) -> Dict:
        """Test the health endpoint"""
        print("Testing health endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            health_data = response.json()
            print(f"[OK] Health check passed: {health_data['status']}")
            return health_data
        except Exception as e:
            print(f"[ERROR] Health check failed: {str(e)}")
            return {}

    def test_root(self) -> Dict:
        """Test the root endpoint"""
        print("Testing root endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/")
            response.raise_for_status()
            root_data = response.json()
            print(f"[OK] Root endpoint accessible: {root_data['message']}")
            return root_data
        except Exception as e:
            print(f"[ERROR] Root endpoint failed: {str(e)}")
            return {}

    def create_test_transaction(self, fraud_indicators: Optional[Dict] = None) -> Dict:
        """Create a test transaction with optional fraud indicators"""

        base_transaction = {
            "amount": 100.0,
            "merchant_category": "grocery",
            "transaction_type": "purchase",
            "location": "seattle_wa",
            "device_type": "mobile",
            "hour_of_day": 14,
            "day_of_week": 2,
            "user_transaction_frequency": 5.0,
            "user_avg_amount": 85.0,
            "user_transaction_count": 25,
        }

        # Apply fraud indicators if provided
        if fraud_indicators:
            base_transaction.update(fraud_indicators)

        return base_transaction

    def test_prediction(self, transaction: Dict) -> Dict:
        """Test a single prediction"""
        try:
            response = self.session.post(
                f"{self.base_url}/predict",
                json=transaction,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Prediction failed: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Response: {e.response.text}")
            return {}

    def test_normal_transactions(self) -> List[Dict]:
        """Test normal (non-fraudulent) transactions"""
        print("\nTesting normal transactions...")

        normal_scenarios = [
            {
                "name": "Regular grocery purchase",
                "transaction": self.create_test_transaction(
                    {
                        "amount": 45.67,
                        "merchant_category": "grocery",
                        "hour_of_day": 10,
                        "user_avg_amount": 50.0,
                    }
                ),
            },
            {
                "name": "Coffee shop purchase",
                "transaction": self.create_test_transaction(
                    {
                        "amount": 5.25,
                        "merchant_category": "restaurant",
                        "hour_of_day": 8,
                        "user_avg_amount": 25.0,
                    }
                ),
            },
            {
                "name": "Gas station purchase",
                "transaction": self.create_test_transaction(
                    {
                        "amount": 35.00,
                        "merchant_category": "gas_station",
                        "hour_of_day": 17,
                        "user_avg_amount": 40.0,
                    }
                ),
            },
        ]

        results = []
        for scenario in normal_scenarios:
            print(f"  - {scenario['name']}")
            prediction = self.test_prediction(scenario["transaction"])
            if prediction:
                print(f"    - Fraud probability: {prediction['fraud_probability']:.4f}")
                print(f"    - Is fraud: {prediction['is_fraud']}")
                print(f"    - Risk level: {prediction['risk_level']}")
                print(f"    - Processing time: {prediction['processing_time_ms']:.2f}ms")
                results.append({**scenario, "prediction": prediction})
            print()

        return results

    def test_suspicious_transactions(self) -> List[Dict]:
        """Test suspicious (potentially fraudulent) transactions"""
        print("\nTesting suspicious transactions...")

        suspicious_scenarios = [
            {
                "name": "Large amount at unusual hour",
                "transaction": self.create_test_transaction(
                    {
                        "amount": 2500.0,
                        "merchant_category": "online",
                        "hour_of_day": 3,
                        "user_avg_amount": 100.0,
                    }
                ),
            },
            {
                "name": "Very high amount vs user average",
                "transaction": self.create_test_transaction(
                    {
                        "amount": 5000.0,
                        "merchant_category": "retail",
                        "hour_of_day": 15,
                        "user_avg_amount": 50.0,
                    }
                ),
            },
            {
                "name": "Unusual device type",
                "transaction": self.create_test_transaction(
                    {
                        "amount": 1500.0,
                        "merchant_category": "entertainment",
                        "device_type": "atm",
                        "hour_of_day": 2,
                        "user_avg_amount": 200.0,
                    }
                ),
            },
        ]

        results = []
        for scenario in suspicious_scenarios:
            print(f"  - {scenario['name']}")
            prediction = self.test_prediction(scenario["transaction"])
            if prediction:
                print(f"    - Fraud probability: {prediction['fraud_probability']:.4f}")
                print(f"    - Is fraud: {prediction['is_fraud']}")
                print(f"    - Risk level: {prediction['risk_level']}")
                print(f"    - Processing time: {prediction['processing_time_ms']:.2f}ms")
                results.append({**scenario, "prediction": prediction})
            print()

        return results

    def test_performance(self, num_requests: int = 100) -> Dict:
        """Test API performance with multiple concurrent requests"""
        print(f"\nTesting performance with {num_requests} requests...")

        transaction = self.create_test_transaction()
        start_time = time.time()

        successful_requests = 0
        total_processing_time = 0

        for i in range(num_requests):
            prediction = self.test_prediction(transaction)
            if prediction:
                successful_requests += 1
                total_processing_time += prediction.get("processing_time_ms", 0)

            if (i + 1) % 10 == 0:
                print(f"  [METRIC] Completed {i + 1}/{num_requests} requests")

        end_time = time.time()
        total_time = end_time - start_time

        metrics = {
            "total_requests": num_requests,
            "successful_requests": successful_requests,
            "failed_requests": num_requests - successful_requests,
            "success_rate": successful_requests / num_requests,
            "total_time_seconds": total_time,
            "requests_per_second": num_requests / total_time,
            "avg_processing_time_ms": total_processing_time / successful_requests
            if successful_requests > 0
            else 0,
        }

        print(f"[OK] Performance test completed:")
        print(f"  - Success rate: {metrics['success_rate']:.2%}")
        print(f"  - Requests per second: {metrics['requests_per_second']:.2f}")
        print(f"  - Average processing time: {metrics['avg_processing_time_ms']:.2f}ms")

        return metrics

    def test_input_validation(self) -> List[Dict]:
        """Test input validation with invalid data"""
        print("\nTesting input validation...")

        invalid_scenarios = [
            {
                "name": "Negative amount",
                "transaction": self.create_test_transaction({"amount": -100.0}),
                "should_fail": True,
            },
            {
                "name": "Invalid merchant category",
                "transaction": self.create_test_transaction(
                    {"merchant_category": "invalid_category"}
                ),
                "should_fail": True,
            },
            {
                "name": "Invalid hour",
                "transaction": self.create_test_transaction({"hour_of_day": 25}),
                "should_fail": True,
            },
            {
                "name": "Missing required field",
                "transaction": {
                    k: v for k, v in self.create_test_transaction().items() if k != "amount"
                },
                "should_fail": True,
            },
        ]

        results = []
        for scenario in invalid_scenarios:
            print(f"  - {scenario['name']}")
            try:
                response = self.session.post(
                    f"{self.base_url}/predict",
                    json=scenario["transaction"],
                    headers={"Content-Type": "application/json"},
                )

                if scenario["should_fail"] and response.status_code == 200:
                    print(f"    [ERROR] Expected failure but request succeeded")
                elif not scenario["should_fail"] and response.status_code != 200:
                    print(
                        f"    [ERROR] Expected success but request failed: {response.status_code}"
                    )
                else:
                    print(f"    [OK] Validation worked as expected")

                results.append(
                    {
                        **scenario,
                        "status_code": response.status_code,
                        "response": response.json()
                        if response.status_code == 200
                        else response.text,
                    }
                )

            except Exception as e:
                if scenario["should_fail"]:
                    print(f"    [OK] Validation failed as expected: {str(e)}")
                else:
                    print(f"    [ERROR] Unexpected error: {str(e)}")
                results.append({**scenario, "error": str(e)})
            print()

        return results

    def get_metrics(self) -> Dict:
        """Get API metrics"""
        try:
            response = self.session.get(f"{self.base_url}/metrics")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to get metrics: {str(e)}")
            return {}

    def run_comprehensive_test(self) -> Dict:
        """Run comprehensive API test suite"""
        print("[START] Starting comprehensive API test suite...")
        print("=" * 60)

        results = {"timestamp": datetime.now().isoformat(), "test_results": {}}

        # Test health and connectivity
        results["test_results"]["health"] = self.test_health()
        results["test_results"]["root"] = self.test_root()

        if not results["test_results"]["health"]:
            print("[ERROR] API is not healthy. Stopping tests.")
            return results

        # Test normal transactions
        results["test_results"]["normal_transactions"] = self.test_normal_transactions()

        # Test suspicious transactions
        results["test_results"]["suspicious_transactions"] = self.test_suspicious_transactions()

        # Test input validation
        results["test_results"]["input_validation"] = self.test_input_validation()

        # Test performance
        results["test_results"]["performance"] = self.test_performance(50)

        # Get final metrics
        results["test_results"]["final_metrics"] = self.get_metrics()

        print("\n[DONE] Comprehensive test suite completed!")
        print("=" * 60)

        return results


def save_test_results(results: Dict, filename: Optional[str] = None):
    """Save test results to file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(results, f, indent=2)

    print(f"[FILE] Test results saved to: {filename}")


def main():
    """Main test execution"""
    print("[INFO] Fraud Detection API Test Suite")
    print("=" * 60)

    # Initialize tester
    tester = FraudDetectionAPITester()

    # Run comprehensive tests
    results = tester.run_comprehensive_test()

    # Save results
    save_test_results(results)

    # Print summary
    print("\n[METRIC] Test Summary:")
    if results["test_results"].get("health", {}).get("status") == "healthy":
        print("[OK] API Health: Healthy")
    else:
        print("[ERROR] API Health: Unhealthy")

    normal_count = len(results["test_results"].get("normal_transactions", []))
    suspicious_count = len(results["test_results"].get("suspicious_transactions", []))
    print(f"[OK] Normal transactions tested: {normal_count}")
    print(f"[OK] Suspicious transactions tested: {suspicious_count}")

    perf_metrics = results["test_results"].get("performance", {})
    if perf_metrics:
        print(f"[SPEED] Performance: {perf_metrics.get('requests_per_second', 0):.2f} req/s")
        print(f"[TIME]  Avg processing time: {perf_metrics.get('avg_processing_time_ms', 0):.2f}ms")


if __name__ == "__main__":
    main()
