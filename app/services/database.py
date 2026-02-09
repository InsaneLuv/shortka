import asyncio
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, List, Optional, Tuple


class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.local = threading.local()
        self.executor = ThreadPoolExecutor(max_workers=1)

    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        return self.local.conn

    async def connect(self):
        pass

    async def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:

        def _execute():
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _execute)

    async def executemany(self, query: str, params_list: List[Tuple]) -> sqlite3.Cursor:

        def _executemany():
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _executemany)

    async def executescript(self, script: str) -> sqlite3.Cursor:

        def _executescript():
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.executescript(script)
            conn.commit()
            return cursor

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _executescript)

    async def fetchall(self, query: str, params: Tuple = ()) -> List[Tuple]:
        cursor = await self.execute(query, params)

        def _fetchall():
            return cursor.fetchall()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _fetchall)

    async def fetchone(self, query: str, params: Tuple = ()) -> Optional[Tuple]:
        cursor = await self.execute(query, params)

        def _fetchone():
            return cursor.fetchone()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _fetchone)

    async def fetchmany(self, query: str, params: Tuple = (), size: int = 1) -> List[Tuple]:
        cursor = await self.execute(query, params)

        def _fetchmany():
            return cursor.fetchmany(size)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _fetchmany)

    async def fetchval(self, query: str, params: Tuple = ()) -> Any:
        result = await self.fetchone(query, params)
        return result[0] if result else None

    async def create_table(self, table_name: str, schema: str):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
        await self.execute(query)

    async def close(self):
        def _close():
            if hasattr(self.local, 'conn'):
                self.local.conn.close()
                delattr(self.local, 'conn')

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, _close)
        self.executor.shutdown(wait=True)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()