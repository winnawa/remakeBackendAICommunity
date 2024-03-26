from datetime import datetime
from app.mapper import FromCommentDataModelToCommentReponseDto, FromCommentDataModelsToCommentsResponseDto, FromEventPostHasUserJoinsUserDataModelsToEventParticipantsResponseDto, FromParticipationDataModelToParticipationResponseDto, FromPostDataModelToPostResponseDto, FromPostDataModelsToGetPostsResponseDto, FromPostHasStarDataModelsToStarsResponseDto, FromPostResponseDtoToElasticSearchModel, FromPostSkillDataModelsToSkillsResponseDto, FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto, FromProjectPostHasUserJoinsUserDataModelsToProjectParticipantsResponseDto, FromUserDataModelToUserResponseDto, PostType
from app.posts import bp
from flask import request
import json
from dataConnection import curr, conn
from app.queryGenerate import generateInsertInsertProjectParticipationQuery, generateInsertPostQuery, generateInsertPostSkillQuery, generateUpdatePostQuery
from app.elasticSearchConnection import AutoMatching

@bp.route('/', methods=['POST'])
def createPost():
    request_data = request.get_json()
    createPostDto = {}
    postSkills = []
    for key in request_data:
        # combine posts_has_skills creation into the same query
        if key == "skills":
            postSkills = request_data["skills"]
        else:
        # normal attribute of a post
            createPostDto[key] = request_data[key]

    curr.execute("""SELECT * FROM posts WHERE title = '{0}' and creatorId = {1}""".format(createPostDto["title"],createPostDto["creatorId"]))
    postDataModel = curr.fetchone()
    if postDataModel is not None:
        return json.dumps({"message": "duplicated title"}), 400, {'ContentType':'application/json'}

    insertPostQuery = generateInsertPostQuery(createPostDto)
    curr.execute(insertPostQuery)
    conn.commit()

    curr.execute("""SELECT * FROM posts WHERE title = '{0}' and creatorId = {1} and postType ='{2}'""".format(createPostDto["title"],createPostDto["creatorId"], createPostDto["postType"]))
    postDataModel = curr.fetchone()
    postReponseDto = FromPostDataModelToPostResponseDto(postDataModel)

    # insert skills
    if len(postSkills) > 0:
        insertUserSkillQuery = generateInsertPostSkillQuery(postReponseDto["id"], postSkills)
        curr.execute(insertUserSkillQuery)
        conn.commit()
    
    # add-on skills
    if createPostDto["postType"] == str(PostType.project.value):
        curr.execute("""SELECT * FROM posts_has_skills as PHS JOIN skills as S ON PHS.skillId = S.id 
                    WHERE PHS.postId = {0}""".format(postReponseDto["id"])) 
        postSkillJoinSkillDataModels = curr.fetchall()
        skillsDetailReponseDto = FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto(postSkillJoinSkillDataModels)
        postReponseDto["skills"] = skillsDetailReponseDto

    # index to elasticsearch
    postElasticSearchModel = FromPostResponseDtoToElasticSearchModel(postReponseDto)
    AutoMatching.indexNewData([postElasticSearchModel])

    postTypeName = PostType(str(createPostDto["postType"])).name
    filterParam = {
        "_id": "{0}_{1}".format(postTypeName, postReponseDto["id"])
    }
    AutoMatching.updateEmbeddingNewData(filterParam, True)

    return json.dumps({"message": "create post success", "post":postReponseDto}), 200, {'ContentType':'application/json'}


@bp.route('/<postId>/skills', methods=['PUT'])
def updatePostSkills(postId):
    
    curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    if postDataModel is None:
        return json.dumps({"message": "post not found"}), 404, {'ContentType':'application/json'}

    request_data = request.get_json()
    skillIds = request_data['skills']

    curr.execute("""DELETE FROM posts_has_skills WHERE postId = {0}""".format(postId))
    
    insertPostSkillQuery = generateInsertPostSkillQuery(postId, skillIds)
    curr.execute(insertPostSkillQuery)
    conn.commit()
    
    curr.execute("""SELECT * FROM posts_has_skills WHERE postId = {0}""".format(postId))
    
    postSkillDataModels = curr.fetchall()
    skillsReponseDto = FromPostSkillDataModelsToSkillsResponseDto(postSkillDataModels)

    # re-indexing after update skills   
    # add-on skills
    postReponseDto = FromPostDataModelToPostResponseDto(postDataModel)
    curr.execute("""SELECT * FROM posts_has_skills as PHS JOIN skills as S ON PHS.skillId = S.id 
                 WHERE PHS.postId = {0}""".format(postReponseDto["id"]))

    postSkillJoinSkillDataModels = curr.fetchall()
    skillsDetailReponseDto = FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto(postSkillJoinSkillDataModels)
    postReponseDto["skills"] = skillsDetailReponseDto

    # index to elasticsearch
    postElasticSearchModel = FromPostResponseDtoToElasticSearchModel(postReponseDto)

    postDocument = AutoMatching.getDocumentById(postId,PostType.project)
    postDocument.meta["content"] = postElasticSearchModel["content"]
    AutoMatching.indexNewData([postDocument])
    filterParam = {
        "_id": "{0}_{1}".format(PostType.project.name, postReponseDto["id"])
    }
    AutoMatching.updateEmbeddingNewData(filterParam, True)
    return json.dumps({"message": "update skills success", "skills":skillsReponseDto}), 200, {'ContentType':'application/json'}


@bp.route('/<postId>', methods=['PUT'])
def updatePostDetails(postId):
    
    curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    if postDataModel is None:
        return json.dumps({"message": "post not found"}), 404, {'ContentType':'application/json'}
    postReponseDto = FromPostDataModelToPostResponseDto(postDataModel)
    request_data = request.get_json()

    if 'title' in request_data:  
        curr.execute("""SELECT * FROM posts WHERE title = '{0}' and id != {1} and creatorId = {2}""".format(request_data["title"],postId,postReponseDto["creatorId"]))
        existedPostDataModel = curr.fetchone()
        if existedPostDataModel is not None:
            return json.dumps({"message": "duplicated found"}), 400, {'ContentType':'application/json'}

    updatePostDetailsDto = {
        "title": request_data['title'],
        "creatorId": request_data['creatorId'],
        "privacy": request_data['privacy'] if 'privacy' in request_data else None,
        "status": request_data['status'] if 'status' in request_data else None,
        "projectLink" : request_data['projectLink'] if 'projectLink' in request_data else None,
        "contactEmail": request_data['contactEmail'] if 'contactEmail' in request_data else None,
        "objectivesProjectInformation": request_data['objectivesProjectInformation'] if 'objectivesProjectInformation' in request_data else None,
        "methodologyProjectInformation": request_data['methodologyProjectInformation'] if 'methodologyProjectInformation' in request_data else None,
        "datasetProjectInformation": request_data['datasetProjectInformation'] if 'datasetProjectInformation' in request_data else None,
        "timelineProjectInformation": request_data['timelineProjectInformation'] if 'timelineProjectInformation' in request_data else None,
        "content": request_data['content'] if 'content' in  request_data else None,
        "isEventDisabled": request_data['isEventDisabled'] if 'isEventDisabled' in  request_data else None
    }

    updatePostQuery = generateUpdatePostQuery(postId, updatePostDetailsDto)
    # print(updatePostQuery)
    curr.execute(updatePostQuery)
    conn.commit()

    # re-indexing after update skills  
    # get post 
    curr.execute("""SELECT * FROM posts WHERE id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    postReponseDto = FromPostDataModelToPostResponseDto(postDataModel)
    
    # add-on skills 
    curr.execute("""SELECT * FROM posts_has_skills as PHS JOIN skills as S ON PHS.skillId = S.id 
                 WHERE PHS.postId = {0}""".format(postReponseDto["id"]))

    postSkillJoinSkillDataModels = curr.fetchall()
    skillsDetailReponseDto = FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto(postSkillJoinSkillDataModels)
    postReponseDto["skills"] = skillsDetailReponseDto

    # index to elasticsearch
    postElasticSearchModel = FromPostResponseDtoToElasticSearchModel(postReponseDto)

    postDocument = AutoMatching.getDocumentById(postId,PostType.project)
    if postDocument is None:
        postDocument = AutoMatching.getDocumentById(postId,PostType.article)
    if postDocument is None:
        postDocument = AutoMatching.getDocumentById(postId,PostType.event)
    
    postDocument.meta["content"] = postElasticSearchModel["content"]
    AutoMatching.indexNewData([postDocument])
    filterParam = {
        "_id": "{0}_{1}".format(PostType.project.name, postReponseDto["id"])
    }
    AutoMatching.updateEmbeddingNewData(filterParam, True)
    return json.dumps({"message": "update post success", "post":postReponseDto}), 200, {'ContentType':'application/json'}


@bp.route('/', methods=['GET'])
def getPosts():
    creatorId = int(request.args.get('creatorId')) if request.args.get('creatorId') is not None else None
    postType = str(request.args.get('postType')) if request.args.get('postType') is not None else None

    page = int(request.args.get('page')) if request.args.get('page') is not None else 0
    size = int(request.args.get('size')) if request.args.get('size') is not None else 10

    queryString = """SELECT * FROM posts """

    if postType or creatorId is not None:
        queryString += "WHERE "
        isFirstParam = True
        for key in request.args.keys():
            if key == "postType" :
                if not isFirstParam:
                    queryString += " and "
                queryString += """postType = '{}' """.format(postType)    
            if key == "creatorId":
                if not isFirstParam:
                    queryString += " and "
                queryString += """creatorId = {} """.format(creatorId)  
            if isFirstParam:
                isFirstParam = False
    queryString += """ORDER BY Id DESC""" 

    print(queryString)

    curr.execute(queryString)
    postsDataModels = curr.fetchall()

    startPoint = page*size
    endPoint = (page+1)*size if (page+1)*size < len(postsDataModels) else len(postsDataModels)
    returnedPostsResponseDto = []
    if startPoint < len(postsDataModels):
        paginatedPostDataModels = [postsDataModels[i] for i in range(startPoint,endPoint)]
        returnedPostsResponseDto = FromPostDataModelsToGetPostsResponseDto(paginatedPostDataModels)

    return json.dumps({"message": "get posts success", "posts":returnedPostsResponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/<postId>', methods=['GET'])
def getPostDetails(postId):

    curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    if postDataModel is None:
        return json.dumps({"message": "post not found"}), 404, {'ContentType':'application/json'}
    
    postReponseDto = FromPostDataModelToPostResponseDto(postDataModel)

    # add-on skills
    if postReponseDto["postType"] == PostType.project.value:
        curr.execute("""SELECT * FROM posts_has_skills AS PHS JOIN skills AS S ON PHS.skillId = S.Id WHERE PHS.postId = {0}""".format(postId))
        postHasSkillJoinsSkillDataModels = curr.fetchall()
        skillsReponseDto = FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto(postHasSkillJoinsSkillDataModels)

        postReponseDto['skills'] = skillsReponseDto
  
    # add-on stars
    curr.execute("""SELECT * FROM post_has_starts WHERE postId = {0}""".format(postId))
    postHasStarDataModels = curr.fetchall()
    starsReponseDto = FromPostHasStarDataModelsToStarsResponseDto(postHasStarDataModels)

    postReponseDto['stars'] = starsReponseDto
  
    # add-on participants
    if postReponseDto["postType"] == PostType.event.value:
        curr.execute("""SELECT * FROM events_has_users AS EHU JOIN users AS U ON EHU.userId = U.Id WHERE EHU.postId = {0}""".format(postId))
        eventPostHasUserJoinsUserDataModels = curr.fetchall()
        participantsReponseDto = FromEventPostHasUserJoinsUserDataModelsToEventParticipantsResponseDto(eventPostHasUserJoinsUserDataModels)
        postReponseDto['participants'] = participantsReponseDto
  
    if postReponseDto["postType"] == PostType.project.value:
        curr.execute("""SELECT * FROM projects_has_users AS PHU JOIN users AS U ON PHU.userId = U.Id WHERE PHU.postId = {0}""".format(postId))
        projectPostHasUserJoinsUserDataModels = curr.fetchall()
        participantsReponseDto = FromProjectPostHasUserJoinsUserDataModelsToProjectParticipantsResponseDto(projectPostHasUserJoinsUserDataModels)
        postReponseDto['participants'] = participantsReponseDto
  

    return json.dumps({"message": "get post details success", "post":postReponseDto}), 200, {'ContentType':'application/json'}


@bp.route('/<postId>/stars', methods=['POST'])
def createStarForPost(postId):
    request_data = request.get_json()
    userId = request_data['userId']

    curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    if postDataModel is None:
        return json.dumps({"message": "post not found"}), 404, {'ContentType':'application/json'}
    
    # add-on stars
    curr.execute("""SELECT * FROM post_has_starts WHERE postId = {0} and userId = {1}""".format(postId,userId))
    postHasStarDataModel = curr.fetchone()
    if postHasStarDataModel is not None:
        return json.dumps({"message": "user already add star to post "}), 400, {'ContentType':'application/json'}
    
    curr.execute("""INSERT INTO post_has_starts (postId,userId) VALUES ({0},{1}) """.format(postId,userId))
    conn.commit()

    curr.execute("""SELECT * FROM post_has_starts WHERE postId = {0}""".format(postId))
    postHasStarDataModels = curr.fetchall()
    print(postHasStarDataModels)
    starsReponseDto = FromPostHasStarDataModelsToStarsResponseDto(postHasStarDataModels)

    return json.dumps({"message": "add stars to post success", "stars":starsReponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/<postId>/stars', methods=['DELETE'])
def deleteStarForPost(postId):
    request_data = request.get_json()
    userId = request_data['userId']

    curr.execute("""DELETE FROM post_has_starts WHERE postId = {0} and userId = {1}""".format(postId,userId))
    conn.commit()

    curr.execute("""SELECT * FROM post_has_starts WHERE postId = {0}""".format(postId))
    postHasStarDataModels = curr.fetchall()
    starsReponseDto = FromPostHasStarDataModelsToStarsResponseDto(postHasStarDataModels)


    return json.dumps({"message": "delete star success", "stars":starsReponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/<postId>/comments', methods=['POST'])
def createCommentForPost(postId):
    request_data = request.get_json()
    createCommentDto = {
        "userId" : request_data['userId'],
        "content": request_data['content']
    }
        
    # add createdTime
    now = datetime.now()
    date_time = now.strftime("%Y/%m/%d, %H:%M:%S")
    createCommentDto["createdTime"] = date_time

    # add username
    curr.execute("""SELECT * FROM users WHERE Id = {0}""".format(createCommentDto["userId"]))
    userDataModel = curr.fetchone()
    if userDataModel is None:
        return json.dumps({"message": "userId not found"}), 404, {'ContentType':'application/json'}
    username = userDataModel[1]    
    createCommentDto["username"] = username

    # check post existance
    curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    if postDataModel is None:
        return json.dumps({"message": "post not found"}), 404, {'ContentType':'application/json'}
    
    # add-on comment
    curr.execute("""INSERT INTO comments (postId,userId,content,createdTime,username) VALUES ({0},{1},'{2}','{3}','{4}') """.format(postId,createCommentDto["userId"],createCommentDto["content"],createCommentDto["createdTime"],createCommentDto["username"]))
    conn.commit()

    curr.execute("""SELECT * FROM comments WHERE postId = {0} and userId = {1} and createdTime = '{2}' ORDER BY createdTime DESC """.format(postId, createCommentDto["userId"], createCommentDto["createdTime"]))
    commentDataModel = curr.fetchone()
    commentReponseDto = FromCommentDataModelToCommentReponseDto(commentDataModel)

    return json.dumps({"message": "add comment to post success", "newComment":commentReponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/<postId>/comments', methods=['GET'])
def getCommentsForPost(postId):

    # check post existance
    curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    if postDataModel is None:
        return json.dumps({"message": "post not found"}), 404, {'ContentType':'application/json'}
    
    # get comments
    curr.execute("""SELECT * FROM comments WHERE postId = {0}""".format(postId))
    commentDataModels = curr.fetchall()
    commentReponseDto = FromCommentDataModelsToCommentsResponseDto(commentDataModels)

    return json.dumps({"message": "get comments success", "comments":commentReponseDto}), 200, {'ContentType':'application/json'}


@bp.route('/<postId>/comments/<commentId>', methods=['DELETE'])
def deleteCommentsForPost(postId,commentId):

    # check post existance
    curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    if postDataModel is None:
        return json.dumps({"message": "post not found"}), 404, {'ContentType':'application/json'}

    # delete comments
    curr.execute("""DELETE FROM comments WHERE postId = {0} and id = {1}""".format(postId,commentId))
    conn.commit()

    return json.dumps({"message": "delete comment success"}), 200, {'ContentType':'application/json'}

    
@bp.route('/<postId>', methods=['DELETE'])
def deletePost(postId):

    # check post existance
    curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
    postDataModel = curr.fetchone()
   
    # delete post
    curr.execute("""DELETE FROM posts WHERE id = {}""".format(postId))
    conn.commit()

    postResponseDto = FromPostDataModelToPostResponseDto(postDataModel)
    AutoMatching.deleteDocument(postResponseDto)

    return json.dumps({"message": "delete post success"}), 200, {'ContentType':'application/json'}


@bp.route('/<postId>/event-participations', methods=['POST'])
def createParticipantForEvent(postId):

    request_data = request.get_json()
    createParticipantForEventDto = {
        "userId" : request_data['userId']
    }

    # check post existance
    curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    if postDataModel is None:
        return json.dumps({"message": "post not found"}), 404, {'ContentType':'application/json'}

    # check post type
    postResponseDto = FromPostDataModelToPostResponseDto(postDataModel)
    if postResponseDto["postType"] != PostType.event.value:
        return json.dumps({"message": "post is not event"}), 400, {'ContentType':'application/json'}

    curr.execute("SELECT * FROM events_has_users WHERE postId={} and userId ={}".format(postId,createParticipantForEventDto["userId"]))
    participation = curr.fetchone()
    if participation is not None:
        return json.dumps({"message": "participation is existed"}), 400, {'ContentType':'application/json'}

    curr.execute("INSERT INTO events_has_users (postId,userId) VALUES ({0},{1})".format(postId,createParticipantForEventDto["userId"]))
    conn.commit()

    curr.execute("SELECT * FROM users WHERE id ={}".format(createParticipantForEventDto["userId"]))
    userDataModel = curr.fetchone()
    userReponseDto = FromUserDataModelToUserResponseDto(userDataModel)

    return json.dumps({"message": "add participation success", "user":userReponseDto}), 200, {'ContentType':'application/json'}


@bp.route('/<postId>/event-participations', methods=['DELETE'])
def deleteParticipationForEvent(postId):

    request_data = request.get_json()
    deleteParticipantForPostDto = {
        "userId" : request_data['userId']
    }
    # check post existance
    curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    if postDataModel is None:
        return json.dumps({"message": "post not found"}), 404, {'ContentType':'application/json'}
   
    # delete post
    curr.execute("""DELETE FROM events_has_users WHERE postId = {0} and userId = {1}""".format(postId,deleteParticipantForPostDto["userId"]))
    conn.commit()

    return json.dumps({"message": "delete participation success"}), 200, {'ContentType':'application/json'}


@bp.route('/<postId>/project-participations', methods=['POST'])
def createParticipantForProject(postId):

    request_data = request.get_json()
    createParticipantForProjectDto = {
        "userId" : request_data['userId'],
        "contributionDescription" : request_data['contributionDescription'] if "contributionDescription" in request_data else None,
        "position": request_data['position']  if "position" in request_data else None
    }

    # check post existance
    curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    if postDataModel is None:
        return json.dumps({"message": "post not found"}), 404, {'ContentType':'application/json'}

    # check post type
    postResponseDto = FromPostDataModelToPostResponseDto(postDataModel)
    if postResponseDto["postType"] != PostType.project.value:
        return json.dumps({"message": "post is not project"}), 400, {'ContentType':'application/json'}

    curr.execute("SELECT * FROM users WHERE id ={}".format(createParticipantForProjectDto["userId"]))
    userDataModel = curr.fetchone()
    if userDataModel is None:
        return json.dumps({"message": "user is not found"}), 404, {'ContentType':'application/json'}


    curr.execute("SELECT * FROM projects_has_users WHERE postId={} and userId ={}".format(postId,createParticipantForProjectDto["userId"]))
    participation = curr.fetchone()
    if participation is not None:
        return json.dumps({"message": "participation is existed"}), 400, {'ContentType':'application/json'}

    insertProjectParticipationQuery = generateInsertInsertProjectParticipationQuery(createParticipantForProjectDto,postId)    
    curr.execute(insertProjectParticipationQuery)
    conn.commit()

    curr.execute("SELECT * FROM users WHERE id ={}".format(createParticipantForProjectDto["userId"]))
    userDataModel = curr.fetchone()
    print("line 472",createParticipantForProjectDto["userId"])
    print("line 473",userDataModel)
    userReponseDto = FromUserDataModelToUserResponseDto(userDataModel)

    curr.execute("SELECT * FROM projects_has_users WHERE postId={0} and userId ={1}".format(postId,createParticipantForProjectDto["userId"]))
    participationDataModel = curr.fetchone()
    participationResponseDto = FromParticipationDataModelToParticipationResponseDto(participationDataModel)
    participationResponseDto["username"] = userReponseDto["username"]
    participationResponseDto["email"] = userReponseDto["email"]
    

    # add user id to participants in ES
    postDocument = AutoMatching.getDocumentById(postId,PostType.project)
    if postDocument is None:
        return json.dumps({"message": "document for project not found"}), 404, {'ContentType':'application/json'}
    
    existingParticipants = postDocument.meta["participants"] if "participants" in postDocument.meta else []
    if existingParticipants is None:
        existingParticipants = []
    existingParticipants.append(str(userReponseDto["id"]))
    postDocument.meta["participants"] = existingParticipants
    
    AutoMatching.indexNewData([postDocument])
    filterParam = {
        "_id": "{0}_{1}".format(PostType.project.name, postId)
    }
    # do not recalculate embedding
    AutoMatching.updateEmbeddingNewData(filterParam, False)

    return json.dumps({"message": "add participation success", "participation":participationResponseDto}), 200, {'ContentType':'application/json'}


@bp.route('/<postId>/project-participations', methods=['DELETE'])
def deleteParticipationForProject(postId):

    request_data = request.get_json()
    deleteParticipantForProjectDto = {
        "userId" : request_data['userId']
    }
    # check post existance
    curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    if postDataModel is None:
        return json.dumps({"message": "post not found"}), 404, {'ContentType':'application/json'}
   
    # delete post
    curr.execute("""DELETE FROM projects_has_users WHERE postId = {0} and userId = {1}""".format(postId,deleteParticipantForProjectDto["userId"]))
    conn.commit()

     # add user id to participants in ES
    postDocument = AutoMatching.getDocumentById(postId,PostType.project)
    if postDocument is None:
        return json.dumps({"message": "document for project not found"}), 404, {'ContentType':'application/json'}
    
    existingParticipants = postDocument.meta["participants"] if "participants" in postDocument.meta else [] 
    removeUserId = lambda x: x != str(deleteParticipantForProjectDto["userId"])
    postDocument.meta["participants"] = list(filter(removeUserId,existingParticipants))
    AutoMatching.indexNewData([postDocument])
    filterParam = {
        "_id": "{0}_{1}".format(PostType.project.name, postId)
    }
    AutoMatching.updateEmbeddingNewData(filterParam, False)

    return json.dumps({"message": "delete participation success"}), 200, {'ContentType':'application/json'}

