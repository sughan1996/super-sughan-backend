"""
PK = "USER_ID"
SK values allowed: ["TYPE#COGNITO_ID", "TYPE#EMAIL", "TYPE#CREATE", "TYPE#UPDATE", "TYPE#DELETE"]
Do not change PK/SK or attribute names in items.
"""
import os
from typing import Any, Dict, Optional, List
import boto3
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer


# ---------------- Config ----------------
DYNAMODB_RESOURCE_ARN = "arn:aws:dynamodb:us-east-1:322828741334:table/haiku-foundation-users-table"
PK = "USER_ID"
SK = "TYPE"
ALLOWED_TYPES = {"TYPE#COGNITO_ID", "TYPE#EMAIL", "TYPE#CREATE", "TYPE#UPDATE", "TYPE#DELETE"}


def _aws_region() -> str:
    # Resolve region from env or current session; default to us-east-1 to avoid None endpoint
    return (
        os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or boto3.session.Session().region_name
        or "us-east-1"
    )


def _client():
    try:
        region = _aws_region()
        endpoint_url = os.getenv("DYNAMODB_ENDPOINT_URL")  # optional: for local testing
        client = boto3.client("dynamodb", region_name=region, endpoint_url=endpoint_url)
    except Exception as e:
        print("Error creating DynamoDB client:", str(e))
        raise
    return client


# Singletons for (de)serialization
_SERIALIZER = TypeSerializer()
_DESERIALIZER = TypeDeserializer()


def _to_av_map(item: Dict[str, Any]) -> Dict[str, Any]:
    return {k: _SERIALIZER.serialize(v) for k, v in item.items()}


def _from_av_map(av_item: Dict[str, Any]) -> Dict[str, Any]:
    return {k: _DESERIALIZER.deserialize(v) for k, v in av_item.items()}


# --------------- Builders ---------------

def _build_item(userId: str, cognitoId: str, email: str, type_value: str) -> Dict[str, Any]:
    if not type_value or not isinstance(type_value, str):
        raise ValueError("type must be a non-empty string")
    return {
        PK: userId,
        SK: type_value,
        "COGNITO_ID": cognitoId,
        "EMAIL": email,
    }


# --------------- Writes -----------------

def insert_user(userId: str, cognitoId: str, email: str, type_value: str) -> Dict[str, Any]:
    """Insert a new item. Fails if item with same PK/SK exists."""
    item = _build_item(userId, cognitoId, email, type_value)
    av_item = _to_av_map(item)
    _client().put_item(
        TableName=DYNAMODB_RESOURCE_ARN,
        Item=av_item,
        ConditionExpression="attribute_not_exists(#pk) AND attribute_not_exists(#sk)",
        ExpressionAttributeNames={"#pk": PK, "#sk": SK},
    )
    return item


def update_user(userId: str, cognitoId: str, email: str, type_value: str) -> Dict[str, Any]:
    """Upsert by default; if you need strict update-only, enable the condition."""
    item = _build_item(userId, cognitoId, email, type_value)
    av_item = _to_av_map(item)
    _client().put_item(
        TableName=DYNAMODB_RESOURCE_ARN,
        Item=av_item,
        # ConditionExpression="attribute_exists(#pk) AND attribute_exists(#sk)",
        # ExpressionAttributeNames={"#pk": PK, "#sk": SK},
    )
    return item


def create_user(userId: str, cognitoId: str, email: str) -> Dict[str, Any]:
    return insert_user(userId, cognitoId, email, "TYPE#CREATE")


# --------------- Reads ------------------

def get_user(userId: str, type_value: str) -> Optional[Dict[str, Any]]:
    key_av = _to_av_map({PK: userId, SK: type_value})
    resp = _client().get_item(TableName=DYNAMODB_RESOURCE_ARN, Key=key_av, ConsistentRead=False)
    av_item = resp.get("Item")
    return _from_av_map(av_item) if av_item else None


def list_user_items(userId: str) -> List[Dict[str, Any]]:
    # Query all items for a userId
    resp = _client().query(
        TableName=DYNAMODB_RESOURCE_ARN,
        KeyConditionExpression=f"#{PK} = :pk",
        ExpressionAttributeNames={f"#{PK}": PK},
        ExpressionAttributeValues={":pk": _SERIALIZER.serialize(userId)},
        ConsistentRead=False,
    )
    items = resp.get("Items", [])
    return [_from_av_map(av) for av in items]


# --------------- CLI demo ---------------
if __name__ == "__main__":
    demo_user = os.getenv("DEMO_USER_ID", "sughanrichardson")
    demo_cog = os.getenv("DEMO_COGNITO_ID", "94f86428-9081-70a5-44f1-7a030f617f5a")
    demo_email = os.getenv("DEMO_EMAIL", "sughanrichardson@gmail.com")

    try:
        print(create_user(demo_user, demo_cog, demo_email))
        print(get_user(demo_user, "TYPE#CREATE"))
    except Exception as e:
        print("Error:", str(e))
