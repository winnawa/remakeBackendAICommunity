from dataConnection import conn

curr = conn.cursor()

curr.execute("""UPDATE posts SET contactEmail = "email@gmail.com" WHERE Id < 10 """)

conn.commit()