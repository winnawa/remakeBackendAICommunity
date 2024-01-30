from app.mapper import FromPostDataModelToPostResponseDto, FromPostDataModelsToGetPostsResponseDto, FromPostResponseDtoToElasticSearchModel, FromPostSkillDataModelsToSkillsResponseDto, FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto
from app.posts import bp
from flask import request
import json
from app.dataConnection import curr, conn
from app.queryGenerate import generateInsertPostQuery, generateInsertPostSkillQuery
# from app.elasticSearchConnection import AutoMatching

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

    insertPostQuery = generateInsertPostQuery(createPostDto)
    curr.execute(insertPostQuery)
    conn.commit()

    curr.execute("""SELECT * FROM posts WHERE title = '{0}' """.format(createPostDto["title"]))
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
    # AutoMatching.indexNewData([postElasticSearchModel])
    # AutoMatching.updateEmbeddingNewData()

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
    return json.dumps({"message": "update skills success", "skills":skillsReponseDto}), 200, {'ContentType':'application/json'}


@bp.route('/', methods=['GET'])
def getPosts():
    page = int(request.args.get('page')) if request.args.get('page') is not None else 0
    size = int(request.args.get('size')) if request.args.get('size') is not None else 10

    curr.execute("""SELECT * FROM posts LIMIT 100""")
    postsDataModels = curr.fetchall()

    startPoint = page*size
    endPoint = (page+1)*size if (page+1)*size < len(postsDataModels) else len(postsDataModels)
    returnedPostsResponseDto = []
    if startPoint < len(postsDataModels):
        paginatedPostDataModels = [postsDataModels[i] for i in range(startPoint,endPoint)]
        returnedPostsResponseDto = FromPostDataModelsToGetPostsResponseDto(paginatedPostDataModels)


    return json.dumps({"message": "get posts success", "posts":returnedPostsResponseDto}), 200, {'ContentType':'application/json'}