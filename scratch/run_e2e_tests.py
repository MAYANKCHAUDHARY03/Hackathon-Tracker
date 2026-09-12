import asyncio
from playwright.async_api import async_playwright

async def main():
    results = {}
    
    def record_pass(step, details=""):
        results[step] = "PASS"
        print(f"[PASS] {step}: {details}")
        
    def record_fail(step, details=""):
        results[step] = "FAIL"
        print(f"[FAIL] {step}: {details}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        console_errors = []
        unexpected_422 = False
        unexpected_404 = False
        unexpected_500 = False

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        
        async def on_response(response):
            nonlocal unexpected_422, unexpected_404, unexpected_500
            if "api/v1" in response.url:
                if response.status == 422:
                    print(f"UNEXPECTED 422: {response.url}")
                    unexpected_422 = True
                if response.status == 404:
                    print(f"UNEXPECTED 404: {response.url}")
                    unexpected_404 = True
                if response.status >= 500:
                    print(f"UNEXPECTED {response.status}: {response.url}")
                    unexpected_500 = True

        page.on("response", on_response)

        import random
        user_email = f"test_{random.randint(1000,9999)}@example.com"

        try:
            print("Registering user...")
            await page.goto("http://localhost:5174/register")
            await page.wait_for_selector("text=Create a new account")
            
            await page.fill("input[name='full_name']", "E2E User")
            await page.fill("input[type='email']", user_email)
            await page.fill("input[type='password']", "password123")
            await page.click("button[type='submit']")
            
            await page.wait_for_selector("text='Organization'", timeout=5000)
            await page.click("button:has-text('Organization')")
            
            # Wait for Dashboard to load (it might be the empty state or the real dashboard)
            await page.wait_for_selector("h1:has-text('Dashboard'), h2:has-text('Welcome to HackTracker')", timeout=5000)
            record_pass("Registration & Login", "Successfully registered and reached dashboard as Org")
            
            # --- 1. CREATE HACKATHON ---
            await page.click("a[href='/hackathons']")
            await page.wait_for_selector("text=Create Program", state="visible", timeout=5000)
            await page.get_by_role("button", name="Create Program", exact=True).click()
            
            await page.wait_for_selector("text=Create Program", state="visible", timeout=5000)
            await page.wait_for_selector("button:has-text('Next Step')", state="visible", timeout=5000)
            await page.wait_for_timeout(500)
            
            await page.get_by_role("button", name="Next Step").click(force=True)
            
            await page.wait_for_selector("#name", state="visible")
            await page.fill("#name", "E2E Test Hackathon")
            await page.fill("#description", "E2E description")
            await page.fill("#start_date", "2027-01-01")
            await page.fill("#end_date", "2027-01-03")
            await page.wait_for_timeout(500)
            
            await page.get_by_role("button", name="Create Program").click(force=True)
            await page.wait_for_selector("text=E2E Test Hackathon")
            record_pass("Hackathon Create", "Hackathon created successfully")
            
            # --- 2. SWITCH TO STUDENT MODE ---
            # We must be in Student mode to see the "Create Team" button.
            await page.goto("http://localhost:5174/mode-selection")
            await page.wait_for_selector("text='Student / Participant'", timeout=5000)
            await page.click("button:has-text('Student / Participant')")
            await page.wait_for_selector("h1:has-text('Dashboard')", timeout=5000)
            record_pass("Mode Switch", "Switched to Student mode")

            # --- 3. CREATE TEAM ---
            await page.click("a[href='/teams']")
            await page.wait_for_selector("text=Team Database", timeout=5000)
            
            async with page.expect_response(lambda r: "teams" in r.url and r.request.method == "POST") as res_info:
                await page.get_by_role("button", name="Create Team").first.click()
                await page.fill("input[name='name']", "E2E Test Team")
                await page.fill("textarea[name='description']", "This is an E2E test team.")
                
                # Hackathon should be in the dropdown
                await page.select_option("select[name='hackathon_id']", label="E2E Test Hackathon")
                
                await page.click("button[type='submit']")
                
            response = await res_info.value
            assert response.status in (200, 201)
            record_pass("Team Create", "POST returned success")
            
            await page.wait_for_selector("text=E2E Test Team")
            record_pass("Team UI Update", "Team appeared immediately")

            # --- 4. CREATE PROJECT ---
            await page.click("a[href='/projects']")
            await page.wait_for_selector("text=Create Project", timeout=5000)
            
            async with page.expect_response(lambda r: "projects" in r.url and r.request.method == "POST") as res_info:
                await page.click("text=Create Project")
                await page.fill("input[type='text']", "E2E Test Project")
                
                # We need to select the Hackathon AND the Team
                await page.select_option("select[name='hackathon_id']", label="E2E Test Hackathon")
                await page.select_option("select[name='team_id']", label="E2E Test Team")
                
                await page.fill("textarea", "E2E project desc")
                await page.click("button[type='submit']")
                
            response = await res_info.value
            assert response.status in (200, 201)
            record_pass("Project Create", "POST returned success")
            
            await page.wait_for_selector("text=E2E Test Project")
            record_pass("Project UI Update", "Project appeared immediately")
            
            # --- FINAL CHECKS ---
            if not unexpected_422: record_pass("Unexpected 422", "No unexpected 422s occurred")
            if not unexpected_404: record_pass("Unexpected 404", "No unexpected 404s occurred")
            if not unexpected_500: record_pass("Unexpected 500", "No unexpected 500s occurred")
            
        except Exception as e:
            print(f"Script failed: {e}")
            import traceback
            traceback.print_exc()
            content = await page.content()
            with open("error_snapshot.html", "w", encoding="utf-8") as f:
                f.write(content)
        
        await browser.close()
        
        print("\n\nFINAL ACCEPTANCE MATRIX\n")
        print("\n".join(f"{k.ljust(30)} {v}" for k, v in results.items()))

if __name__ == "__main__":
    asyncio.run(main())
