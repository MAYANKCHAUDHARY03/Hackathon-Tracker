import os
import re

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return

    original_content = content
    
    if 'timezone.utc' in content:
        # Check if timezone is imported from datetime
        has_import = bool(re.search(r'^from datetime import .*?\btimezone\b', content, re.MULTILINE))
        if not has_import:
            if 'from datetime import' in content:
                # Add timezone to the FIRST existing import of datetime
                content = re.sub(r'^(from datetime import.*?)$', lambda m: m.group(1) + ', timezone', content, count=1, flags=re.MULTILINE)
            else:
                # Add new import at the top
                content = "from datetime import timezone\n" + content
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated imports in {filepath}")

def main():
    for root, dirs, files in os.walk('backend/app'):
        for file in files:
            if file.endswith('.py'):
                process_file(os.path.join(root, file))
    for root, dirs, files in os.walk('backend/tests'):
        for file in files:
            if file.endswith('.py'):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
