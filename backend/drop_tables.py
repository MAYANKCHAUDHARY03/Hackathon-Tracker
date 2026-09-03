import sqlite3

tables_to_drop = [
    'portable_identities',
    'verified_skills',
    'organization_trusts',
    'trust_verifications',
    'project_impacts',
    'ontology_entities',
    'custom_metrics',
    'forecasts',
    'platform_events',
    'funding_opportunities',
    '_alembic_tmp_achievements'
]

conn = sqlite3.connect('c:/Hackathon tracker/hackathon-tracker/backend/hackathon.db')
c = conn.cursor()

for table in tables_to_drop:
    try:
        c.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"Dropped {table}")
    except Exception as e:
        print(f"Failed to drop {table}: {e}")

conn.commit()
conn.close()
