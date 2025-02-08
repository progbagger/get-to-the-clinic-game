from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from functools import wraps

connection_string = "sqlite+aiosqlite:///db.db"
engine = create_async_engine(
    connection_string,
    echo=True,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class DatabaseManager:

    def __init__(self):
        pass


def create_session(func):
    @wraps
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            # try:
            return await func(*args, **kwargs, session=session)
        # except Exception as e:
        #     await session.rollback()
        #     raise

    return wrapper
