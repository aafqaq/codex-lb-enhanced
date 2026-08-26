from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel


class DashboardModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        ser_json_timedelta="iso8601",
    )

    @field_serializer("*", when_used="json")
    def serialize_datetime_as_utc(value, _info):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.isoformat() + "Z"
            return value.isoformat().replace("+00:00", "Z")
        return value
