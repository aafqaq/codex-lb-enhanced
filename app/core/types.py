from __future__ import annotations

from collections.abc import Mapping

type JsonValue = bool | int | float | str | None | list[JsonValue] | Mapping[str, JsonValue]
type JsonObject = Mapping[str, JsonValue]
