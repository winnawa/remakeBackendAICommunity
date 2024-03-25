from dataConnection import conn

curr = conn.cursor()

curr.execute("""delete from users where Id = 6""")

conn.commit()