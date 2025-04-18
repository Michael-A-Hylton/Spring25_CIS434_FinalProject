import sqlite3
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Insert a test user
test_username = "testuser"
test_password = "testpassword"  # Note: This would be hashed in a real app

cursor.execute("INSERT INTO User (username, password) VALUES (?, ?);", (test_username, test_password))
conn.commit()

# Verify the insert by fetching the user
cursor.execute("SELECT * FROM User WHERE username = ?;", (test_username,))
inserted_user = cursor.fetchone()

conn.close()

inserted_user