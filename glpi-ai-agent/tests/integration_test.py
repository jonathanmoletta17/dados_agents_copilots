import time
import requests
import subprocess
import sys
import os
import signal
import json

# Configuration
MOCK_GLPI_PORT = 8090
AGENT_PORT = 8000
MOCK_GLPI_URL = f"http://127.0.0.1:{MOCK_GLPI_PORT}"
AGENT_URL = f"http://127.0.0.1:{AGENT_PORT}"

def wait_for_service(url, name, retries=10):
    print(f"Waiting for {name} at {url}...")
    for i in range(retries):
        try:
            requests.get(f"{url}/docs", timeout=2) # checking docs or root
            print(f"✅ {name} is up!")
            return True
        except:
            time.sleep(2)
    print(f"❌ {name} failed to start.")
    return False

def run_test():
    print("🚀 Starting Integration Test")

    # 1. Start Mock GLPI
    print("Starting Mock GLPI...")
    env_mock = os.environ.copy()
    mock_process = subprocess.Popen(
        [sys.executable, "tests/mocks/mock_glpi.py"],
        cwd=os.getcwd(),
        env=env_mock,
        # stdout=subprocess.DEVNULL, # Mute output to keep console clean, or remove for debug
        # stderr=subprocess.DEVNULL
    )

    # 2. Start AI Agent
    print("Starting AI Agent...")
    env_agent = os.environ.copy()
    # Override settings to point to Mock GLPI
    env_agent["GLPI_DTIC_URL"] = MOCK_GLPI_URL
    env_agent["GLPI_DTIC_APP_TOKEN"] = "mock_app"
    env_agent["GLPI_DTIC_USER_TOKEN"] = "mock_user"
    env_agent["AI_SERVICE_URL"] = "http://host.docker.internal:11434/api/generate" # Assuming local ollama is running default
    # If host.docker.internal doesn't work on pure python windows, we might need localhost
    env_agent["AI_SERVICE_URL"] = "http://127.0.0.1:11434/api/generate"
    
    agent_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", str(AGENT_PORT)],
        cwd=os.getcwd(),
        env=env_agent,
        # stdout=subprocess.DEVNULL, 
        # stderr=subprocess.DEVNULL
    )

    try:
        # Wait for services
        if not wait_for_service(MOCK_GLPI_URL, "Mock GLPI") or not wait_for_service(AGENT_URL, "AI Agent"):
            return

        # 3. Trigger Webhook for Ticket 101 (Uncategorized)
        print("\n🧪 Test Case 1: Uncategorized Ticket (ID 101)")
        payload = {
            "event": "add",
            "itemtype": "Ticket",
            "items": [{"id": 101}]
        }
        
        try:
            resp = requests.post(f"{AGENT_URL}/api/v1/webhook/ticket", json=payload)
            print(f"Webhook Response: {resp.status_code} - {resp.json()}")
        except Exception as e:
            print(f"❌ Webhook call failed: {e}")
            return

        # 4. Wait for processing
        print("Waiting for background processing (5s)...")
        time.sleep(5)

        # 5. Check results in Mock GLPI
        resp = requests.get(f"{MOCK_GLPI_URL}/_debug/updates")
        updates = resp.json()
        
        print("\n📊 Verification Results:")
        found = False
        for update in updates:
            if update['ticket_id'] == 101:
                print(f"✅ Ticket 101 Updated! Data: {update['updates']}")
                found = True
                # Check if category is valid (should be something related to Internet/Rede)
                # Note: This depends on the actual AI model response. 
                # If AI fails or is offline, this might not happen.
                break
        
        if not found:
            print("❌ Ticket 101 was NOT updated. (Check AI service or logs)")
            # Check logs logic could be added here if we were capturing stdout

    finally:
        print("\n🧹 Cleaning up processes...")
        mock_process.terminate()
        agent_process.terminate()
        # On Windows terminate might not kill the tree, but for this simple script it's usually enough.

if __name__ == "__main__":
    # Ensure we are in the right directory
    if not os.path.exists("src/main.py"):
        print("❌ Please run this script from the project root (glpi-ai-agent)")
        sys.exit(1)
        
    run_test()
