import os, glob

for f in glob.glob('tests/*.py'):
    with open(f, 'r') as file:
        content = file.read()
    
    content = content.replace('/hackathons/"', '/hackathons"')
    content = content.replace('/rounds/"', '/rounds"')
    content = content.replace('/hackathons/?', '/hackathons?')
    
    with open(f, 'w') as file:
        file.write(content)
