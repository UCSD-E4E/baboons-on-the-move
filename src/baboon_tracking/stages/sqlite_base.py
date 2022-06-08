from abc import ABC
from datetime import datetime
import json
from sqlite3 import Connection, Cursor, connect

import git
from library.config import get_config
from pipeline.parent_stage import ParentStage
from pipeline.pipeline import Pipeline
from pipeline.stage import Stage


class SqliteBase(Stage, ABC):
    created_metadata = False
    inserted_metadata = False

    connection: Connection = None
    cursor: Cursor = None

    def __init__(self):
        Stage.__init__(self)

        self.file_name = "./output/results.db"

    def __exit__(self, exc_type, exc_value, traceback):
        self.on_destroy()

    def before_database_create(self) -> None:
        """
        Called before the database file is created.
        """

    def on_database_create(self) -> None:
        """
        Called when the database file is created.
        """

    def _create_metadata_tables(self):
        if SqliteBase.created_metadata:
            return

        SqliteBase.cursor.execute(
            """CREATE TABLE IF NOT EXISTS metadata
                (run_key text, key text, value text)"""
        )

        SqliteBase.cursor.execute(
            """CREATE TABLE IF NOT EXISTS stages
                (run_key text, name text, sort_order int)"""
        )

        SqliteBase.cursor.execute(
            """DELETE FROM metadata
                WHERE run_key = ?""",
            (Pipeline.instance.name,),
        )

        SqliteBase.cursor.execute(
            """DELETE FROM stages
                WHERE run_key = ?""",
            (Pipeline.instance.name,),
        )

        SqliteBase.connection.commit()
        SqliteBase.created_metadata = True

    def _insert_start_metadata(self):
        if SqliteBase.inserted_metadata:
            return

        repo = git.Repo(".")
        sha = repo.head.object.hexsha

        SqliteBase.cursor.executemany(
            "INSERT INTO metadata VALUES (?, ?, ?)",
            [
                (Pipeline.instance.name, "start_time", datetime.utcnow()),
                (Pipeline.instance.name, "git_commit", sha),
                (Pipeline.instance.name, "config", json.dumps(get_config())),
            ],
        )

        SqliteBase.cursor.executemany(
            "INSERT INTO stages VALUES (?, ?, ?)",
            [
                (Pipeline.instance.name, s.__class__.__name__, i)
                for i, s in enumerate(ParentStage.static_stages)
            ],
        )

        SqliteBase.connection.commit()
        SqliteBase.inserted_metadata = True

    def on_init(self) -> None:
        self.before_database_create()

        if SqliteBase.connection is None:

            SqliteBase.connection = connect(self.file_name)
            SqliteBase.cursor = self.connection.cursor()

            self._create_metadata_tables()
            self._insert_start_metadata()

        self.on_database_create()

    def before_database_close(self) -> None:
        """
        Called just before the connection to the database is closed.
        """

    def on_destroy(self) -> None:
        if SqliteBase.connection is not None:
            SqliteBase.connection.commit()

            self.before_database_close()

            SqliteBase.cursor.execute(
                "INSERT INTO metadata VALUES (?, ?, ?)",
                (Pipeline.instance.name, "end_time", datetime.utcnow()),
            )

            SqliteBase.connection.commit()
            SqliteBase.connection.close()

            SqliteBase.cursor = None
            SqliteBase.connection = None
            SqliteBase.created_metadata = False
            SqliteBase.inserted_metadata = False
