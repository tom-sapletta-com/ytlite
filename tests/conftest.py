import pytest
import subprocess
import time
import requests
from pathlib import Path
import os

# Define the port for the test server
TEST_PORT = 5001

@pytest.fixture(scope="session")
def live_server():
    """Fixture to run the Flask app in a separate process for E2E tests."""
    
    # Command to run the Flask app
    run_script = Path(__file__).parent.parent / "run_new_gui.py"
    command = ["python3", str(run_script)]
    
    # Set environment variables for the test server
    env = os.environ.copy()
    env["FLASK_RUN_PORT"] = str(TEST_PORT)
    test_output_dir = Path(__file__).parent / "output"
    test_output_dir.mkdir(exist_ok=True)
    env["YTLITE_OUTPUT_DIR"] = str(test_output_dir)
    env["YTLITE_FAST_TEST"] = "1"

    server_process = None
    try:
        print(f"\n🚀 Starting test server with command: {' '.join(command)}")
        print(f"Environment variables: FLASK_RUN_PORT={env.get('FLASK_RUN_PORT')}, YTLITE_FAST_TEST={env.get('YTLITE_FAST_TEST')}")
        
        server_process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Server process started with PID: {server_process.pid}")
        
        retries = 15
        while retries > 0:
            try:
                response = requests.get(f"http://localhost:{TEST_PORT}/health")
                if response.status_code == 204:
                    print(f"\n✅ Test server is running on http://localhost:{TEST_PORT}")
                    break
                else:
                    print(f"Health check returned status: {response.status_code}")
            except requests.ConnectionError:
                print(f"Connection attempt failed, retries left: {retries}")
                time.sleep(1)
                retries -= 1
        else:
            print("❌ Server failed to start within timeout")
            if server_process.poll() is None:
                stdout, stderr = server_process.communicate(timeout=5)
            else:
                stdout = server_process.stdout.read() if server_process.stdout else b""
                stderr = server_process.stderr.read() if server_process.stderr else b""
            
            print(f"Server stdout:\n{stdout.decode()}")
            print(f"Server stderr:\n{stderr.decode()}")
            print(f"Server return code: {server_process.returncode}")
            pytest.fail("Could not start the test server.")

        yield f"http://localhost:{TEST_PORT}"

    finally:
        if server_process:
            print("\n🛑 Stopping test server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("\n🛑 Test server stopped.")
