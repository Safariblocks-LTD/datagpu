"""Cache management and dataset versioning."""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json

from datagpu.utils import compute_hash, ensure_dir


class CacheManager:
    """Manages local cache of compiled datasets."""
    
    def __init__(self, cache_dir: Path = Path(".datagpu/cache")):
        self.cache_dir = ensure_dir(cache_dir)
        self.db_path = self.cache_dir / "cache.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for cache metadata."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT NOT NULL,
                version TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                compiled_path TEXT NOT NULL,
                manifest_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT,
                UNIQUE(dataset_name, version)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dataset_name 
            ON cache_entries(dataset_name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_hash 
            ON cache_entries(source_hash)
        """)
        
        conn.commit()
        conn.close()
    
    def compute_source_hash(self, source_path: Path) -> str:
        """Compute hash of source dataset file."""
        with open(source_path, "rb") as f:
            # Read in chunks for large files
            hasher = compute_hash(f.read())
        return hasher
    
    def get_cached_entry(self, dataset_name: str, version: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached entry by name and version."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT dataset_name, version, source_hash, compiled_path, 
                   manifest_path, created_at, metadata
            FROM cache_entries
            WHERE dataset_name = ? AND version = ?
        """, (dataset_name, version))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "dataset_name": row[0],
                "version": row[1],
                "source_hash": row[2],
                "compiled_path": row[3],
                "manifest_path": row[4],
                "created_at": row[5],
                "metadata": json.loads(row[6]) if row[6] else {}
            }
        return None
    
    def find_by_source_hash(self, source_hash: str) -> Optional[Dict[str, Any]]:
        """Find cached entry by source file hash."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT dataset_name, version, source_hash, compiled_path, 
                   manifest_path, created_at, metadata
            FROM cache_entries
            WHERE source_hash = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (source_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "dataset_name": row[0],
                "version": row[1],
                "source_hash": row[2],
                "compiled_path": row[3],
                "manifest_path": row[4],
                "created_at": row[5],
                "metadata": json.loads(row[6]) if row[6] else {}
            }
        return None
    
    def add_entry(
        self,
        dataset_name: str,
        version: str,
        source_hash: str,
        compiled_path: str,
        manifest_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add new cache entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        created_at = datetime.utcnow().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO cache_entries 
            (dataset_name, version, source_hash, compiled_path, manifest_path, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (dataset_name, version, source_hash, compiled_path, manifest_path, created_at, metadata_json))
        
        conn.commit()
        conn.close()
    
    def list_entries(self, dataset_name: Optional[str] = None) -> list:
        """List all cache entries, optionally filtered by dataset name."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if dataset_name:
            cursor.execute("""
                SELECT dataset_name, version, source_hash, created_at
                FROM cache_entries
                WHERE dataset_name = ?
                ORDER BY created_at DESC
            """, (dataset_name,))
        else:
            cursor.execute("""
                SELECT dataset_name, version, source_hash, created_at
                FROM cache_entries
                ORDER BY created_at DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "dataset_name": row[0],
                "version": row[1],
                "source_hash": row[2],
                "created_at": row[3]
            }
            for row in rows
        ]
    
    def clear_cache(self, dataset_name: Optional[str] = None) -> int:
        """Clear cache entries. Returns number of entries removed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if dataset_name:
            cursor.execute("DELETE FROM cache_entries WHERE dataset_name = ?", (dataset_name,))
        else:
            cursor.execute("DELETE FROM cache_entries")
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
