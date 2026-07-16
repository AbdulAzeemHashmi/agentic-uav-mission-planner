import sqlite3
import os
from datetime import datetime
from typing import Any

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
DB_PATH = os.path.join(DB_DIR, "missions.db")

def init_db():
    """Initialize the SQLite database and create tables if they do not exist."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Missions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS missions (
            mission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_name TEXT NOT NULL,
            mission_type TEXT NOT NULL,
            altitude REAL NOT NULL,
            duration REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # 2. Waypoints Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waypoints (
            waypoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id INTEGER NOT NULL,
            sequence_no INTEGER NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            altitude REAL NOT NULL,
            action TEXT NOT NULL,
            FOREIGN KEY (mission_id) REFERENCES missions (mission_id) ON DELETE CASCADE
        )
    """)
    
    # 3. Safety Checks Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS safety_checks (
            check_id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id INTEGER NOT NULL,
            check_name TEXT NOT NULL,
            result TEXT NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY (mission_id) REFERENCES missions (mission_id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def save_mission(mission_data: dict[str, Any], waypoints: list[dict[str, Any]], safety_results: list[dict[str, Any]]) -> int:
    """
    Saves a complete mission (mission metadata, waypoints, and safety check results) to the database.
    Returns the newly created mission_id.
    """
    init_db()  # Ensure database is initialized
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Insert mission
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO missions (mission_name, mission_type, altitude, duration, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            mission_data.get("mission_name", "Unnamed Mission"),
            mission_data.get("mission_type", "surveillance"),
            float(mission_data.get("altitude", 50.0)),
            float(mission_data.get("duration", 15.0)),
            mission_data.get("status", "Needs Revision"),
            created_at
        ))
        
        mission_id = cursor.lastrowid
        
        # Insert waypoints
        for idx, wp in enumerate(waypoints):
            cursor.execute("""
                INSERT INTO waypoints (mission_id, sequence_no, latitude, longitude, altitude, action)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                mission_id,
                wp.get("sequence_no", idx),
                float(wp["latitude"]),
                float(wp["longitude"]),
                float(wp.get("altitude", mission_data.get("altitude", 50.0))),
                wp.get("action", "waypoint")
            ))
            
        # Insert safety checks
        for check in safety_results:
            cursor.execute("""
                INSERT INTO safety_checks (mission_id, check_name, result, message)
                VALUES (?, ?, ?, ?)
            """, (
                mission_id,
                check["check_name"],
                check["result"],
                check["message"]
            ))
            
        conn.commit()
        return mission_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_missions() -> list[dict[str, Any]]:
    """Retrieve all missions from the database."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM missions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    missions = []
    for r in rows:
        missions.append(dict(r))
        
    conn.close()
    return missions

def get_mission_by_id(mission_id: int) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Retrieve a specific mission, its waypoints, and its safety checks from the database.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Load mission metadata
    cursor.execute("SELECT * FROM missions WHERE mission_id = ?", (mission_id,))
    mission_row = cursor.fetchone()
    if not mission_row:
        conn.close()
        raise ValueError(f"Mission ID {mission_id} not found.")
        
    mission = dict(mission_row)
    
    # Load waypoints
    cursor.execute("SELECT * FROM waypoints WHERE mission_id = ? ORDER BY sequence_no ASC", (mission_id,))
    waypoint_rows = cursor.fetchall()
    waypoints = [dict(r) for r in waypoint_rows]
    
    # Load safety checks
    cursor.execute("SELECT * FROM safety_checks WHERE mission_id = ?", (mission_id,))
    check_rows = cursor.fetchall()
    safety_checks = [dict(r) for r in check_rows]
    
    conn.close()
    return mission, waypoints, safety_checks

def delete_mission(mission_id: int):
    """Delete a mission and all its related records from the database."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # SQLite foreign key cascade should be enabled if supported, or we do manual deletion:
        cursor.execute("DELETE FROM waypoints WHERE mission_id = ?", (mission_id,))
        cursor.execute("DELETE FROM safety_checks WHERE mission_id = ?", (mission_id,))
        cursor.execute("DELETE FROM missions WHERE mission_id = ?", (mission_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
