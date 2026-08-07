import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000/api/v1") as client:
        # 1. Login
        resp = await client.post("/auth/login", json={"email": "founder@example.com", "password": "securepassword123"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get Workspaces
        resp = await client.get("/workspaces", headers=headers)
        workspaces = resp.json()
        if not workspaces:
            print("No workspaces found.")
            return
        ws_id = workspaces[0]["id"]
        headers["x-workspace-id"] = ws_id
        
        # 3. Create Automation Rule
        rule_payload = {
            "name": "Test Notify",
            "trigger_type": "submission_created",
            "action_type": "send_notification",
            "conditions": {},
            "enabled": True
        }
        print("Creating automation rule...")
        resp = await client.post(f"/workspaces/{ws_id}/automation/rules", headers=headers, json=rule_payload)
        print(f"Rule create status: {resp.status_code}")
        if resp.status_code == 201:
            rule_id = resp.json()["id"]
            print(f"Created rule {rule_id}")
            
            # Wait for any previous background tasks (just in case)
            await asyncio.sleep(1)
            
            # Get executions
            resp = await client.get(f"/workspaces/{ws_id}/automation/rules/{rule_id}/executions", headers=headers)
            print(f"Executions before trigger: {len(resp.json())}")
            
        else:
            print(f"Failed to create rule: {resp.text}")

if __name__ == "__main__":
    asyncio.run(main())
