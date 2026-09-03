import asyncio
from app.models import Base

def main():
    print("Tables registered in Base.metadata:")
    for t in Base.metadata.tables.keys():
        print(t)

if __name__ == "__main__":
    main()
