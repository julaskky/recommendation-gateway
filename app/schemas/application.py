
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MappingField(BaseModel):
    """
    Defines how one source field maps to a canonical field.
    """

    model_config = ConfigDict(extra="forbid")

    source: str | None = None

    value: Any = None

    default: Any = None

    transform: str | None = None

    value_map: dict[str, Any] = Field(default_factory=dict)

    required: bool = False

    @model_validator(mode="after")
    def validate_mapping(self):
        if self.source is None and self.value is None and self.default is None:
            raise ValueError(
                "A mapping must define source, value, or default."
            )

        allowed_transforms = {
            "identity",
            "lowercase",
            "uppercase",
            "integer",
            "float",
            "string",
            "boolean",
        }

        if self.transform and self.transform not in allowed_transforms:
            raise ValueError(
                f"Unsupported transformation: {self.transform}"
            )

        return self


class CollectionMapping(BaseModel):
    """
    Defines how a list of application records maps into
    a canonical collection.
    """

    model_config = ConfigDict(extra="forbid")

    source: str

    fields: dict[str, MappingField]

    defaults: dict[str, Any] = Field(default_factory=dict)


class ApplicationMapping(BaseModel):
    """
    Complete integration configuration for an application.
    """

    model_config = ConfigDict(extra="forbid")

    application_id: str

    version: str = "1.0.0"

    defaults: dict[str, Any] = Field(default_factory=dict)

    fields: dict[str, MappingField] = Field(
        default_factory=dict
    )

    collections: dict[str, CollectionMapping] = Field(
        default_factory=dict
    )
