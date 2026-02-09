from app.services.database import Database


async def run_migrations(db: Database):
    migrations = [
        """
        CREATE TABLE IF NOT EXISTS urls (
            short_id VARCHAR(10) PRIMARY KEY,
            original_url TEXT NOT NULL
        )
        """,
        """
            CREATE INDEX IF NOT EXISTS idx_urls_original_url 
            ON urls(original_url)
        """,
    ]

    for migration in migrations:
        await db.execute(migration)

    print("Migrations completed successfully")
