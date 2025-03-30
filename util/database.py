import aiosqlite
import os

DB_PATH = os.path.join('data', "players.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                eos_id TEXT NOT NULL,
                steam_id TEXT NOT NULL UNIQUE
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                discord_id TEXT NOT NULL,
                steam_id TEXT,
                status TEXT NOT NULL
            )
            """
        )
        await db.commit()

async def add_player(name: str, eos_id: str, steam_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO players (name, eos_id, steam_id) VALUES (?, ?, ?)",
            (name, eos_id, steam_id)
        )
        await db.commit()

async def get_players():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name, eos_id, steam_id FROM players") as cursor:
            rows = await cursor.fetchall()
            return [{"Name": row[0], "EOS_Id": row[1], "Steam_Id": row[2]} for row in rows]

async def update_player(name: str, eos_id: str, steam_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE players SET name = ?, eos_id = ? WHERE steam_id = ?",
            (name, eos_id, steam_id)
        )
        await db.commit()

async def add_link(code: str, discord_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO links (code, discord_id, status) VALUES (?, ?, ?)",
            (code, discord_id, "pending")
        )
        await db.commit()

async def update_link(code: str, discord_id: str, steam_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE links SET steam_id = ?, status = ? WHERE code = ? AND discord_id = ? AND status = ?",
            (steam_id, "linked", code, discord_id, "pending")
        )
        await db.commit()

async def get_link(code: str, discord_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id, code, discord_id, steam_id, status FROM links WHERE code = ? AND discord_id = ?",
            (code, discord_id)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"id": row[0], "code": row[1], "discord_id": row[2], "steam_id": row[3], "status": row[4]}
            return None

# user profile stuff
async def user_profile(discord_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT links.steam_id, links.status, players.eos_id
            FROM links
            LEFT JOIN players ON links.steam_id = players.steam_id
            WHERE links.discord_id = ?
            """,
            (discord_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"steam_id": row[0], "status": row[1], "eos_id": row[2] if row[2] else "N/A"}
            return None
