from abc import ABC
from datetime import datetime
import json
import hashlib
from sqlite3 import Connection, Cursor, OperationalError, connect
from typing import Dict

import git
import backoff
from library.config import get_config
from bom_pipeline.parent_stage import ParentStage
from bom_pipeline.pipeline import Pipeline
from bom_pipeline.stage import Stage


class SqliteBase(Stage, ABC):
    created_metadata = False
    inserted_metadata = False

    connection: Connection = None
    cursor: Cursor = None

    def __init__(self):
        Stage.__init__(self)

        self.file_name = "./output/results.db"
        self.md5 = hashlib.md5()
        self._pipeline_name: str = None

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
        self._pipeline_name = Pipeline.instance.name

        if SqliteBase.created_metadata:
            return

        SqliteBase.cursor.execute(
            """CREATE TABLE IF NOT EXISTS metadata
                (pipeline text, key text, value text)"""
        )

        SqliteBase.cursor.execute(
            """CREATE TABLE IF NOT EXISTS stages
                (pipeline text, name text, sort_order int)"""
        )

        SqliteBase.cursor.execute(
            """DELETE FROM metadata
                WHERE pipeline = ?""",
            (self._pipeline_name,),
        )

        SqliteBase.cursor.execute(
            """DELETE FROM stages
                WHERE pipeline = ?""",
            (self._pipeline_name,),
        )

        SqliteBase.connection.commit()
        SqliteBase.created_metadata = True

    @backoff.on_exception(backoff.expo, OperationalError)
    def _insert_start_metadata(self):
        if SqliteBase.inserted_metadata:
            return

        repo = git.Repo(".")
        sha = repo.head.object.hexsha

        self.insert_metadata(
            {
                "start_time": datetime.utcnow(),
                "git_commit": sha,
                "config": json.dumps(get_config()),
            }
        )

        SqliteBase.cursor.executemany(
            "INSERT INTO stages VALUES (?, ?, ?)",
            [
                (self._pipeline_name, s.__class__.__name__, i)
                for i, s in enumerate(ParentStage.static_stages)
            ],
        )

        SqliteBase.connection.commit()
        SqliteBase.inserted_metadata = True

    @backoff.on_exception(backoff.expo, OperationalError)
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

    @backoff.on_exception(backoff.expo, OperationalError)
    def on_destroy(self) -> None:
        if SqliteBase.connection is not None:
            SqliteBase.connection.commit()

            self.before_database_close()

            self.insert_metadata({"end_time": datetime.utcnow()})

            SqliteBase.connection.commit()
            SqliteBase.connection.close()

            SqliteBase.cursor = None
            SqliteBase.connection = None
            SqliteBase.created_metadata = False
            SqliteBase.inserted_metadata = False

    @backoff.on_exception(backoff.expo, OperationalError)
    def save_hash(self, hash_key: str):
        self.insert_metadata({hash_key: self.md5.hexdigest()})

    @backoff.on_exception(backoff.expo, OperationalError)
    def insert_metadata(self, metadata: Dict[str, str]):
        SqliteBase.cursor.executemany(
            "INSERT INTO metadata VALUES (?, ?, ?)",
            [(self._pipeline_name, k, v) for k, v in metadata.items()],
        )
