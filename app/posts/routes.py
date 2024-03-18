from datetime import datetime
from app.mapper import FromCommentDataModelToCommentReponseDto, FromCommentDataModelsToCommentsResponseDto, FromPostDataModelToPostResponseDto, FromPostDataModelsToGetPostsResponseDto, FromPostHasStarDataModelsToStarsResponseDto, FromPostResponseDtoToElasticSearchModel, FromPostSkillDataModelsToSkillsResponseDto, FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto, PostType
from app.posts import bp
from flask import request
import json
from dataConnection import curr, conn
from app.queryGenerate import generateInsertPostQuery, generateInsertPostSkillQuery, generateUpdatePostQuery
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

    curr.execute("""SELECT * FROM posts WHERE title = '{0}' and creatorId = {1}""".format(createPostDto["title"],createPostDto["creatorId"]))
    postDataModel = curr.fetchone()
    postReponseDto = FromPostDataModelToPostResponseDto(postDataModel)

    # insert skills
    if len(postSkills) > 0:
        insertUserSkillQuery = generateInsertPostSkillQuery(postReponseDto["id"], postSkills)
        curr.execute(insertUserSkillQuery)
        conn.commit()
    
    # add-on skills
    curr.execute("""SELECT * FROM posts_has_skills as PHS JOIN skills as S ON PHS.skillId = S.id 
                 WHERE PHS.postId = {0}""".format(postReponseDto["id"])) 
    postSkillJoinSkillDataModels = curr.fetchall()
    skillsDetailReponseDto = FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto(postSkillJoinSkillDataModels)
    postReponseDto["skills"] = skillsDetailReponseDto

    # index to elasticsearch
    postElasticSearchModel = FromPostResponseDtoToElasticSearchModel(postReponseDto)
    AutoMatching.indexNewData([postElasticSearchModel])

    filterParam = {
        "_id": "{0}_{1}".format(PostType.project.name, postReponseDto["id"])
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
        "objectivesProjectInformation": request_data['objectivesProjectInformation'],
        "methodologyProjectInformation": request_data['methodologyProjectInformation'],
        "datasetProjectInformation": request_data['datasetProjectInformation'],
        "timelineProjectInformation": request_data['timelineProjectInformation']
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

    page = int(request.args.get('page')) if request.args.get('page') is not None else 0
    size = int(request.args.get('size')) if request.args.get('size') is not None else 10

    queryString = """SELECT * FROM posts LIMIT 100""" 
    if creatorId is not None:
        queryString = """SELECT * FROM posts WHERE creatorId = {}""".format(creatorId) 

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
    curr.execute("""SELECT * FROM posts_has_skills AS PHS JOIN skills AS S ON PHS.skillId = S.Id WHERE PHS.postId = {0}""".format(postId))
    postHasSkillJoinsSkillDataModels = curr.fetchall()
    skillsReponseDto = FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto(postHasSkillJoinsSkillDataModels)

    postReponseDto['skills'] = skillsReponseDto
  
    # add-on stars
    curr.execute("""SELECT * FROM post_has_starts WHERE postId = {0}""".format(postId))
    postHasStarDataModels = curr.fetchall()
    starsReponseDto = FromPostHasStarDataModelsToStarsResponseDto(postHasStarDataModels)

    postReponseDto['stars'] = starsReponseDto
  
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

    curr.execute("""SELECT * FROM comments WHERE postId = {0} and userId = {1} and createdTime = '{2}'""".format(postId, createCommentDto["userId"], createCommentDto["createdTime"]))
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