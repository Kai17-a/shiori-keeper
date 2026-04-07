import sqlite3


class SettingsRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_api_base_url(self) -> str:
        row = self.conn.execute(
            "SELECT value FROM app_settings WHERE key = 'api_base_url'"
        ).fetchone()
        return row["value"]

    def set_api_base_url(self, value: str) -> str:
        self.conn.execute(
            "INSERT INTO app_settings (key, value) VALUES ('api_base_url', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (value,),
        )
        return self.get_api_base_url()
