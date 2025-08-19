#!/usr/bin/env python3
"""Database migration script to add performance indexes."""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import linkcovery modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from linkcovery.core.config import get_config


def migrate_database() -> None:
    """Add performance indexes to existing database."""
    config = get_config()
    db_path = config.get_database_path()

    if not Path(db_path).exists():
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if indexes already exist
        existing_indexes = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='links'",
        ).fetchall()

        existing_index_names = {idx[0] for idx in existing_indexes}

        # Add indexes if they don't exist
        indexes_to_create = [
            ("idx_links_domain", "CREATE INDEX IF NOT EXISTS idx_links_domain ON links (domain)"),
            ("idx_links_tag", "CREATE INDEX IF NOT EXISTS idx_links_tag ON links (tag)"),
            ("idx_links_is_read", "CREATE INDEX IF NOT EXISTS idx_links_is_read ON links (is_read)"),
            ("idx_links_created_at", "CREATE INDEX IF NOT EXISTS idx_links_created_at ON links (created_at)"),
            (
                "idx_links_domain_is_read",
                "CREATE INDEX IF NOT EXISTS idx_links_domain_is_read ON links (domain, is_read)",
            ),
            ("idx_links_tag_is_read", "CREATE INDEX IF NOT EXISTS idx_links_tag_is_read ON links (tag, is_read)"),
        ]

        for idx_name, sql in indexes_to_create:
            if idx_name not in existing_index_names:
                cursor.execute(sql)
            else:
                pass

        # Optimize database
        cursor.execute("VACUUM")

        cursor.execute("ANALYZE")

        conn.commit()

        # Show final index list
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='links'",
        ).fetchall()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()
