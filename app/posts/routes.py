from app.mapper import FromPostDataModelToPostResponseDto, FromPostDataModelsToGetPostsResponseDto, FromPostResponseDtoToElasticSearchModel, FromPostSkillDataModelsToSkillsResponseDto, FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto, PostType
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

    if len(postSkills) > 0:
        insertUserSkillQuery = generateInsertPostSkillQuery(postReponseDto["id"], postSkills)
        curr.execute(insertUserSkillQuery)
        conn.commit()
    curr.execute("""SELECT * FROM posts_has_skills as PHS JOIN skills as S ON PHS.skillId = S.id 
                 WHERE PHS.postId = {0}""".format(postReponseDto["id"]))

    postSkillJoinSkillDataModels = curr.fetchall()
    skillsDetailReponseDto = FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto(postSkillJoinSkillDataModels)
    postReponseDto["skills"] = skillsDetailReponseDto

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
    # updateUserSkillsDto = {
    #     "skills": request_data['skills'],
    # }
    skillIds = request_data['skills']

    curr.execute("""DELETE FROM posts_has_skills WHERE postId = {0}""".format(postId))
    
    insertPostSkillQuery = generateInsertPostSkillQuery(postId, skillIds)
    curr.execute(insertPostSkillQuery)
    conn.commit()
    
    curr.execute("""SELECT * FROM posts_has_skills WHERE postId = {0}""".format(postId))
    
    postSkillDataModels = curr.fetchall()
    skillsReponseDto = FromPostSkillDataModelsToSkillsResponseDto(postSkillDataModels)

    # need to implement the indexing after update skills   
    postReponseDto = FromPostDataModelToPostResponseDto(postDataModel)
    curr.execute("""SELECT * FROM posts_has_skills as PHS JOIN skills as S ON PHS.skillId = S.id 
                 WHERE PHS.postId = {0}""".format(postReponseDto["id"]))

    postSkillJoinSkillDataModels = curr.fetchall()
    skillsDetailReponseDto = FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto(postSkillJoinSkillDataModels)
    postReponseDto["skills"] = skillsDetailReponseDto

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
    print(updatePostQuery)
    curr.execute(updatePostQuery)
    conn.commit()

    # need to implement the indexing after update skills   
    curr.execute("""SELECT * FROM posts WHERE id = {0}""".format(postId))
    postDataModel = curr.fetchone()
    postReponseDto = FromPostDataModelToPostResponseDto(postDataModel)
    
    curr.execute("""SELECT * FROM posts_has_skills as PHS JOIN skills as S ON PHS.skillId = S.id 
                 WHERE PHS.postId = {0}""".format(postReponseDto["id"]))

    postSkillJoinSkillDataModels = curr.fetchall()
    skillsDetailReponseDto = FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto(postSkillJoinSkillDataModels)
    postReponseDto["skills"] = skillsDetailReponseDto

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

    
    curr.execute("""SELECT * FROM posts_has_skills AS PHS JOIN skills AS S ON PHS.skillId = S.Id WHERE PHS.postId = {0}""".format(postId))
    postHasSkillJoinsSkillDataModels = curr.fetchall()
    skillsReponseDto = FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto(postHasSkillJoinsSkillDataModels)

    postReponseDto['skills'] = skillsReponseDto
  
    return json.dumps({"message": "get post details success", "post":postReponseDto}), 200, {'ContentType':'application/json'}
