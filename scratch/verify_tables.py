import sqlite3
import os

db_path = 'test_db.sqlite'
if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cursor.fetchall()]

required = [
    'developer_apps', 'webhook_endpoints', 'trust_verifications', 
    'data_subject_requests', 'consent_records', 'governance_audit_logs', 
    'security_incidents', 'notification_preferences'
]

for req in required:
    print(f"{req}: {'YES' if req in tables else 'NO'}")
