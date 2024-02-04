from app.elasticSearchConnection import AutoMatching
from app.queryGenerate import generateFindPostsByIdsQueryString, generateFindUsersByIdsQueryString, generateInsertUserExperienceQuery, generateInsertUserQuery, generateInsertUserSkillQuery
from app.repoAbstraction import getDetailsUserResponseDto
from app.users import bp
from flask import request
import json
from app.dataConnection import curr, conn
from app.mapper import FromExperienceDataModelsToExperiencesResponseDto, FromPostDataModelToPostResponseDto, FromPostDataModelsToGetPostsResponseDto, FromUserContextDataToSystemContextQuery, FromUserDataModelToUserResponseDto, FromUserResponseDtoToElasticSearchModel, FromUserSkillDataModelsToSkillsResponseDto, FromUserSkillJoinSkillDataModelsToSkillsDetailResponseDto, PostType

@bp.route('/', methods=['POST'])
def createUser():
    request_data = request.get_json()
    createUserDto = {}
    for key in request_data:
        createUserDto[key] = request_data[key]

    curr.execute("""SELECT * FROM users WHERE username = '{0}' """.format(createUserDto["username"]))
    userDataModel = curr.fetchone()
    if userDataModel is not None:
        return json.dumps({"message": "username existed"}), 400, {'ContentType':'application/json'}

    insertUserQuery = generateInsertUserQuery(createUserDto)
    curr.execute(insertUserQuery)
    conn.commit()

    curr.execute("""SELECT * FROM users WHERE username = '{0}' """.format(createUserDto["username"]))
    userDataModel = curr.fetchone()
    userReponseDto = FromUserDataModelToUserResponseDto(userDataModel)

    return json.dumps({"message": "create user success", "user":userReponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/', methods=['PUT'])
def login():
    request_data = request.get_json()
    loginDto = {}
    for key in request_data:
        loginDto[key] = request_data[key]

    curr.execute("""SELECT * FROM users WHERE username = '{0}' """.format(loginDto["username"]))
    userDataModel = curr.fetchone()
    if userDataModel is None:
        return json.dumps({"message": "user not found"}), 404, {'ContentType':'application/json'}

    password = userDataModel[2]
    if password != loginDto["password"]:
        return json.dumps({"message": "wrong credential"}), 400, {'ContentType':'application/json'}

    userReponseDto = FromUserDataModelToUserResponseDto(userDataModel)

    # add skills and experiences
    userReponseDto = getDetailsUserResponseDto(userReponseDto, None, None, None)

    return json.dumps({"message": "login success", "user":userReponseDto}), 200, {'ContentType':'application/json'}


@bp.route('/<userId>', methods=['PUT'])
def updateUserById(userId):
    
    curr.execute("""SELECT * FROM users WHERE Id = {0}""".format(userId))
    userDataModel = curr.fetchone()
    if userDataModel is None:
        return json.dumps({"message": "user not found"}), 404, {'ContentType':'application/json'}

    request_data = request.get_json()
    updateUserDto = {
        "username": request_data['username'],
        "password": request_data['password'],
        "email": request_data['email'],
        "cvLink" : request_data['cvLink']
    }

    curr.execute("""UPDATE users SET username = %s, password = %s, email = %s, cvLink = %s WHERE Id = %s""",(
        updateUserDto["username"], updateUserDto["password"], updateUserDto["email"], updateUserDto["cvLink"], userId))
    conn.commit()
    
    curr.execute("""SELECT * FROM users WHERE Id = %s""",(userId))
    userDataModel = curr.fetchone()
    userReponseDto = FromUserDataModelToUserResponseDto(userDataModel)

    return json.dumps({"message": "update user success", "user":userReponseDto}), 200, {'ContentType':'application/json'}


@bp.route('/<userId>/skills', methods=['PUT'])
def updateUserSkills(userId):
    
    curr.execute("""SELECT * FROM users WHERE Id = {0}""".format(userId))
    userDataModel = curr.fetchone()
    if userDataModel is None:
        return json.dumps({"message": "user not found"}), 404, {'ContentType':'application/json'}

    request_data = request.get_json()
    skillIds = request_data['skills']

    curr.execute("""DELETE FROM users_has_skills WHERE userId = {0}""".format(userId))
    
    insertUserSkillQuery = generateInsertUserSkillQuery(userId, skillIds)
    curr.execute(insertUserSkillQuery)
    conn.commit()
    
    # get user skills
    curr.execute("""SELECT * FROM users_has_skills AS UHS JOIN skills AS S ON UHS.skillId = S.id
                  WHERE UHS.userId = {0}""".format(userId))
    
    userSkillJoinSkillDataModels = curr.fetchall()
    userSkillsDetailReponseDto = FromUserSkillJoinSkillDataModelsToSkillsDetailResponseDto(userSkillJoinSkillDataModels)
    
    # get data to index to ElasticSearch
    userReponseDto = getDetailsUserResponseDto(None, userId, userSkillsDetailReponseDto, None)
    userElasticSearchModel = FromUserResponseDtoToElasticSearchModel(userReponseDto)
    AutoMatching.indexNewData([userElasticSearchModel])
    AutoMatching.updateEmbeddingNewData()

    return json.dumps({"message": "update skills success", "skills":userSkillsDetailReponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/<userId>/experiences', methods=['PUT'])
def updateUserExperiences(userId):
    
    curr.execute("""SELECT * FROM users WHERE Id = {0}""".format(userId))
    userDataModel = curr.fetchone()
    if userDataModel is None:
        return json.dumps({"message": "user not found"}), 404, {'ContentType':'application/json'}
    
    request_data = request.get_json()
    experiences = request_data['experiences']

    curr.execute("""DELETE FROM experiences WHERE userId = {0}""".format(userId))
    
    insertUserExperienceQuery = generateInsertUserExperienceQuery(userId, experiences)
    curr.execute(insertUserExperienceQuery)
    conn.commit()

    # get user experiences
    curr.execute("""SELECT * FROM experiences WHERE userId = {0}""".format(userId))
    experienceDataModels = curr.fetchall()
    experiencesReponseDto = FromExperienceDataModelsToExperiencesResponseDto(experienceDataModels)

    # get data to index to ElasticSearch
    userReponseDto = getDetailsUserResponseDto(None, userId, None, experiencesReponseDto)
    userElasticSearchModel = FromUserResponseDtoToElasticSearchModel(userReponseDto)
    AutoMatching.indexNewData([userElasticSearchModel])
    AutoMatching.updateEmbeddingNewData()

    return json.dumps({"message": "update experiences success", "experiences":experiencesReponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/<userId>/posts', methods=['GET'])
def searchPostsByQuery(userId):
    queryString = request.args.get('queryString')
    isConsideringUserContext = int(request.args.get('isConsideringUserContext')) == 1 #0 is false, 1 is true

    curr.execute("""SELECT * FROM users WHERE Id = {0}""".format(userId))
    userDataModel = curr.fetchone()
    if userDataModel is None:
        return json.dumps({"message": "user not found"}), 404, {'ContentType':'application/json'}
    
    userReponseDto = FromUserDataModelToUserResponseDto(userDataModel)
    userReponseDto = getDetailsUserResponseDto(userReponseDto, None, None, None)
    
    userContextData = {
        "skills": userReponseDto["skills"],
        "experiences": userReponseDto["experiences"]
    }

    contextQuery = ""
    if isConsideringUserContext:
        contextQuery = FromUserContextDataToSystemContextQuery(userContextData)
    documents = AutoMatching.searchDocuments(queryString, contextQuery, PostType.project.value)
    postIds= []
    if documents is not None:
        postIds = [int(document.meta['id']) for document in documents['documents']]
    
        findPostsByIdsQueryString = generateFindPostsByIdsQueryString(postIds)

        curr.execute(findPostsByIdsQueryString)
        postDataModels = curr.fetchall()

        getPostsResponseDto = FromPostDataModelsToGetPostsResponseDto(postDataModels)

    sortedGetPostResponseDto= []
    orderPrecedence = [x for x in postIds]
    while len(orderPrecedence) > 0:
        for post in getPostsResponseDto:
            if post["id"] == orderPrecedence[0]:
                sortedGetPostResponseDto.append(post)
                orderPrecedence.pop(0)
                break

    return json.dumps({"message": "get posts success", "posts":sortedGetPostResponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/<userId>/otherUsers', methods=['GET'])
def searchOtherUsersByQuery(userId):
    queryString = request.args.get('queryString')
    postId = request.args.get('postId')

    contextQuery = ""
    
    if postId is not None:
        postId = int(postId)
        document = AutoMatching.getDocumentById(postId, PostType.project)
        contextQuery = document.content
  
    documents = AutoMatching.searchDocuments(queryString, contextQuery, PostType.userProfile.value)
    userIds= []
    sortedGetUserResponseDto= []

    if documents is not None:
        userIds = [int(document.meta['id']) for document in documents['documents']]
        for userId in userIds:
            userResponseDto = getDetailsUserResponseDto(None, userId, None, None)
            sortedGetUserResponseDto.append(userResponseDto)
        # findUsersByIdsQueryString = generateFindUsersByIdsQueryString(userIds)

        # curr.execute(findUsersByIdsQueryString)
        # postDataModels = curr.fetchall()

        # getPostsResponseDto = FromPostDataModelsToGetPostsResponseDto(postDataModels)

    
    # orderPrecedence = [x for x in userIds]
    # while len(orderPrecedence) > 0:
    #     for post in getPostsResponseDto:
    #         if post["id"] == orderPrecedence[0]:
    #             sortedGetPostResponseDto.append(post)
    #             orderPrecedence.pop(0)
    #             break

    return json.dumps({"message": "get users success", "users":sortedGetUserResponseDto}), 200, {'ContentType':'application/json'}
