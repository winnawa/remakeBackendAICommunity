from app.mapper import FromPostDataModelToPostResponseDto, FromPostResponseDtoToElasticSearchModel
from app.posts import bp
from flask import request
import json
from app.dataConnection import curr, conn
from app.queryGenerate import generateInsertPostQuery
from app.elasticSearchConnection import AutoMatching

@bp.route('/', methods=['POST'])
def createPost():
    request_data = request.get_json()
    createPostDto = {}
    for key in request_data:
        createPostDto[key] = request_data[key]

    insertPostQuery = generateInsertPostQuery(createPostDto)
    curr.execute(insertPostQuery)
    conn.commit()

    curr.execute("""SELECT * FROM posts WHERE title = '{0}' """.format(createPostDto["title"]))
    postDataModel = curr.fetchone()
    postReponseDto = FromPostDataModelToPostResponseDto(postDataModel)

    postElasticSearchModel = FromPostResponseDtoToElasticSearchModel(postReponseDto)
    AutoMatching.indexNewData([postElasticSearchModel])
    AutoMatching.updateEmbeddingNewData()

    return json.dumps({"message": "create post success", "post":postReponseDto}), 200, {'ContentType':'application/json'}
