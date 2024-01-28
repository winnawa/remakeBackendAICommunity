from typing import Any
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

def FromPostDataModelToPostResponseDto(postDataModel: tuple[Any, ...]):
    
    postDto = {
        "id": int(postDataModel[0]),
        "title": str(postDataModel[1]),
        "creatorId": int(postDataModel[2]),
        "privacy": postDataModel[3],
        "status": postDataModel[4],
        "projectLink": postDataModel[5],
        "contactEmail": postDataModel[6],
        "methodologyProjectInformation": postDataModel[7],
        "datasetProjectInformation": postDataModel[8],
        "timelineProjectInformation": postDataModel[9]
    }
    return postDto 
