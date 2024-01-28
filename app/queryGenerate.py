
def generateInsertUserQuery(createUserDto):
    prefixQuery = "INSERT INTO users ("
    postfixQuery = ") VALUES ("
    for key in createUserDto:
        prefixQuery = prefixQuery + key + ", "
        postfixQuery = postfixQuery + "'{}'".format(createUserDto[key]) + ", "
    
    query = prefixQuery[:-2] + postfixQuery[:-2] + ")"

    return query

def generateInsertUserSkillQuery(userId, updateUserSkillsDto):
    prefixQuery = "INSERT INTO users_has_skills (userId,skillId) VALUES "
    postfixQuery = ""
    for skillId in updateUserSkillsDto["skills"]:
        postfixQuery = postfixQuery + "({0},{1})".format(userId,skillId) + ", "
    
    query = prefixQuery + postfixQuery[:-2]

    return query

def generateInsertPostQuery(createPostDto):
    prefixQuery = "INSERT INTO posts ("
    postfixQuery = ") VALUES ("
    for key in createPostDto:
        prefixQuery = prefixQuery + key + ", "
        if key == "creatorId":
            postfixQuery = postfixQuery + "{0}".format(createPostDto[key]) + ", "
        else:
            postfixQuery = postfixQuery + "'{0}'".format(createPostDto[key]) + ", "
    
    query = prefixQuery[:-2] + postfixQuery[:-2] + ")"

    return query