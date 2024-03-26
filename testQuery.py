from dataConnection import conn

curr = conn.cursor()

curr.execute("""DELETE FROM projects_has_users;""")

conn.commit()