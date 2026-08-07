import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def run_rehearsal():
    print("Starting Staging Rehearsal (API End-to-End)...")
    
    # 1. Register & Login
    # We will skip register if user exists or just use a dummy register
    email = f"test_{int(time.time())}@example.com"
    password = "password123"
    
    res = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password, "full_name": "E2E User"})
    if res.status_code not in (200, 201):
        print("Failed to register:", res.json())
        return
    print("User registered.")
    
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if res.status_code != 200:
        print("Failed to login:", res.json())
        return
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("User logged in.")
    
    # 2. Create Workspace
    res = requests.post(f"{BASE_URL}/workspaces", json={"name": "E2E Workspace", "slug": f"e2e-{int(time.time())}"}, headers=headers)
    if res.status_code != 200:
        print("Failed to create workspace:", res.json())
        return
    workspace_id = res.json()["id"]
    print(f"Workspace created: {workspace_id}")
    
    # 3. Create Hackathon
    res = requests.post(f"{BASE_URL}/hackathons", json={
        "workspace_id": workspace_id,
        "name": "E2E Hackathon",
        "description": "Staging test",
        "start_date": "2026-09-01T00:00:00Z",
        "end_date": "2026-09-03T00:00:00Z"
    }, headers=headers)
    if res.status_code != 200:
        print("Failed to create hackathon:", res.json())
        return
    hackathon_id = res.json()["id"]
    print(f"Hackathon created: {hackathon_id}")
    
    # 4. Create Team
    res = requests.post(f"{BASE_URL}/teams", json={
        "hackathon_id": hackathon_id,
        "name": "E2E Team"
    }, headers=headers)
    if res.status_code != 200:
        print("Failed to create team:", res.json())
        return
    team_id = res.json()["id"]
    print(f"Team created: {team_id}")
    
    print("✅ Staging Rehearsal Completed Successfully.")

if __name__ == "__main__":
    try:
        run_rehearsal()
    except Exception as e:
        print("Rehearsal failed due to connection error. Ensure the server is running.")
