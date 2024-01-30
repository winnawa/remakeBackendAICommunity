
from typing import List


def generateInsertUserQuery(createUserDto):
    prefixQuery = "INSERT INTO users ("
    postfixQuery = ") VALUES ("
    for key in createUserDto:
        prefixQuery = prefixQuery + key + ", "
        postfixQuery = postfixQuery + "'{}'".format(createUserDto[key]) + ", "
    
    query = prefixQuery[:-2] + postfixQuery[:-2] + ")"

    return query

def generateInsertUserSkillQuery(userId, skillIds):
    prefixQuery = "INSERT INTO users_has_skills (userId,skillId) VALUES "
    postfixQuery = ""
    for skillId in skillIds:
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

def generateInsertPostSkillQuery(postId, skillIds: List[any]):
    prefixQuery = "INSERT INTO posts_has_skills (postId,skillId) VALUES "
    postfixQuery = ""
    for skillId in skillIds:
        postfixQuery = postfixQuery + "({0},{1})".format(postId,skillId) + ", "
    
    query = prefixQuery + postfixQuery[:-2]

    return query

def generateFindPostsByIdsQueryString(postIds):
    prefixQuery = "SELECT * FROM posts WHERE id IN "
    postfixQuery = "( "
    for postId in postIds:
        postfixQuery = postfixQuery + "{0}, ".format(postId)
    query = prefixQuery + postfixQuery[:-2] + ")"

    return query