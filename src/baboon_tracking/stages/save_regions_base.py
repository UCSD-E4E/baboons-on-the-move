"""
Base class for saving regions to Sqlite database.
"""

from abc import ABC
from sqlite3 import Connection, Cursor, connect
from datetime import datetime
import json
import git

from pipeline import Stage
from pipeline.stage_result import StageResult
from pipeline.parent_stage import ParentStage
from config import get_config


class SaveRegionsBase(Stage, ABC):
    """
    Base class for saving regions to Sqlite database.
    """

    def __init__(self, run_key: str) -> None:
        Stage.__init__(self)

        self.run_key = run_key

        self.file_name = "./output/results.db"

        self.connection: Connection = None
        self.cursor: Cursor = None

    def __exit__(self, exc_type, exc_value, traceback):
        self.on_destroy()

    def on_init(self) -> None:
        if self.connection is None:
            self.before_database_create()

            self.connection = connect(self.file_name)
            self.cursor = self.connection.cursor()

            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS metadata
                (run_key text, key text, value text)"""
            )

            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS stages
                (run_key text, name text, sort_order int)"""
            )

            self.cursor.execute(
                """DELETE FROM metadata
                WHERE run_key = ?""",
                (self.run_key,),
            )

            self.cursor.execute(
                """DELETE FROM stages
                WHERE run_key = ?""",
                (self.run_key,),
            )

            self.connection.commit()

            repo = git.Repo(".")
            sha = repo.head.object.hexsha

            self.cursor.executemany(
                "INSERT INTO metadata VALUES (?, ?, ?)",
                [
                    (self.run_key, "start_time", datetime.utcnow()),
                    (self.run_key, "git_commit", sha),
                    (self.run_key, "config", json.dumps(get_config())),
                ],
            )

            self.cursor.executemany(
                "INSERT INTO stages VALUES (?, ?, ?)",
                [
                    (self.run_key, s.__class__.__name__, i)
                    for i, s in enumerate(ParentStage.static_stages)
                ],
            )

            self.connection.commit()

            self.on_database_create()

    def before_database_create(self) -> None:
        """
        Called before the database file is created.
        """

    def on_database_create(self) -> None:
        """
        Called when the database file is created.
        """

    def execute(self) -> StageResult:
        return StageResult(True, True)

    def before_database_close(self) -> None:
        """
        Called just before the connection to the database is closed.
        """

    def on_destroy(self) -> None:
        if self.connection is not None:
            self.connection.commit()

            self.before_database_close()

            self.cursor.execute(
                "INSERT INTO metadata VALUES (?, ?, ?)",
                (self.run_key, "end_time", datetime.utcnow()),
            )

            self.connection.commit()
            self.connection.close()

            self.cursor = None
            self.connection = None
