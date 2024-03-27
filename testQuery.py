from dataConnection import conn

curr = conn.cursor()

curr.execute("""DELETE FROM experiences WHERE userId = 5 """)

curr.execute("""INSERT INTO experiences (userId,experienceDescription,timeline) VALUES 
    (5,"In their role as an AI Analyst at VinAI, User conducted thorough market research and data analysis that informed the companyss AI strategy, publishing a model that can detect the malfunctioning body part of the human, thus treating the health problem before it becomes serious  . Their insights led to the successful launch of three new AI products.","2020 To 2023.")
""")

conn.commit()