
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
        if createPostDto[key] is None:
            continue
        
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
    if updatePostDetailsDto["content"] is not None:
        prefixQuery += ", content = '{}'".format(updatePostDetailsDto["content"])
    else:
        prefixQuery += ", content = NULL"
    if updatePostDetailsDto["isEventDisabled"] is not None:
        prefixQuery += ", isEventDisabled = '{}'".format(updatePostDetailsDto["isEventDisabled"])
    else:
        prefixQuery += ", isEventDisabled = NULL"

    if updatePostDetailsDto["objectivesProjectInformation"] is not None:
        prefixQuery += ", objectivesProjectInformation = '{}'".format(updatePostDetailsDto["objectivesProjectInformation"])
    else:
        prefixQuery += ", objectivesProjectInformation = NULL"   

    if updatePostDetailsDto["methodologyProjectInformation"] is not None:
        prefixQuery += ", methodologyProjectInformation = '{}'".format(updatePostDetailsDto["methodologyProjectInformation"])
    else:
        prefixQuery += ", methodologyProjectInformation = NULL"      

    if updatePostDetailsDto["datasetProjectInformation"] is not None:
        prefixQuery += ", datasetProjectInformation = '{}'".format(updatePostDetailsDto["datasetProjectInformation"])
    else:
        prefixQuery += ", datasetProjectInformation = NULL" 

    if updatePostDetailsDto["timelineProjectInformation"] is not None:
        prefixQuery += ", timelineProjectInformation = '{}'".format(updatePostDetailsDto["timelineProjectInformation"])
    else:
        prefixQuery += ", timelineProjectInformation = NULL"
    
    
    # prefixQuery += """,objectivesProjectInformation = '{0}', methodologyProjectInformation = '{1}',datasetProjectInformation = '{2}',timelineProjectInformation = '{3}' WHERE Id = {4}""".format(updatePostDetailsDto["objectivesProjectInformation"],updatePostDetailsDto["methodologyProjectInformation"],updatePostDetailsDto["datasetProjectInformation"],updatePostDetailsDto["timelineProjectInformation"], postId) 
    prefixQuery += """ WHERE Id = {}""".format(postId) 
    return prefixQuery

def generateInsertNotificationQuery(createNotificationDto):
    prefixQuery = "INSERT INTO notifications ("
    postfixQuery = ") VALUES ("
    for key in createNotificationDto:
        if key == "postId":
            prefixQuery = prefixQuery + key + ", "
            postfixQuery = postfixQuery + "{}".format(createNotificationDto[key]) + ", "
        else:    
            prefixQuery = prefixQuery + key + ", "
            postfixQuery = postfixQuery + "'{}'".format(createNotificationDto[key]) + ", "
    
    query = prefixQuery[:-2] + postfixQuery[:-2] + ")"

    return query

def generateInsertUserIsNotifiedByNotificationQuery(notificationReponseDto,userIds):
    prefixQuery = "INSERT INTO user_is_notified_by_notification (userId, notificationId) VALUES "
    for userId in userIds:
        postfixQuery = "({0},{1}),".format(notificationReponseDto["id"],userId)
        prefixQuery += postfixQuery
    query = prefixQuery[0:-1]
    return query

def generateInsertInsertProjectParticipationQuery(createParticipantForProjectDto,postId):
    prefixQuery = "INSERT INTO projects_has_users (postId,userId "
    postfixQuery = "VALUES ({0},{1}".format(postId,createParticipantForProjectDto["userId"]) 

    for key in createParticipantForProjectDto:
        if key == "contributionDescription" and createParticipantForProjectDto["contributionDescription"] is not None:
            prefixQuery += ",contributionDescription "
            postfixQuery += ",'{}' ".format(createParticipantForProjectDto["contributionDescription"])
        if key == "position" and createParticipantForProjectDto["position"] is not None:
            prefixQuery += ",position "
            postfixQuery += ",'{}' ".format(createParticipantForProjectDto["position"])
    query = prefixQuery + ")" + postfixQuery + ")"
    return query