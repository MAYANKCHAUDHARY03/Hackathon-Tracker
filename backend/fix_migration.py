import re
import os

migration_dir = "alembic/versions"
files = [f for f in os.listdir(migration_dir) if f.endswith("_graph_models.py")]
if not files:
    print("No migration file found")
    exit(1)

filename = os.path.join(migration_dir, files[0])
with open(filename, "r") as f:
    content = f.read()

# We need to remove blocks like:
# with op.batch_alter_table('table_name', schema=None) as batch_op:
#     batch_op.alter_column(...)
# We can use regex to remove everything from 'with op.batch_alter_table' up to the next non-indented line or end of function

def remove_batch_alters(text):
    lines = text.split('\n')
    new_lines = []
    in_batch_alter = False
    for line in lines:
        if line.strip().startswith("with op.batch_alter_table"):
            in_batch_alter = True
            continue
        if in_batch_alter:
            if line.strip() == "" or line.startswith("    ") or line.startswith("\t"):
                continue
            else:
                in_batch_alter = False
        
        # also ignore op.drop_index if it's outside batch
        if "op.drop_index" in line:
            continue
            
        new_lines.append(line)
    return '\n'.join(new_lines)

new_content = remove_batch_alters(content)

with open(filename, "w") as f:
    f.write(new_content)

print(f"Fixed migration file: {filename}")
