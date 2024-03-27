from app.elasticSearchConnection import AutoMatching
from app.queryGenerate import generateFindPostsByIdsQueryString, generateInsertFriendshipQuery, generateInsertSearchHistoryQuery, generateInsertUserExperienceQuery, generateInsertUserQuery, generateInsertUserSkillQuery
from app.repoAbstraction import getDetailsUserResponseDto
from app.users import bp
from flask import request
import json
from dataConnection import curr, conn
from app.mapper import FromEventPostHasUserJoinsUserDataModelsToEventParticipantsResponseDto, FromExperienceDataModelsToExperiencesResponseDto, FromFriendshipJoinUserDataModelsToGetFriendsResponseDto, FromPostDataModelToPostResponseDto, FromPostDataModelsToGetPostsResponseDto, FromPostHasStarDataModelsToStarsResponseDto, FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto, FromProjectPostHasUserJoinsUserDataModelsToProjectParticipantsResponseDto, FromSearchHistoryDataModelToCreateSearchHistoryResponseDto, FromSearchHistoryDataModelsToGetSearchHistoriesResponseDto, FromUserContextDataToSystemContextQuery, FromUserDataModelToUserResponseDto, FromUserResponseDtoToElasticSearchModel, FromUserSkillJoinSkillDataModelsToSkillsDetailResponseDto, PostType

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
      
    userReponseDto = getDetailsUserResponseDto(userReponseDto, None, None, None)

    # index data to elastic search
    userElasticSearchModel = FromUserResponseDtoToElasticSearchModel(userReponseDto)
    AutoMatching.indexNewData([userElasticSearchModel])
    filterParam = {
        "_id": "{0}_{1}".format(PostType.userProfile.name, userReponseDto['id'])
    }
    AutoMatching.updateEmbeddingNewData(filterParam, True)

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

    # get details (exps and skills)
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

    # get data to index to ElasticSearch
    userDocument = AutoMatching.getDocumentById(userId,PostType.userProfile)

    userReponseDto = getDetailsUserResponseDto(userReponseDto, userId, None, None)
    userElasticSearchModel = FromUserResponseDtoToElasticSearchModel(userReponseDto)

    userDocument.meta["content"] = userElasticSearchModel["content"]
    AutoMatching.indexNewData([userDocument])
    filterParam = {
        "_id": "{0}_{1}".format(PostType.userProfile.name, userId)
    }
    AutoMatching.updateEmbeddingNewData(filterParam, True)

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
    userDocument = AutoMatching.getDocumentById(userId,PostType.userProfile)

    userReponseDto = getDetailsUserResponseDto(None, userId, userSkillsDetailReponseDto, None)
    userElasticSearchModel = FromUserResponseDtoToElasticSearchModel(userReponseDto)
    userDocument.meta["content"] = userElasticSearchModel["content"]
    AutoMatching.indexNewData([userDocument])
    filterParam = {
        "_id": "{0}_{1}".format(PostType.userProfile.name, userId)
    }
    AutoMatching.updateEmbeddingNewData(filterParam, True)

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
    userDocument = AutoMatching.getDocumentById(userId,PostType.userProfile)

    userReponseDto = getDetailsUserResponseDto(None, userId, None, experiencesReponseDto)
    userElasticSearchModel = FromUserResponseDtoToElasticSearchModel(userReponseDto)
    userDocument.meta["content"] = userElasticSearchModel["content"]
    AutoMatching.indexNewData([userDocument])
    filterParam = {
        "_id": "{0}_{1}".format(PostType.userProfile.name, userId)
    }
    AutoMatching.updateEmbeddingNewData(filterParam, True)

    return json.dumps({"message": "update experiences success", "experiences":experiencesReponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/<userId>/posts', methods=['GET'])
def searchPostsByQuery(userId):
    queryString = request.args.get('queryString')
    if queryString is None:
        queryString = ""
    isConsideringUserContext = (int(request.args.get('isConsideringUserContext')) if request.args.get('isConsideringUserContext') is not None else 0) == 1 #0 is false, 1 is true
    postId = request.args.get('postId')

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

    filterParam = {
        "postType": PostType.project.value,
        "creatorId": {"$ne": "{}".format(userId)}
    }

    if postId is not None:
        postId = int(postId)
        document = AutoMatching.getDocumentById(postId, PostType.project)
        if document is None:
            document = AutoMatching.getDocumentById(postId, PostType.article)
        if document is None:
            document = AutoMatching.getDocumentById(postId, PostType.event)
        if document is None:
            return  json.dumps({"message": "no post matching postId"}), 400, {'ContentType':'application/json'}

        queryString += document.content
  
        filterParam["id"]=  {"$ne": "{}".format(postId)}

    documents = AutoMatching.searchDocuments(queryString, contextQuery, filterParam)
    postIds= []
    sortedGetPostResponseDto= []
    
    if documents is not None:
        postIds = [int(document.meta['id']) for document in documents['documents']]
    
        for postId in postIds:
            curr.execute("""SELECT * FROM posts WHERE Id = {0}""".format(postId))
            postDataModel = curr.fetchone()
            if postDataModel is None:
                return json.dumps({"message": "post not found{}".format(postId)}), 404, {'ContentType':'application/json'}
            
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

            sortedGetPostResponseDto.append(postReponseDto)
  
    return json.dumps({"message": "get posts success", "posts":sortedGetPostResponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/<userId>/otherUsers', methods=['GET'])
def searchOtherUsersByQuery(userId):
    queryString = request.args.get('queryString')
    if queryString is None:
        queryString = ""
    postId = request.args.get('postId')

    contextQuery = ""
    
    if postId is not None:
        postId = int(postId)
        document = AutoMatching.getDocumentById(postId, PostType.project)
        if document is None:
            document = AutoMatching.getDocumentById(postId, PostType.article)
        if document is None:
            document = AutoMatching.getDocumentById(postId, PostType.event)
        if document is None:
            return  json.dumps({"message": "no post matching postId"}), 400, {'ContentType':'application/json'}

        contextQuery = document.content
  
    filterParam = {
        "postType": PostType.userProfile.value,
        "id": {"$ne": "{}".format(userId)}
    }
    # exclude user from this project
    if postId is not None:
        excludeIds = document.meta["participants"] if "participants" in document.meta else []
        print(excludeIds)
        filterParam = {
            "postType": PostType.userProfile.value,
            "id": {"$nin": excludeIds}
        }

    documents = AutoMatching.searchDocuments(queryString, contextQuery, filterParam)
    userIds= []
    sortedGetUserResponseDto= []

    # get the searcher document to get friendIds, thus we know whether user and searcher is friend or not
    seacherDocument = AutoMatching.getDocumentById(userId, PostType.userProfile)
    friendIds = seacherDocument.meta["friendIds"] if "friendIds" in seacherDocument.meta else []

    if documents is not None:
        userIds = [int(document.meta['id']) for document in documents['documents']]
        for userId in userIds:
            userResponseDto = getDetailsUserResponseDto(None, userId, None, None)

            # check if stranger or friend
            userResponseDto["isFriend"] = userResponseDto["id"] in friendIds 
            
            sortedGetUserResponseDto.append(userResponseDto)
        
        ############################################################################### 
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

@bp.route('/<userId>/searchHistory', methods=['GET'])
def getUserSearchHistory(userId):
    curr.execute("""SELECT * FROM users WHERE id = {0} """.format(userId))
    userDataModel = curr.fetchone()
    if userDataModel is None:
        return json.dumps({"message": "user not found"}), 404, {'ContentType':'application/json'}

    curr.execute("""SELECT * FROM searchHistory WHERE userId = {0} ORDER BY Id DESC LIMIT 3""".format(userId))
    searchHistoryDataModels = curr.fetchall()

    createSearchHistoryReponseDto = FromSearchHistoryDataModelsToGetSearchHistoriesResponseDto(searchHistoryDataModels)

    return json.dumps({"message": "get searchHistory success", "searchHistory":createSearchHistoryReponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/<userId>/searchHistory', methods=['POST'])
def addSearchHistory(userId):
    request_data = request.get_json()
    createSearchHistoryDto = {}
    for key in request_data:
        createSearchHistoryDto[key] = request_data[key]
    # expect userId, searchString, date

    curr.execute("""SELECT * FROM users WHERE id = {0} """.format(userId))
    userDataModel = curr.fetchone()
    if userDataModel is None:
        return json.dumps({"message": "user not found"}), 404, {'ContentType':'application/json'}

    curr.execute("""DELETE FROM searchHistory WHERE userId = {0} and searchString = '{1}'""".format(userId, createSearchHistoryDto["searchString"]))

    insertSearchHistoryQuery = generateInsertSearchHistoryQuery(userId, createSearchHistoryDto)
    curr.execute(insertSearchHistoryQuery)
    conn.commit()

    curr.execute("""SELECT * FROM searchHistory WHERE userId = {0} and searchString = '{1}'""".format(userId, createSearchHistoryDto["searchString"]))
    searchHistoryDataModel = curr.fetchone()
    createSearchHistoryReponseDto = FromSearchHistoryDataModelToCreateSearchHistoryResponseDto(searchHistoryDataModel)

    return json.dumps({"message": "create user success", "searchHistory":createSearchHistoryReponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/<userId>/friends', methods=['POST'])
def addFriend(userId):
    request_data = request.get_json()
    createFriendshipDto = {}
    for key in request_data:
        createFriendshipDto[key] = request_data[key]
    # expect secondUserId, friendshipDescription

    firstUserId = userId
    secondUserId = createFriendshipDto["friendId"]

    curr.execute("""SELECT * FROM users WHERE id = {0} """.format(firstUserId))
    userDataModel = curr.fetchone()
    if userDataModel is None:
        return json.dumps({"message": "user not found"}), 404, {'ContentType':'application/json'}

    curr.execute("""SELECT * FROM users WHERE id = {0} """.format(secondUserId))
    userDataModel = curr.fetchone()
    if userDataModel is None:
        return json.dumps({"message": "user not found"}), 404, {'ContentType':'application/json'}
    
    curr.execute("""SELECT * FROM user_is_friend_with_user WHERE (firstUserId = {0} and secondUserId = {1}) or (firstUserId = {1} and secondUserId = {0})""".format(firstUserId, secondUserId))
    userDataModel = curr.fetchone()
    if userDataModel is not None:
        return json.dumps({"message": "friendship existed"}), 400, {'ContentType':'application/json'}
    
    insertFriendshipQuery = generateInsertFriendshipQuery(userId,createFriendshipDto)
    curr.execute(insertFriendshipQuery)

    createSecondUserFriendshipDto = {}
    for key in createFriendshipDto:
        if key != "friendId" and key != "friendshipDescription":
            createSecondUserFriendshipDto[key] = createFriendshipDto[key]
    createSecondUserFriendshipDto["friendId"] = firstUserId
    createSecondUserFriendshipDto["friendshipDescription"] = ""
    insertFriendshipQuery = generateInsertFriendshipQuery(secondUserId,createSecondUserFriendshipDto)
    curr.execute(insertFriendshipQuery)
    conn.commit()

    firstUserDocument = AutoMatching.getDocumentById(userId,PostType.userProfile)
    firstUserFriendIds = []
    if "friendIds" in firstUserDocument.meta:
        firstUserFriendIds = firstUserDocument.meta["friendIds"]
    firstUserFriendIds.append(secondUserId)
    firstUserDocument.meta["friendIds"] = firstUserFriendIds
    AutoMatching.indexNewData([firstUserDocument])
    filterParam = {
        "_id": "{0}_{1}".format(PostType.userProfile.name, firstUserId)
    }
    AutoMatching.updateEmbeddingNewData(filterParam, True)

    secondUserDocument = AutoMatching.getDocumentById(secondUserId, PostType.userProfile)
    secondUserFriendIds = []
    if "friendIds" in secondUserDocument.meta:
        secondUserFriendIds = secondUserDocument.meta["friendIds"]
    secondUserFriendIds.append(firstUserId)
    secondUserDocument.meta["friendIds"] = secondUserFriendIds
    AutoMatching.indexNewData([secondUserDocument])
    filterParam = {
        "_id": "{0}_{1}".format(PostType.userProfile.name, secondUserId)
    }
    AutoMatching.updateEmbeddingNewData(filterParam, True)

    # will find the document and add userId to the list. Later on, we can filter and query for search history
    # "filters":{
    #             "postType": postType,
    #             "friendIds": 10
    #         }

    # possibly creating a document type friendshipPost

    return json.dumps({"message": "add friendship success"}), 200, {'ContentType':'application/json'}


@bp.route('/<userId>/friends', methods=['GET'])
def getUserFriends(userId):
    getFriendsResponseDto = []
    isRecommendingNewFriendship = (int(request.args.get('isRecommendingNewFriendship')) if request.args.get('isRecommendingNewFriendship') is not None else 0) == 1 #0 is false, 1 is true
    
    if isRecommendingNewFriendship:
        userDocument = AutoMatching.getDocumentById(userId, PostType.userProfile)
        # get user friendList
        friendIds = userDocument.meta["friendIds"] if "friendIds" in userDocument.meta else []
        # get user search history
        curr.execute("""SELECT * FROM searchHistory WHERE userId = {0} LIMIT 5""".format(userId))
        searchHistoryDataModels = curr.fetchall()

        # use elasticsearch to find the document containing number in the list
        userSearchHistories = FromSearchHistoryDataModelsToGetSearchHistoriesResponseDto(searchHistoryDataModels)
        print(userSearchHistories)
        excludeIds = [id for id in friendIds]
        excludeIds.append(userId)

        userIds= []
        queryStringSuggestions = []
        for userSearchHistory in userSearchHistories:
            # filter option here
            filterParam = {
                "postType": PostType.userProfile.value,
                # need to have friends in common
                "friendIds": friendIds,
                "id": {"$nin": excludeIds}
            }
            documents = AutoMatching.searchDocuments(userSearchHistory["searchString"], "", filterParam)
            if documents is not None:
                for document in documents["documents"]:
                    if document.meta["id"] not in userIds:
                        userIds.append(document.meta["id"])
                        queryStringSuggestions.append(userSearchHistory["searchString"])
                    if  len(userIds) > 3:
                        break
                if  len(userIds) > 3:
                        break    
            
        for userId, queryStringSuggestion in zip(userIds,queryStringSuggestions):
            userResponseModel = getDetailsUserResponseDto(None, userId, None, None)
            userResponseModel["suggestionQueryString"] = queryStringSuggestion
            getFriendsResponseDto.append(userResponseModel)
        
        return json.dumps({"message": "get friends suggestion success", "friends":getFriendsResponseDto}), 200, {'ContentType':'application/json'}

    else:
        curr.execute("""SELECT * 
            FROM user_is_friend_with_user as UIFWU  
            JOIN users as U on UIFWU.secondUserId = U.id  
            WHERE (UIFWU.firstUserId = {0}) LIMIT 100""".format(userId))
        friendshipJoinUserDataModels = curr.fetchall()

        friendModels = FromFriendshipJoinUserDataModelsToGetFriendsResponseDto(friendshipJoinUserDataModels)
        getFriendsResponseDto = []
        for friendModel in friendModels:
            detailedFriendModel = getDetailsUserResponseDto(friendModel, None, None, None)
            getFriendsResponseDto.append(detailedFriendModel)
    return json.dumps({"message": "get friends success", "friends":getFriendsResponseDto}), 200, {'ContentType':'application/json'}
