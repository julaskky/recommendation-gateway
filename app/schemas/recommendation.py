
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class CanonicalModel(BaseModel):
    """
    Base model shared by all canonical data structures.
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class InteractionType(str, Enum):
    IMPRESSION = "impression"
    VIEW = "view"
    CLICK = "click"
    LIKE = "like"
    FAVORITE = "favorite"
    CART = "cart"
    PURCHASE = "purchase"
    RATING = "rating"
    SHARE = "share"
    DISMISS = "dismiss"
    CUSTOM = "custom"


class User(CanonicalModel):
    """
    Standard representation of a recommendation consumer.
    """

    user_id: str = Field(
        min_length=1,
        description="Unique identifier of the user."
    )

    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Domain-specific user attributes."
    )

    segments: list[str] = Field(
        default_factory=list,
        description="User groups or segments."
    )


class Item(CanonicalModel):
    """
    Standard representation of a recommendable entity.

    An item could be a product, restaurant, course,
    movie, article, service, or another entity.
    """

    item_id: str = Field(
        min_length=1,
        description="Unique identifier of the item."
    )

    item_type: str = Field(
        min_length=1,
        description="Category or type of recommendable entity."
    )

    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Domain-specific item attributes."
    )


class Interaction(CanonicalModel):
    """
    Standard representation of user-item interactions.
    """

    event_type: InteractionType

    item_id: str | None = None

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    value: float | None = None

    attributes: dict[str, Any] = Field(
        default_factory=dict
    )


class Context(CanonicalModel):
    """
    Represents the circumstances surrounding a request.
    """

    domain: str = Field(
        min_length=1,
        description="Application domain, e.g. food, education or retail."
    )

    application_id: str | None = None

    session_id: str | None = None

    locale: str | None = None

    timezone: str | None = None

    device_type: str | None = None

    location: dict[str, Any] | None = None

    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional contextual information."
    )


class Constraints(CanonicalModel):
    """
    Optional restrictions on recommendation results.
    """

    exclude_item_ids: list[str] = Field(
        default_factory=list
    )

    include_item_ids: list[str] | None = None

    filters: dict[str, Any] = Field(
        default_factory=dict,
        description="Domain-specific filtering conditions."
    )

    min_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0
    )

    max_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0
    )

    @model_validator(mode="after")
    def validate_score_range(self):
        if (
            self.min_score is not None
            and self.max_score is not None
            and self.min_score > self.max_score
        ):
            raise ValueError(
                "min_score cannot exceed max_score."
            )

        return self


class RecommendationRequest(CanonicalModel):
    """
    Standard input contract for all applications.
    """

    request_id: UUID = Field(
        default_factory=uuid4
    )

    user: User

    context: Context

    interaction_history: list[Interaction] = Field(
        default_factory=list
    )

    candidate_items: list[Item] | None = None

    constraints: Constraints = Field(
        default_factory=Constraints
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=100
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class Recommendation(CanonicalModel):
    """
    One recommendation returned by a recommendation engine.
    """

    item: Item

    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Normalised recommendation relevance score."
    )

    rank: int = Field(
        ge=1
    )

    reason: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class RecommendationResponse(CanonicalModel):
    """
    Standard output contract returned to applications.
    """

    request_id: UUID

    recommendations: list[Recommendation] = Field(
        default_factory=list
    )

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )
