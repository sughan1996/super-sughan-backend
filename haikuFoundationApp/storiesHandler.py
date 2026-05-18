"""
PK = "CONTENT_ID"
SK = ["TYPE#CREATE", "TYPE#DELETE", "TYPE#UPDATE"]
attributes = ["CREATED_AT", "UPDATED_AT", "CONTENT", "USER_ID"]
"""

def readItemWithAttributes(contentId, type, createdAt, updatedAt, content, userId):
    return {
        PK: contentId,
        SK: type,
        "CREATED_AT": createdAt,
        "UPDATED_AT": updatedAt,
        "CONTENT": content,
        "USER_ID": userId
    }


def writewithAttributes(contentId, type, createdAt, updatedAt, content, userId):
    return {
        PK: contentId,
        SK: type,
        "CREATED_AT": createdAt,
        "UPDATED_AT": updatedAt,
        "CONTENT": content,
        "USER_ID": userId
    }