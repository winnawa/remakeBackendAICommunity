from app.queryGenerate import generateInsertUserQuery, generateInsertUserSkillQuery
from app.users import bp
from flask import request
import json
from app.dataConnection import curr, conn
from app.mapper import FromUserDataModelToUserResponseDto, FromUserSkillDataModelsToSkillsResponseDto

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
    # updateUserSkillsDto = {
    #     "skills": request_data['skills'],
    # }
    skillIds = request_data['skills']

    curr.execute("""DELETE FROM users_has_skills WHERE userId = {0}""".format(userId))
    
    insertUserSkillQuery = generateInsertUserSkillQuery(userId, skillIds)
    curr.execute(insertUserSkillQuery)
    conn.commit()
    
    curr.execute("""SELECT * FROM users_has_skills WHERE userId = {0}""".format(userId))
    
    userSkillDataModels = curr.fetchall()
    skillsReponseDto = FromUserSkillDataModelsToSkillsResponseDto(userSkillDataModels)

    return json.dumps({"message": "update skills success", "skills":skillsReponseDto}), 200, {'ContentType':'application/json'}


@bp.route('/<userId>/posts', methods=['PUT'])
def updateUserSkills(userId):
    
    curr.execute("""SELECT * FROM users WHERE Id = {0}""".format(userId))
    userDataModel = curr.fetchone()
    if userDataModel is None:
        return json.dumps({"message": "user not found"}), 404, {'ContentType':'application/json'}

    request_data = request.get_json()
    # updateUserSkillsDto = {
    #     "skills": request_data['skills'],
    # }
    skillIds = request_data['skills']

    curr.execute("""DELETE FROM users_has_skills WHERE userId = {0}""".format(userId))
    
    insertUserSkillQuery = generateInsertUserSkillQuery(userId, skillIds)
    curr.execute(insertUserSkillQuery)
    conn.commit()
    
    curr.execute("""SELECT * FROM users_has_skills WHERE userId = {0}""".format(userId))
    
    userSkillDataModels = curr.fetchall()
    skillsReponseDto = FromUserSkillDataModelsToSkillsResponseDto(userSkillDataModels)

    return json.dumps({"message": "update skills success", "skills":skillsReponseDto}), 200, {'ContentType':'application/json'}