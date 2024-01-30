from typing import Any, List
from app.models.user import User

def FromUserDataModelToUserResponseDto(userDataModel: tuple[Any, ...]):
    
    userDto = {
        "id": int(userDataModel[0]),
        "username": str(userDataModel[1]),
        "password": str(userDataModel[2]),
        "email": str(userDataModel[3]),
        "cvLink": userDataModel[4]
    }
    return userDto 

def FromUserSkillDataModelsToSkillsResponseDto(userSkillDataModels: list[tuple[Any, ...]]):
    skillIds = []
    for userSkillDataModel in userSkillDataModels:
        skillIds.append(userSkillDataModel[2])
    
    return skillIds

def FromPostSkillDataModelsToSkillsResponseDto(postSkillDataModels: list[tuple[Any, ...]]):
    skillIds = []
    for postSkillDataModel in postSkillDataModels:
        skillIds.append(postSkillDataModel[2])
    
    return skillIds

def FromPostDataModelToPostResponseDto(postDataModel: tuple[Any, ...]):
    
    postDto = {
        "id": int(postDataModel[0]),
        "title": str(postDataModel[1]),
        "creatorId": int(postDataModel[2]),
        "privacy": postDataModel[3],
        "status": postDataModel[4],
        "projectLink": postDataModel[5],
        "contactEmail": postDataModel[6],
        "objectivesProjectInformation": postDataModel[7],
        "methodologyProjectInformation": postDataModel[8],
        "datasetProjectInformation": postDataModel[9],
        "timelineProjectInformation": postDataModel[10]
    }
    return postDto 

def FromPostResponseDtoToElasticSearchModel(postReponseDto):
    postContent = ""
    if postReponseDto["title"] is not None:
        postContent = postContent + "Project Title: " + postReponseDto["title"] + "."
    if postReponseDto["objectivesProjectInformation"] is not None:
        postContent = postContent + "Project Objectives: " + postReponseDto["objectivesProjectInformation"]
    if postReponseDto["methodologyProjectInformation"] is not None:
        postContent = postContent + "Project Methodology: " + postReponseDto["methodologyProjectInformation"]
    if postReponseDto["datasetProjectInformation"] is not None:
        postContent = postContent + "Dataset Information: " + postReponseDto["datasetProjectInformation"]
    if postReponseDto["timelineProjectInformation"] is not None:
        postContent = postContent + "Project Timeline: " + postReponseDto["timelineProjectInformation"]
    if postReponseDto["skills"] is not None and len(postReponseDto["skills"]) > 0:
        skillsContent = ""
        for skill in postReponseDto["skills"]:
            skillsContent = skillsContent + skill["skillName"] + ", "
        postContent = postContent + "Skills: " + skillsContent[:-2] + "."

    return {
        'content' : postContent,
        'meta' : {
            'id' : str(postReponseDto['id'])
        }
    }

def FromUserContextDataToSystemContextQuery(userContextData):
    contextQuery = ""
    newSentence = False
    for key in userContextData:
        if  key == "skills" and len(userContextData["skills"]) > 0:
            if not(newSentence):
                contextQuery = contextQuery + "for a user who has skills in "
                skillsContent = ""
                for skill in userContextData["skills"]:
                    skillsContent = skillsContent + skill["skillName"] + ", "
                contextQuery = contextQuery + skillsContent[:-2] + "."
                newSentence = True
        # if key == "experiences":
            # dosth
    return contextQuery

def FromPostSkillJoinSkillDataModelsToSkillsDetailResponseDto(postSkillJoinSkillDataModels: list[tuple[Any, ...]]):
    skillIds = []
    for postSkillJoinSkillDataModel in postSkillJoinSkillDataModels:
        skillIds.append({
            'id': postSkillJoinSkillDataModel[3],
            'skillName': postSkillJoinSkillDataModel[4],
        })
    
    return skillIds

def FromUserSkillJoinSkillDataModelsToSkillsDetailResponseDto(userSkillJoinSkillDataModels: list[tuple[Any, ...]]):
    skills = []
    for userSkillJoinSkillDataModel in userSkillJoinSkillDataModels:
        skills.append({
            'id': userSkillJoinSkillDataModel[3],
            'skillName': userSkillJoinSkillDataModel[4],
        })
    
    return skills

def FromPostDataModelsToGetPostsResponseDto(postDataModels: list[tuple[Any, ...]]):
    posts = []
    for postDataModel in postDataModels:
        postDto = {
            "id": int(postDataModel[0]),
            "title": str(postDataModel[1]),
            "creatorId": int(postDataModel[2]),
            "privacy": postDataModel[3],
            "status": postDataModel[4],
            "projectLink": postDataModel[5],
            "contactEmail": postDataModel[6],
            "objectivesProjectInformation": postDataModel[7],
            "methodologyProjectInformation": postDataModel[8],
            "datasetProjectInformation": postDataModel[9],
            "timelineProjectInformation": postDataModel[10]
        }
        posts.append(postDto)
    return posts
