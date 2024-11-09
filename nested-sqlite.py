import sqlite3
import json
from typing import Dict, Any, List, Optional


class NestedDictStorage:
    def __init__(self, db_path: str):
        """Initialize database connection and create table if it doesn't exist."""
        self.conn = sqlite3.connect(db_path)
        # Enable JSON functions
        self.conn.create_function(
            "json_valid", 1, lambda x: True if json.loads(x) else False
        )
        self.cursor = self.conn.cursor()

        # Create table with a JSON column and add indexes for common JSON paths
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS nested_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (json_valid(data))
            );
            
            -- Index for faster JSON path queries
            CREATE INDEX IF NOT EXISTS idx_data_json ON nested_data(key, json_extract(data, '$'));
        """)
        self.conn.commit()

    def store(self, key: str, nested_dict: Dict[str, Any]) -> None:
        """Store a nested dictionary using JSON serialization."""
        json_data = json.dumps(nested_dict)

        self.cursor.execute(
            """
            INSERT OR REPLACE INTO nested_data (key, data)
            VALUES (?, json(?))
        """,
            (key, json_data),
        )
        self.conn.commit()

    def retrieve(self, key: str) -> Dict[str, Any]:
        """Retrieve and deserialize a nested dictionary."""
        self.cursor.execute(
            """
            SELECT json_extract(data, '$') FROM nested_data WHERE key = ?
        """,
            (key,),
        )

        result = self.cursor.fetchone()
        if result is None:
            raise KeyError(f"No data found for key: {key}")

        return json.loads(result[0])

    def query_by_json_path(self, json_path: str, value: Any) -> List[Dict[str, Any]]:
        """
        Query records where the JSON path matches the specified value.
        Example: query_by_json_path('$.user.address.city', 'Springfield')
        """
        self.cursor.execute(
            """
            SELECT key, json_extract(data, '$') 
            FROM nested_data 
            WHERE json_extract(data, ?) = ?
        """,
            (json_path, value),
        )

        results = []
        for key, data in self.cursor.fetchall():
            results.append({"key": key, "data": json.loads(data)})
        return results

    def update_json_path(self, key: str, json_path: str, value: Any) -> None:
        """
        Update a specific value within the nested structure using JSON path.
        Example: update_json_path('user1', '$.user.preferences.theme', 'light')
        """
        self.cursor.execute(
            """
            UPDATE nested_data 
            SET data = json_set(data, ?, ?)
            WHERE key = ?
        """,
            (json_path, json.dumps(value), key),
        )
        self.conn.commit()

    def extract_json_path(self, key: str, json_path: str) -> Any:
        """
        Extract a specific value from the nested structure using JSON path.
        Example: extract_json_path('user1', '$.user.preferences.theme')
        """
        self.cursor.execute(
            """
            SELECT json_extract(data, ?) 
            FROM nested_data 
            WHERE key = ?
        """,
            (json_path, key),
        )

        result = self.cursor.fetchone()
        if result is None:
            raise KeyError(f"No data found for key: {key}")
        return json.loads(result[0]) if result[0] else None

    def search_json_text(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Full-text search within JSON values.
        Returns records where any string value contains the search term.
        """
        self.cursor.execute(
            """
            SELECT key, json_extract(data, '$') 
            FROM nested_data 
            WHERE data LIKE ?
        """,
            (f"%{search_term}%",),
        )

        results = []
        for key, data in self.cursor.fetchall():
            results.append({"key": key, "data": json.loads(data)})
        return results

    def get_array_length(self, key: str, json_path: str) -> int:
        """
        Get the length of a JSON array at a specific path.
        Example: get_array_length('user1', '$.user.hobbies')
        """
        self.cursor.execute(
            """
            SELECT json_array_length(json_extract(data, ?))
            FROM nested_data 
            WHERE key = ?
        """,
            (json_path, key),
        )

        result = self.cursor.fetchone()
        return result[0] if result and result[0] is not None else 0

    def close(self):
        """Close the database connection."""
        self.conn.close()


# Example usage
if __name__ == "__main__":
    # Create a nested dictionary
    sample_data = {
        "user": {
            "name": "John Doe",
            "address": {
                "street": "123 Main St",
                "city": "Springfield",
                "zipcode": "12345",
            },
            "preferences": {
                "theme": "dark",
                "notifications": {"email": True, "push": False},
            },
            "hobbies": ["reading", "hiking", "photography"],
        }
    }

    # Initialize storage
    storage = NestedDictStorage("nested_dict.db")

    # Store the nested dictionary
    storage.store("user1", sample_data)

    # Example queries using JSON features
    # Get all users from Springfield
    springfield_users = storage.query_by_json_path("$.user.address.city", "Springfield")

    # Update theme preference
    storage.update_json_path("user1", "$.user.preferences.theme", "light")

    # Get number of hobbies
    hobby_count = storage.get_array_length("user1", "$.user.hobbies")

    # Get specific preference
    theme = storage.extract_json_path("user1", "$.user.preferences.theme")

    # Search for users with "photography" hobby
    photo_enthusiasts = storage.search_json_text("photography")

    storage.close()
