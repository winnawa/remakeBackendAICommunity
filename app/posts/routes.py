from app.mapper import FromPostDataModelToPostResponseDto
from app.posts import bp
from flask import request,Flask
import json
from app.dataConnection import curr, conn
from app.queryGenerate import generateInsertPostQuery

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

    return json.dumps({"message": "create post success", "post":postReponseDto}), 200, {'ContentType':'application/json'}
