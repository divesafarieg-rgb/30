import sqlite3


def check_if_vaccine_has_spoiled(
        cursor: sqlite3.Cursor,
        truck_number: str
) -> bool:
    cursor.execute("""
        SELECT EXISTS(
            SELECT 1 
            FROM table_truck_with_vaccine 
            WHERE truck_number = ? 
            AND temperature NOT BETWEEN -20 AND -16
            GROUP BY truck_number
            HAVING COUNT(*) >= 3
        )
    """, (truck_number,))

    result = cursor.fetchone()[0]
    return bool(result)