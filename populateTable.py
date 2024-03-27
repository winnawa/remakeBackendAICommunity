# import psycopg2
# conn_str = "postgres://smokhbuk:bjPRreLazLtTKelzdNGuYUMAMRbX08cC@tiny.db.elephantsql.com/smokhbuk"
# user, password, host, path = conn_str.split("//")[1].split(":")[0], conn_str.split(":")[2].split("@")[0], conn_str.split("@")[1].split("/")[0], conn_str.split("/")[3]

# # Create a connection
# conn = psycopg2.connect(
#     dbname=path,
#     user=user,
#     password=password,
#     host=host
# )

from dataConnection import conn

curr = conn.cursor()

curr.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    cvLink VARCHAR(255)             
)""")

# curr.execute("""INSERT INTO users (username, password, email) VALUES 
#     ('namkhoa','asd123','namkhoa@gmail.com'),
#     ('namkhoaphamnguyen','asd123','namkhoaphamnguyen@gmail.com'),
#     ('kienvo','asd123','kienvo@gmail.com'),
#     ('namkhoapham','asd123','namkhoapham@gmail.com'),
#     ('anhkhoapham','asd123','anhkhoapham@gmail.com'),
#     ('vtkienn','asd123','vtkienn@gmail.com')        
# """)

curr.execute("""CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY,
    skillName VARCHAR(255) NOT NULL UNIQUE          
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


curr.execute("""CREATE TABLE IF NOT EXISTS users_has_skills (
    id INTEGER PRIMARY KEY,
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


# curr.execute("""INSERT INTO users_has_skills (userId,skillId) VALUES 
#     (1,1),
#     (1,2),
#     (1,4),
#     (1,5),
#     (1,6),
#     (2,2),                
#     (2,4),
#     (2,7),
#     (2,8)           
# """)

curr.execute("""CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    
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
             
    postType VARCHAR(255) NOT NULL,
    content VARCHAR(500),

    eventStartDate VARCHAR(255),         
    isEventDisabled INT,
    imgUrl VARCHAR(500),

    CONSTRAINT fk_creator
      FOREIGN KEY(creatorId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE   
)""")



# curr.execute("""INSERT INTO posts (title,creatorId,privacy,status,projectLink,contactEmail, objectivesProjectInformation, methodologyProjectInformation, datasetProjectInformation, timelineProjectInformation, postType) VALUES 
#     ("AI-Based Disease Prediction System", 1, 'public', 'in-progress', 'www.aiBased.com', email@gmail.com,"The aim of this project is to develop a system that uses artificial intelligence to predict the likelihood of diseases based on patient symptoms.", "The project will involve training a deep learning model using patient data. The model will use patient symptoms as input and output the likelihood of various diseases. Techniques such as data preprocessing, model training, and model evaluation will be used.", "The project will use anonymized patient data from public health databases. All data used will comply with relevant data protection and privacy laws.", "The project is expected to take six months, with the first two months dedicated to data collection and preprocessing, the next three months for model development and training, and the final month for testing and evaluation.",'0'),
#     ('Sentiment Analysis of Social Media Comments', 1,'public', 'in-progress', 'www.semantic.com', email@gmail.com,'The goal of this project is to develop an AI system that can accurately determine the sentiment (positive, negative, neutral) of comments on social media platforms.', 'The project will involve training a machine learning model on a dataset of social media comments labeled with their sentiment. Techniques such as text preprocessing, feature extraction, model training, and model evaluation will be used.', 'The project will use publicly available datasets of social media comments. All data used will comply with relevant data protection and privacy laws.', 'The project is expected to take four months, with the first month dedicated to data collection and preprocessing, the next two months for model development and training, and the final month for testing and evaluation.','0'),
#     ('Smart Home Automation - Develop an AI-based system that can automate home appliances such as lights, fans, and air conditioners',1,'public', 'in-progress', NULL, email@gmail.com,'The goal of this project is to reduce energy consumption and improve convenience.','Supervised Learning.','Sensor data from home appliances.','3 months.','0'),
#     ('Sentiment Analysis - Build an AI model that can analyze the sentiment of social media posts', 1,'public', 'in-progress', NULL, email@gmail.com,'The goal of this project is to understand the public opinion on a particular topic.','Unsupervised Learning.','Social media posts.','2 months.','0'),
#     ('Fraud Detection - Create an AI system that can detect fraudulent transactions in real-time', 1,'public', 'in-progress', NULL, email@gmail.com,'The goal of this project is to prevent financial losses.','Semi-Supervised Learning.','Transaction data.','6 months.','0'),
#     ('Autonomous Vehicles - Develop an AI-based system that can control autonomous vehicles', 1,'public', 'in-progress', NULL, email@gmail.com,'The goal of this project is to improve road safety and reduce traffic congestion.','Reinforcement Learning.','Sensor data from vehicles.','12 months.','0'),
#     ('Chatbot - create an AI-powered chatbot that can assist customers with their queries', 1,'public', 'in-progress', NULL, email@gmail.com,'The goal of this project is to is to improve customer service.','Supervised Learning.','Customer queries.','It might take years to complete the project.','0'),
#     ('Autonomous Vehicles - Develop an AI-based system that can control autonomous vehicles', 1,'private', 'in-progress', NULL, NULL,'The goal of this project is to improve road safety and reduce traffic congestion.','Reinforcement Learning.','Sensor data from vehicles.','12 months.','0'),
#     ('Image Recognition - Build an AI model that can recognize objects in images', 1,'private', 'in-progress', NULL, NULL,'	The goal of this project is to automate image classification.','Convolutional Neural Networks.','Image data.','Two months.','0'),
#     ('Recommendation System - Develop an AI-based recommendation system that can suggest products to customers', 1,'private', 'in-progress', NULL, email@gmail.com,'	The goal of this project is to improve sales.','Collaborative Filtering.','Customer purchase history.','Three months.','0'),
#     ('Predictive Maintenance - Create an AI system that can predict equipment failures before they occur', 1,'private', 'in-progress', NULL, NULL,'The goal of this project is to reduce downtime.','Time Series Analysis.','Equipment sensor data.','6 months.','0'),
#     ('Speech Recognition - Build an AI model that can transcribe speech to text', 1,'private', 'in-progress', NULL, email@gmail.com,'The goal of this project is to automate speech recognition.','Recurrent Neural Networks.','Audio data.','Two months.','0'),
#     ('Medical Diagnosis - Develop an AI-based system that can diagnose medical conditions', 2,'private', 'in-progress', NULL, email@gmail.com,'	The objective of this project is to improve health care.','Deep Learning.','Medical records.','12 months.','0'),
#     ('AI-Driven IoT Device Management System For Effiency', 1,'public', 'in-progress', NULL, email@gmail.com,'The goal of this project is to create a system that uses artificial intelligence to manage and optimize the performance of IoT devices.','The project will involve training a machine learning model using data from IoT devices. The model will use device data as input and output optimized device settings. Techniques such as data preprocessing, model training, and model evaluation will be used.','The project will use anonymized device data from public IoT databases. All data used will comply with relevant data protection and privacy laws.','The project is expected to take six months, with the first two months dedicated to data collection and preprocessing, the next three months for model development and training, and the final month for testing and evaluation.','0'),
#     ('Chatbot for Answering Frequently Asked Questions (FAQ)', 1, 'public', 'done', 'www.faq.com', 'email@gmail.com','The goal of this project is to create an intelligent chatbot capable of answering common queries and frequently asked questions. By leveraging natural language processing (NLP) techniques, the chatbot will provide accurate and helpful responses to users.','Data Collection: Gather a set of frequently asked questions related to a specific domain (e.g., customer service, technical support, product information). Data Preprocessing: Clean and preprocess the FAQ data by removing noise, tokenizing sentences, and creating a question-answer dataset.','a set of frequently asked questions.','From 2021 to 2022.','0'),
#     ('AI in agriculture', 1, 'public', 'in progress', 'www.project-link.com', 'email@gmail.com','Apply AI in agriculture for optimized crop yield, resource efficiency, and precision farming. Analyze soil, weather, and pest data to improve productivity. Optimize irrigation and fertilization for resource conservation. Empower farmers with AI-driven insights for informed decisions.','Collect diverse datasets and employ supervised/unsupervised learning. Develop models for real-time monitoring and decision-making. Rigorous testing ensures reliability in real-world settings.','Comprise soil, weather, satellite, and historical crop data. Soil samples inform about pH, nutrients, and organic matter. Weather data includes temperature, precipitation, and humidity. Satellite imagery monitors vegetation health and field conditions. Historical crop records provide insights into yield, pest incidents, and agronomic practices.','2024-2025.','0')        
# """)


curr.execute("""CREATE TABLE IF NOT EXISTS posts_has_skills (
    id INTEGER PRIMARY KEY,
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

# curr.execute("""INSERT INTO posts_has_skills (postId,skillId) VALUES 
#     (1,1),
#     (1,2),
#     (1,6),
#     (1,10),
#     (2,1),
#     (2,12),
#     (2,5),
#     (2,6),
#     (3,1),
#     (3,6),
#     (3,11),
#     (3,13),
#     (3,15),
#     (3,14),    
#     (4,5),
#     (4,6),
#     (4,16),
#     (4,17),    
#     (5,1),
#     (5,6),
#     (5,18),
#     (5,20),
#     (5,15),
#     (5,19),
#     (6,1),
#     (6,6),    
#     (6,21),    
#     (6,15),
#     (7,1),   
#     (7,5),   
#     (7,2),   
#     (7,15),   
#     (7,22),
#     (9,6),
#     (9,1),                
#     (9,9),
#     (10,1),
#     (10,6),
#     (10,18),   
#     (11,1),                
#     (11,6),
#     (11,18),
#     (11,19),
#     (11,20),
#     (11,15),
#     (12,1),
#     (12,6),
#     (12,5),
#     (13,1),
#     (13,6),
#     (13,18),
#     (13,4),
#     (13,15),
#     (14,1),
#     (14,6),
#     (14,18),
#     (14,4),
#     (14,15),
#     (15,5),
#     (15,4),
#     (14,6),
#     (14,2),
#     (14,15),
#     (15,6),
#     (15,4),
#     (15,2),
#     (15,15),
#     (15,5),
#     (16,6),
#     (16,7),
#     (16,8),
#     (16,10) 
# """)

curr.execute("""CREATE TABLE IF NOT EXISTS experiences (
    id INTEGER PRIMARY KEY,
    userId INT NOT NULL,
    experienceDescription VARCHAR(500) NOT NULL,
    timeline VARCHAR(500) NULL,
    CONSTRAINT fk_users
      FOREIGN KEY(userId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE 
)""")

# curr.execute("""INSERT INTO experiences (userId,experienceDescription,timeline) VALUES 
#     (2,"User, as a Deep Learning Specialist at VinAI, developed a neural network model that improved the accuracy of the company's image recognition software by 30%. They also wrote a technical paper on their work that was published in a top-tier AI conference.","From 2023 To 2024."),
#     (3,"User, in their role as a Machine Learning Engineer at VinAI, designed an anomaly detection system that reduced fraudulent transactions by 25%. They also optimized the company's machine learning infrastructure, reducing model training time by 40%","From 2023 To 2024."),
#     (5,"In their role as an AI Analyst at VinAI, User conducted thorough market research and data analysis that informed the companyss AI strategy, publishing a model that can detect the malfunctioning body part of the human, thus treating the health problem before it becomes serious  . Their insights led to the successful launch of three new AI products.","2020 To 2023."),
#     (4,"At VinAI, User held the position of AI Architect and designed the architecture for a distributed AI system that allowed for faster processing of large datasets. This resulted in a 50% reduction in data processing times.","From 2022 To 2023."),
#     (4,"User works as an AI Consultant at VinAI, helped clients implement AI solutions that increased operational efficiency by 35%. They also provided training to clients’ staff on how to use and maintain these AI systems.","From 2023 To 2024."),
#     (1,"User works as a Software Engineer at VinAI in spearheadeding the development of a machine learning model that improved our product recommendation system, resulting in a 20% increase in user engagement. User also collaborated with the data engineering team to streamline our data pipeline, enhancing the efficiency of our model training process.","From 2021 To April 2024."),
#     (1,"As a Senior AI Engineer at VinAI, User led a team that built a robust AI platform that supported multiple machine learning and deep learning models. This platform enabled the company to rapidly prototype and deploy new AI features.","From April 2023 To January 2024."),
#     (1,"User works as a Product Manager at VinAI in leading the successful launch of an AI-powered customer service chatbot, which improved customer response times by 30% and increased customer satisfaction scores.","From January, 1st 2024 To present.")
# """)

# can add exp for other user
#     (1,"As an AI Solutions Developer at TechGenius AI Solutions, I drove the development of AI-powered applications, specializing in natural language processing and computer vision. Collaborating closely with cross-functional teams, I engineered innovative solutions that revolutionized client workflows, from automated document processing to image recognition systems.","Now."),
#     (1,"As an AI Research Assistant at NeuralNet Labs, I conducted in-depth analysis and experimentation to advance AI algorithms. Collaborating with researchers, I contributed to developing novel models for image recognition and natural language understanding. Employing cutting-edge techniques, I played a crucial role in pushing the boundaries of AI capabilities.","2018-2019."),
#     (1,"	As an AI Data Analyst at InsightAI Solutions, I utilized data mining and statistical analysis techniques to derive actionable insights from large datasets. Leveraging machine learning algorithms, I developed predictive models to optimize business processes and enhance decision-making. Collaborating with cross-functional teams, I contributed to the development of AI-driven solutions tailored to meet client needs, driving innovation and efficiency.","2016-2017.")               

curr.execute("""CREATE TABLE IF NOT EXISTS searchHistory (
    id INTEGER PRIMARY KEY,
    userId INT NOT NULL,
    searchString VARCHAR(500) NOT NULL,
    CONSTRAINT fk_users
      FOREIGN KEY(userId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE 
)""")

# curr.execute("""INSERT INTO searchHistory (userId,searchString) VALUES 
#     (1,"Machine Learning Engineer with experience in improving the effiency of the system"),
#     (1,"research paper")             
# """)

curr.execute("""CREATE TABLE IF NOT EXISTS user_is_friend_with_user (
    id INTEGER PRIMARY KEY,
    firstUserId INT NOT NULL,
    secondUserId INT NOT NULL,
    friendshipDescription VARCHAR(500),                   
    CONSTRAINT fk_first_user
      FOREIGN KEY(firstUserId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE,
    CONSTRAINT fk_second_user
      FOREIGN KEY(secondUserId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE  
)""")

# curr.execute("""INSERT INTO user_is_friend_with_user (firstUserId,secondUserId,friendshipDescription) VALUES 
#     (5,1,"working in the same outsource project relating to Machine Learning in IoT"),
#     (1,5,""),             
#     (5,2,"working in the same outsource project relating to Machine Learning in IoT"),
#     (2,5,""),             
#     (5,3,"working in the same outsource project relating to Machine Learning in IoT"),
#     (3,5,""),             
#     (5,4,"working in the same outsource project relating to Machine Learning in IoT"),
#     (4,5,"")                         
# """)

curr.execute("""CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY,
    createdTime VARCHAR(255),         
    notificationDescription VARCHAR(500), 
    type INT NOT NULL,
    postId INT,
    CONSTRAINT fk_post
      FOREIGN KEY(postId) 
	  REFERENCES posts(id)
	  ON DELETE CASCADE
)""")


curr.execute("""CREATE TABLE IF NOT EXISTS user_is_notified_by_notification (
    id INTEGER PRIMARY KEY,
    userId INT NOT NULL,
    notificationId INT NOT NULL,
    CONSTRAINT fk_user
      FOREIGN KEY(userId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE,
    CONSTRAINT fk_notification
      FOREIGN KEY(notificationId) 
	  REFERENCES notifications(id)
	  ON DELETE CASCADE  
)""")


curr.execute("""CREATE TABLE IF NOT EXISTS post_has_starts (
    id INTEGER PRIMARY KEY,
    postId INT NOT NULL,
    userId INT NOT NULL,
    CONSTRAINT fk_user
      FOREIGN KEY(userId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE,
    CONSTRAINT fk_post
      FOREIGN KEY(postId) 
	  REFERENCES posts(id)
	  ON DELETE CASCADE  
)""")

curr.execute("""CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY,
    postId INT NOT NULL,
    userId INT NOT NULL,
    content VARCHAR(500) NOT NULL,
    createdTime VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL, 
    CONSTRAINT fk_user
      FOREIGN KEY(userId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE,
    CONSTRAINT fk_post
      FOREIGN KEY(postId) 
	  REFERENCES posts(id)
	  ON DELETE CASCADE  
)""")

curr.execute("""CREATE TABLE IF NOT EXISTS events_has_users (
    id INTEGER PRIMARY KEY,
    postId INT NOT NULL,
    userId INT NOT NULL,
    CONSTRAINT fk_user
      FOREIGN KEY(userId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE,
    CONSTRAINT fk_post
      FOREIGN KEY(postId) 
	  REFERENCES posts(id)
	  ON DELETE CASCADE  
)""")

curr.execute("""CREATE TABLE IF NOT EXISTS projects_has_users (
    id INTEGER PRIMARY KEY,
    postId INT NOT NULL,
    userId INT NOT NULL,
    contributionDescription VARCHAR(500),
    position VARCHAR(255) ,                          
    CONSTRAINT fk_user
      FOREIGN KEY(userId) 
	  REFERENCES users(id)
	  ON DELETE CASCADE,
    CONSTRAINT fk_post
      FOREIGN KEY(postId) 
	  REFERENCES posts(id)
	  ON DELETE CASCADE  
)""")

conn.commit()