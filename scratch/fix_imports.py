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
        # Check if timezone is imported
        if not re.search(r'\btimezone\b', content[:content.find('timezone.utc')]):
            # Needs import
            if 'from datetime import' in content:
                # Add timezone to existing import
                content = re.sub(r'(from datetime import .*?)$', lambda m: m.group(1) + ', timezone' if 'timezone' not in m.group(1) else m.group(1), content, count=1, flags=re.MULTILINE)
            else:
                # Add new import
                content = "from datetime import timezone\n" + content
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated imports in {filepath}")

def main():
    for root, dirs, files in os.walk('backend'):
        for file in files:
            if file.endswith('.py'):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
