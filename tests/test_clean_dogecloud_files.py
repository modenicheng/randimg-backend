"""Regression tests for the DogeCloud cleanup candidate query."""

import importlib
import sys
import tempfile
import unittest
from pathlib import Path

from sqlalchemy import Boolean, Column, Integer, JSON, MetaData, String, Table


class DogeCloudCleanupTest(unittest.TestCase):
    def setUp(self):
        self.config_path = Path(__file__).resolve().parents[1] / "db" / "configs.py"
        self.tmp_dir = tempfile.TemporaryDirectory()
        db_url = f"sqlite:///{Path(self.tmp_dir.name) / 'cleanup.db'}"
        self.config_path.write_text(f'DATABASE_URL = "{db_url}"\n')

        for module_name in [
            "clean_dogecloud_files",
            "db.database",
            "db.configs",
        ]:
            sys.modules.pop(module_name, None)

        self.cleanup = importlib.import_module("clean_dogecloud_files")

    def tearDown(self):
        self.config_path.unlink(missing_ok=True)
        self.tmp_dir.cleanup()
        for module_name in [
            "clean_dogecloud_files",
            "db.database",
            "db.configs",
        ]:
            sys.modules.pop(module_name, None)

    def test_get_cleanup_candidates_uses_core_batches(self):
        metadata = MetaData()
        images = Table(
            "images",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("image_path", String),
            Column("colors", JSON),
            Column("accessable", Boolean),
            Column("uploaded", Boolean),
        )
        metadata.create_all(self.cleanup.database.engine)

        with self.cleanup.database.engine.begin() as conn:
            conn.execute(
                images.insert(),
                [
                    {
                        "id": 1,
                        "image_path": "ok.jpg",
                        "colors": {"primary_color": [1, 2, 3]},
                        "accessable": True,
                        "uploaded": True,
                    },
                    {
                        "id": 2,
                        "image_path": "blocked.jpg",
                        "colors": {"primary_color": [1, 2, 3]},
                        "accessable": False,
                        "uploaded": True,
                    },
                    {
                        "id": 3,
                        "image_path": "no-colors.jpg",
                        "colors": None,
                        "accessable": True,
                        "uploaded": True,
                    },
                ],
            )

        candidates = list(self.cleanup.get_cleanup_candidates(batch_size=1))

        self.assertEqual(
            [(item.id, item.image_path, item.reason) for item in candidates],
            [
                (2, "blocked.jpg", "accessable=false"),
                (3, "no-colors.jpg", "missing-colors"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
