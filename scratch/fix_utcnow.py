import os
import re

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping {filepath} due to decode error")
        return

    original_content = content
    
    # 1. Add timezone import if not present
    if 'from datetime import ' in content and 'timezone' not in content:
        content = re.sub(r'from datetime import (.*?)$', lambda m: f"from datetime import {m.group(1)}, timezone" if 'timezone' not in m.group(1) else m.group(0), content, count=1, flags=re.MULTILINE)
    elif 'import datetime' in content and 'timezone' not in content:
        # Just use datetime.timezone.utc
        pass
        
    # Some files use `from datetime import datetime, timedelta`
    if 'datetime.utcnow' in content and 'timezone' not in content:
        # add from datetime import timezone
        if 'import datetime' not in content and 'from datetime import' not in content:
            content = "from datetime import datetime, timezone\n" + content
        elif 'from datetime import' in content:
             content = re.sub(r'from datetime import (.*?)$', lambda m: f"from datetime import {m.group(1)}, timezone" if 'timezone' not in m.group(1) else m.group(0), content, count=1, flags=re.MULTILINE)

    # 2. Replace usages
    content = content.replace('datetime.utcnow()', 'datetime.now(timezone.utc)')
    content = content.replace('datetime.datetime.utcnow()', 'datetime.datetime.now(datetime.timezone.utc)')
    content = content.replace('default=datetime.utcnow', 'default=lambda: datetime.now(timezone.utc)')
    content = content.replace('default_factory=datetime.utcnow', 'default_factory=lambda: datetime.now(timezone.utc)')
    content = content.replace('onupdate=datetime.utcnow', 'onupdate=lambda: datetime.now(timezone.utc)')
    content = content.replace('default=datetime.datetime.utcnow', 'default=lambda: datetime.datetime.now(datetime.timezone.utc)')
    content = content.replace('onupdate=datetime.datetime.utcnow', 'onupdate=lambda: datetime.datetime.now(datetime.timezone.utc)')

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

def main():
    for root, dirs, files in os.walk('backend'):
        for file in files:
            if file.endswith('.py'):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
