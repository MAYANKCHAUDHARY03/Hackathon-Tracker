import asyncio
from sqlalchemy import Column, JSON, String, select, cast, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

Base = declarative_base()
class T(Base):
    __tablename__ = 't'
    id = Column(String, primary_key=True)
    properties = Column(JSON)

async def main():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    Session = async_sessionmaker(engine)
    async with Session() as session:
        t = T(id='1', properties={'domain': 'Climate'})
        session.add(t)
        await session.commit()
        
        expr = func.trim(cast(T.properties['domain'], String), '"')
        stmt = select(T).where(expr == 'Climate')
        res = await session.execute(stmt)
        print('RESULT:', res.scalars().all())

asyncio.run(main())
