from app.elasticSearchConnection import AutoMatching
from app.mapper import FromNotificationDataModelToNotificationReponseDto, FromNotificationDataModelsToNotificationsReponseDto, FromSkillDataModelsToGetSkillsResponseDto, NotificationType, PostType
from app.notifications import bp
from flask import request
import json
from app.queryGenerate import generateInsertNotificationQuery, generateInsertUserIsNotifiedByNotificationQuery
from dataConnection import curr, conn
from app.socketConnection import socketio
from datetime import datetime

@bp.route('/', methods=['POST'])
def createNotification():
    request_data = request.get_json()
    createNotificationDto = {}
    for key in request_data:
        createNotificationDto[key] = request_data[key]

    # add createdTime
    now = datetime.now()
    date_time = now.strftime("%Y/%m/%d, %H:%M:%S")
    print("date and time:",date_time)
    createNotificationDto["createdTime"] = date_time

    if createNotificationDto["type"] == NotificationType.projectCreation.value:
        # require postId
        postId = createNotificationDto["postId"]
        postDocument = AutoMatching.getDocumentById(postId,PostType.project)
        if postDocument is None:
            return json.dumps({"message": "project matching postId not found"}), 404, {'ContentType':'application/json'}

        postContent = postDocument.content
        creatorId = postDocument.meta["creatorId"] if "creatorId" in postDocument.meta else "0"

        filterParam = {
            "postType": "{0}".format(PostType.userProfile.value),
            "id": {"$ne": "{}".format(creatorId)}
        }
        userDocuments = AutoMatching.searchRelatedDocuments(postContent,filterParam)
        userIds = [userDocument.meta["id"] for userDocument in userDocuments["documents"]]
        
        insertNotificationQuery = generateInsertNotificationQuery(createNotificationDto)
        curr.execute(insertNotificationQuery)
        conn.commit()

        # need to take in DESC order
        curr.execute("""SELECT * FROM notifications WHERE type = '{0}' and notificationDescription = '{1}' and createdTime = '{2}' ORDER BY createdTime DESC""".format(createNotificationDto["type"], createNotificationDto["notificationDescription"], createNotificationDto["createdTime"]))
        notificationDataModel = curr.fetchone()
        notificationReponseDto = FromNotificationDataModelToNotificationReponseDto(notificationDataModel)
      
        # create notification history for each user
        insertUserIsNotifiedByNotificationQuery = generateInsertUserIsNotifiedByNotificationQuery(notificationReponseDto,userIds)
        curr.execute(insertUserIsNotifiedByNotificationQuery)
        conn.commit()

        notificationReponseDto["receiverUserIds"] = userIds
        # send notificationResponseDto via socket, remember to include the userList
        socketio.emit("{}".format(NotificationType.projectCreation.name), {'message': notificationReponseDto})
    
    
    return json.dumps({"message": "create notification success", "notification":notificationReponseDto}), 200, {'ContentType':'application/json'}

@bp.route('/', methods=['GET'])
def getNotifications():

    userId = int(request.args.get('userId')) if request.args.get('userId') is not None else 1
   
    # need to take in DESC order
    curr.execute("""SELECT * FROM notifications AS N JOIN user_is_notified_by_notification AS UINBN ON N.Id = UINBN.NotificationId WHERE UINBN.UserId = {} ORDER BY createdTime DESC""".format(userId))
    notificationDataModels = curr.fetchall()
    notificationsReponseDto = FromNotificationDataModelsToNotificationsReponseDto(notificationDataModels)

    return json.dumps({"message": "get notifications success", "notifications":notificationsReponseDto}), 200, {'ContentType':'application/json'}