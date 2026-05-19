"""
PK = "USER_ID"
SK values allowed: ["TYPE#COGNITO_ID", "TYPE#EMAIL", "TYPE#PROFILE"]
attributes = ["CREATED_AT", "UPDATED_AT", "TIMESTAMP"]
Do not change PK/SK or attribute names in items.
"""
import os
from typing import Any, Dict, Optional, List
import boto3
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from datetime import datetime, timezone


# ---------------- Config ----------------
DYNAMODB_RESOURCE_ARN = "arn:aws:dynamodb:us-east-1:322828741334:table/haiku-foundation-users-table"
PK = "USER_ID"           # logical PK attribute you want to keep in items
SK = "TYPE"              # logical SK attribute you want to keep in items
# Actual DynamoDB key attribute names in the table schema:
DDB_PK_ATTR = os.getenv("DDB_PK_ATTR", "userId")
DDB_SK_ATTR = os.getenv("DDB_SK_ATTR", "metaData")  # default to 'metaData' per table definition
ALLOWED_TYPES = {"TYPE#COGNITO_ID", "TYPE#EMAIL", "TYPE#PROFILE"}


def _aws_region() -> str:
    return (
        os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or boto3.session.Session().region_name
        or "us-east-1"
    )


def _client():
    region = _aws_region()
    return boto3.client("dynamodb", region_name=region)


def _table_name_from_arn(arn: str) -> str:
    # arn:aws:dynamodb:region:acct:table/Name → return Name
    return arn.split("/", 1)[1] if "/" in arn else arn


# Singletons for (de)serialization
_SERIALIZER = TypeSerializer()
_DESERIALIZER = TypeDeserializer()


def _to_av_map(item: Dict[str, Any]) -> Dict[str, Any]:
    return {k: _SERIALIZER.serialize(v) for k, v in item.items()}


def _from_av_map(av_item: Dict[str, Any]) -> Dict[str, Any]:
    return {k: _DESERIALIZER.deserialize(v) for k, v in av_item.items()}


def _now_iso() -> str:
    # RFC3339/ISO-8601 in UTC with milliseconds
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


# --------------- Builders ---------------

def _build_item(userId: str, cognitoId: str, email: str, type_value: str) -> Dict[str, Any]:
    if not type_value or not isinstance(type_value, str):
        raise ValueError("type must be a non-empty string")
    if type_value not in ALLOWED_TYPES:
        raise ValueError(f"type must be one of {sorted(ALLOWED_TYPES)}")
    # Include both your logical attributes (PK/SK you want) and the actual table key attributes
    return {
        PK: userId,                 # your logical PK attribute retained in the item
        SK: type_value,             # your logical SK attribute retained in the item
        DDB_PK_ATTR: userId,        # actual DynamoDB partition key
        DDB_SK_ATTR: type_value,    # actual DynamoDB sort key
        "COGNITO_ID": cognitoId,
        "EMAIL": email,
        "TIMESTAMP": _now_iso(),  # single timestamp attribute
    }


# --------------- Writes -----------------

def insert_user(userId: str, cognitoId: str, email: str, type_value: str) -> Dict[str, Any]:
    """Insert a new item. If the item already exists (same userId/metaData), return the existing item."""
    item = _build_item(userId, cognitoId, email, type_value)
    # set creation/update stamps on insert
    now = _now_iso()
    item["CREATED_AT"] = now
    item["UPDATED_AT"] = now
    av_item = _to_av_map(item)
    client = _client()
    try:
        client.put_item(
            TableName=_table_name_from_arn(DYNAMODB_RESOURCE_ARN),
            Item=av_item,
            ConditionExpression="attribute_not_exists(#pk) AND attribute_not_exists(#sk)",
            ExpressionAttributeNames={"#pk": DDB_PK_ATTR, "#sk": DDB_SK_ATTR},
        )
        return item
    except client.exceptions.ConditionalCheckFailedException:
        # Item exists; return current stored value (idempotent create)
        return get_user_by_type(userId, type_value) or item


def update_user(userId: str, cognitoId: str, email: str, type_value: str) -> Dict[str, Any]:
    """Upsert/replace item (on actual table keys)."""
    item = _build_item(userId, cognitoId, email, type_value)
    # set update stamp on upsert
    item["UPDATED_AT"] = _now_iso()
    av_item = _to_av_map(item)
    _client().put_item(
        TableName=_table_name_from_arn(DYNAMODB_RESOURCE_ARN),
        Item=av_item,
    )
    return item


def create_user(userId: str, cognitoId: str, email: str) -> Dict[str, Any]:
    """Create a user PROFILE record (alias for insert_profile)."""
    return insert_profile(userId=userId, cognitoId=cognitoId, email=email)


# --------------- Reads ------------------

def get_user(userId: str, type_value: str = "TYPE#PROFILE") -> Optional[Dict[str, Any]]:
    """Fetch a user profile item, always using TYPE#PROFILE regardless of caller input."""
    type_value = "TYPE#PROFILE"
    key_av = _to_av_map({DDB_PK_ATTR: userId, DDB_SK_ATTR: type_value})
    resp = _client().get_item(TableName=_table_name_from_arn(DYNAMODB_RESOURCE_ARN), Key=key_av, ConsistentRead=False)
    av_item = resp.get("Item")
    return _from_av_map(av_item) if av_item else None


def get_user_by_type(userId: str, type_value: str) -> Optional[Dict[str, Any]]:
    key_av = _to_av_map({DDB_PK_ATTR: userId, DDB_SK_ATTR: type_value})
    resp = _client().get_item(TableName=_table_name_from_arn(DYNAMODB_RESOURCE_ARN), Key=key_av, ConsistentRead=False)
    av_item = resp.get("Item")
    return _from_av_map(av_item) if av_item else None


def list_user_items(userId: str) -> List[Dict[str, Any]]:
    # Query all items for a userId using actual table key attribute
    resp = _client().query(
        TableName=_table_name_from_arn(DYNAMODB_RESOURCE_ARN),
        KeyConditionExpression="#pk = :pk",
        ExpressionAttributeNames={"#pk": DDB_PK_ATTR},
        ExpressionAttributeValues={":pk": _SERIALIZER.serialize(userId)},
        ConsistentRead=False,
    )
    items = resp.get("Items", [])
    return [_from_av_map(av) for av in items]


# --------------- Convenience functions for each allowed TYPE ------------------

def insert_profile(userId: str, cognitoId: str = "", email: str = "") -> Dict[str, Any]:
    """Create a TYPE#PROFILE record (fails if exists)."""
    return insert_user(userId=userId, cognitoId=cognitoId, email=email, type_value="TYPE#PROFILE")


def update_profile(userId: str, cognitoId: str = "", email: str = "") -> Dict[str, Any]:
    """Upsert a TYPE#PROFILE record."""
    return update_user(userId=userId, cognitoId=cognitoId, email=email, type_value="TYPE#PROFILE")


def insert_cognito_id(userId: str, cognitoId: str) -> Dict[str, Any]:
    """Create a TYPE#COGNITO_ID record (fails if exists)."""
    return insert_user(userId=userId, cognitoId=cognitoId, email="", type_value="TYPE#COGNITO_ID")


def update_cognito_id(userId: str, cognitoId: str) -> Dict[str, Any]:
    """Upsert a TYPE#COGNITO_ID record."""
    return update_user(userId=userId, cognitoId=cognitoId, email="", type_value="TYPE#COGNITO_ID")


def insert_email(userId: str, email: str) -> Dict[str, Any]:
    """Create a TYPE#EMAIL record (fails if exists)."""
    return insert_user(userId=userId, cognitoId="", email=email, type_value="TYPE#EMAIL")


def update_email(userId: str, email: str) -> Dict[str, Any]:
    """Upsert a TYPE#EMAIL record."""
    return update_user(userId=userId, cognitoId="", email=email, type_value="TYPE#EMAIL")



# keep cognito/email helpers
# remove deprecated helpers (CREATE/UPDATE/DELETE/VIEW)

# --------------- CLI demo ---------------
if __name__ == "__main__":
    demo_user = "sughanrichardson"
    demo_cog = "94f86428-9081-70a5-44f1-7a030f617f5a"
    demo_email = "sughanrichardson@gmail.com"

    try:
        print(insert_profile(demo_user, demo_cog, demo_email))
        print(get_user(demo_user))
    except Exception as e:
        raise e
