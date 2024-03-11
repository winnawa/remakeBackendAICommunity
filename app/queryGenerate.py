
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

def generateInsertUserExperienceQuery(userId, experiences):
    prefixQuery = "INSERT INTO experiences (userId,experienceDescription,timeline) VALUES "
    postfixQuery = ""
    for experience in experiences:
        description = experience["experienceDescription"]
        timeline = experience["timeline"]
        postfixQuery = postfixQuery + "({0},'{1}','{2}')".format(userId, description, timeline) + ", "
    
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

def generateFindUsersByIdsQueryString(userIds):
    prefixQuery = "SELECT * FROM users WHERE id IN "
    postfixQuery = "( "
    for userId in userIds:
        postfixQuery = postfixQuery + "{0}, ".format(userId)
    query = prefixQuery + postfixQuery[:-2] + ")"

    return query

# def generateFindSkillsByIdsQueryString(userIds):
#     prefixQuery = "SELECT * FROM users WHERE id IN "
#     postfixQuery = "( "
#     for userId in userIds:
#         postfixQuery = postfixQuery + "{0}, ".format(userId)
#     query = prefixQuery + postfixQuery[:-2] + ")"

#     return query

# def generateFindUsersByIdsQueryString(userIds):
#     prefixQuery = "SELECT * FROM users WHERE id IN "
#     postfixQuery = "( "
#     for userId in userIds:
#         postfixQuery = postfixQuery + "{0}, ".format(userId)
#     query = prefixQuery + postfixQuery[:-2] + ")"

#     return query

def generateInsertSearchHistoryQuery(userId, createSearchHistoryDto):
    prefixQuery = "INSERT INTO searchHistory (userId, "
    postfixQuery = ") VALUES ({0}, ".format(userId)
    for key in createSearchHistoryDto:
        prefixQuery = prefixQuery + key + ", "
        postfixQuery = postfixQuery + "'{}'".format(createSearchHistoryDto[key]) + ", "
    
    query = prefixQuery[:-2] + postfixQuery[:-2] + ")"

    return query    

def generateInsertFriendshipQuery(userId, createFriendshipDto):
    prefixQuery = "INSERT INTO user_is_friend_with_user (firstUserId, "
    postfixQuery = ") VALUES ({0}, ".format(userId)
    for key in createFriendshipDto:
        
        if key == "friendId":
            prefixQuery = prefixQuery + "secondUserId" + ", "
            postfixQuery = postfixQuery + "{}".format(createFriendshipDto[key]) + ", "
        else:
            prefixQuery = prefixQuery + key + ", "
            postfixQuery = postfixQuery + "'{}'".format(createFriendshipDto[key]) + ", "
    
    query = prefixQuery[:-2] + postfixQuery[:-2] + ")"

    return query

def generateUpdatePostQuery(postId, updatePostDetailsDto):
    prefixQuery = "UPDATE posts SET title = '{0}', creatorId = {1}".format(updatePostDetailsDto["title"],updatePostDetailsDto["creatorId"]) 
    if updatePostDetailsDto["privacy"] is not None:
        prefixQuery += ",privacy = '{}'".format(updatePostDetailsDto["privacy"])
    else:
        prefixQuery += ",privacy = NULL"
    if updatePostDetailsDto["status"] is not None:
        prefixQuery += ",status = '{}'".format(updatePostDetailsDto["status"])
    else:
        prefixQuery += ",status = NULL"
    if updatePostDetailsDto["projectLink"] is not None:
        prefixQuery += ", projectLink = '{}'".format(updatePostDetailsDto["projectLink"])
    else:
        prefixQuery += ",projectLink = NULL"
    if updatePostDetailsDto["contactEmail"] is not None:
        prefixQuery += ", contactEmail = '{}'".format(updatePostDetailsDto["contactEmail"])
    else:
        prefixQuery += ", contactEmail = NULL"
    
    prefixQuery += """,objectivesProjectInformation = '{0}', methodologyProjectInformation = '{1}',datasetProjectInformation = '{2}',timelineProjectInformation = '{3}' WHERE Id = {4}""".format(updatePostDetailsDto["objectivesProjectInformation"],updatePostDetailsDto["methodologyProjectInformation"],updatePostDetailsDto["datasetProjectInformation"],updatePostDetailsDto["timelineProjectInformation"], postId) 
    return prefixQuery