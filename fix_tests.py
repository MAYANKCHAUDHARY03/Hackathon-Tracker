import os
import re

test_dir = r"c:\Hackathon tracker\hackathon-tracker\backend\tests\api"
count = 0
for root, _, files in os.walk(test_dir):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            
            if "def _override_access():\n        return True" in content:
                replacement = '''class MockMembership:
        def __init__(self, user, workspace_id, role="admin"):
            self.user = user
            self.workspace_id = workspace_id
            self.role = role
    def _override_access():
        return MockMembership(MockUser(id=mock_user_id, email="test@test.com"), uuid.uuid4())'''
                new_content = content.replace("def _override_access():\n        return True", replacement)
                with open(path, "w", encoding="utf-8") as file:
                    file.write(new_content)
                count += 1
print(f"Updated {count} files")
