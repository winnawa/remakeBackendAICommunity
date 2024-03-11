from app.elasticSearchConnection import AutoMatching
from app.mapper import FromSkillDataModelsToGetSkillsResponseDto, NotificationType, PostType
from app.notifications import bp
from flask import request
import json
from dataConnection import curr, conn
from app.socketConnection import socketio

@bp.route('/', methods=['POST'])
def createNotification():
    request_data = request.get_json()
    createNotificationDto = {}
    # for key in request_data:
    #     createNotificationDto[key] = request_data[key]
    # if createNotificationDto["type"] == NotificationType.projectCreation.value:
    #     # require postId
    #     postId = createNotificationDto["postId"]
    #     postDocument = AutoMatching.getDocumentById(postId,PostType.project)
    #     postContent = postDocument.meta["content"]

    #     filterParam = {
    #         "postType": "{0}".format(PostType.userProfile.value)
    #     }
    #     userDocuments = AutoMatching.searchRelatedDocuments(postContent,filterParam)
    socketio.emit("{}".format(NotificationType.projectCreation.name), {'message': "hello"})
    
    
    return json.dumps({"message": "create notification success", "notification":{}}), 200, {'ContentType':'application/json'}

@bp.route('/', methods=['GET'])
def getNotifications():
    curr.execute("""SELECT * FROM skills LIMIT 100""")
    skillDataModels = curr.fetchall()

    getSkillsResponseDto = FromSkillDataModelsToGetSkillsResponseDto(skillDataModels)


    return json.dumps({"message": "get posts success", "skills":getSkillsResponseDto}), 200, {'ContentType':'application/json'}