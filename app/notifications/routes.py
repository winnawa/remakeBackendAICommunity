from app.mapper import FromSkillDataModelsToGetSkillsResponseDto
from app.skills import bp
from flask import request
import json
from dataConnection import curr, conn

# @bp.route('/', methods=['POST'])
# def createPost():
#     return json.dumps({"message": "not yet implemented", "skills":{}}), 200, {'ContentType':'application/json'}

@bp.route('/', methods=['GET'])
def getNotifications():
    curr.execute("""SELECT * FROM skills LIMIT 100""")
    skillDataModels = curr.fetchall()

    getSkillsResponseDto = FromSkillDataModelsToGetSkillsResponseDto(skillDataModels)


    return json.dumps({"message": "get posts success", "skills":getSkillsResponseDto}), 200, {'ContentType':'application/json'}