import psycopg2
conn_str = "postgres://smokhbuk:bjPRreLazLtTKelzdNGuYUMAMRbX08cC@tiny.db.elephantsql.com/smokhbuk"
user, password, host, path = conn_str.split("//")[1].split(":")[0], conn_str.split(":")[2].split("@")[0], conn_str.split("@")[1].split("/")[0], conn_str.split("/")[3]

# Create a connection
conn = psycopg2.connect(
    dbname=path,
    user=user,
    password=password,
    host=host
)

curr = conn.cursor()
curr.execute("""CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    cvLink VARCHAR(255)             
)""")

curr.execute("""CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    skillName VARCHAR(255) NOT NULL UNIQUE          
)""")

curr.execute("""CREATE TABLE IF NOT EXISTS users_has_skills (
    id SERIAL PRIMARY KEY,
    userId INT NOT NULL,
    skillId INT NOT NULL,                   
    CONSTRAINT fk_users
      FOREIGN KEY(userId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE,
    CONSTRAINT fk_skills
      FOREIGN KEY(skillId) 
	  REFERENCES skills(id)
	  ON DELETE CASCADE                           
)""")

# curr.execute("""INSERT INTO skills (skillName) VALUES 
#     ('Machine Learning'),
#     ('Deep Learning'),
#     ('PyTorch'),
#     ('Keras'),
#     ('Natural Language Processing'),
#     ('Python'),
#     ('Pandas'),
#     ('Numpy'),
#     ('Computer Vision'),
#     ('Data Analysis'),
#     ('Raspberry Pi'),
#     ('Data Mining'),
#     ('IoT'),
#     ('Arduino'),
#     ('TensorFlow'),
#     ('Scikit-learn'),
#     ('NLTK'),
#     ('Data Science'),
#     ('Apache Spark'),
#     ('Hadoop'),
#     ('Robotics'),
#     ('Dialogflow')
# """)

curr.execute("""CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    
    title VARCHAR(255) NOT NULL,
    creatorId INT NOT NULL,         
    privacy VARCHAR(255),
    status VARCHAR(255),
    projectLink VARCHAR(255),
    contactEmail VARCHAR(255),

    objectivesProjectInformation VARCHAR(500),
    methodologyProjectInformation VARCHAR(500),
    datasetProjectInformation VARCHAR(500),
    timelineProjectInformation VARCHAR(500),
             
    CONSTRAINT fk_creator
      FOREIGN KEY(creatorId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE   
)""")

curr.execute("""CREATE TABLE IF NOT EXISTS posts_has_skills (
    id SERIAL PRIMARY KEY,
    postId INT NOT NULL,
    skillId INT NOT NULL,                   
    CONSTRAINT fk_posts
      FOREIGN KEY(postId) 
	  REFERENCES posts(id)
	  ON DELETE CASCADE,
    CONSTRAINT fk_skills
      FOREIGN KEY(skillId) 
	  REFERENCES skills(id)
	  ON DELETE CASCADE  
)""")

curr.execute("""CREATE TABLE IF NOT EXISTS experiences (
    id SERIAL PRIMARY KEY,
    userId INT NOT NULL,
    experienceDescription VARCHAR(500) NOT NULL,
    timeline VARCHAR(500) NOT NULL,
    CONSTRAINT fk_users
      FOREIGN KEY(userId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE 
)""")

conn.commit()