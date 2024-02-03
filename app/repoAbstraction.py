from app.dataConnection import curr, conn
from app.mapper import FromExperienceDataModelsToExperiencesResponseDto, FromUserDataModelToUserResponseDto, FromUserSkillDataModelsToSkillsResponseDto, FromUserSkillJoinSkillDataModelsToSkillsDetailResponseDto

def getDetailsUserResponseDto(userReponseDto,userId,userSkillsDetailReponseDto,experiencesResponseDto):
    
    if  userReponseDto is None:
        curr.execute("""SELECT * FROM users WHERE Id = {0}""".format(userId))
        userDataModel = curr.fetchone()
        userReponseDto = FromUserDataModelToUserResponseDto(userDataModel)

    if userId is None:
        userId = userReponseDto["id"]

    if userSkillsDetailReponseDto is None:
        curr.execute("""SELECT * FROM users_has_skills AS UHS JOIN skills AS S ON UHS.skillId = S.id
                  WHERE UHS.userId = {0}""".format(userId))
        userSkillJoinSkillDataModels = curr.fetchall()
        userSkillsDetailReponseDto = FromUserSkillJoinSkillDataModelsToSkillsDetailResponseDto(userSkillJoinSkillDataModels)

    if experiencesResponseDto is None:
        curr.execute("""SELECT * FROM experiences WHERE userId = {0}""".format(userId))
        experienceDataModels = curr.fetchall()
        experiencesResponseDto = FromExperienceDataModelsToExperiencesResponseDto(experienceDataModels)

    userReponseDto["skills"] = userSkillsDetailReponseDto
    userReponseDto["experiences"] = experiencesResponseDto

    return userReponseDto