import json
import re

from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.schemas.application import ApplicationMapping
from app.schemas.recommendation import RecommendationRequest


MAPPINGS_DIRECTORY = (
    Path(__file__).resolve().parent.parent / "mappings"
)


class NormalizationError(Exception):
    """Raised when an application payload cannot be normalised."""


class ApplicationMappingNotFound(Exception):
    """Raised when no mapping exists for an application."""


class NormalizationService:
    """
    Generic application-to-canonical data normalisation engine.

    Application-specific differences are defined through
    external mapping configuration files.
    """

    def __init__(
        self,
        mappings_directory: Path | None = None
    ):
        self.mappings_directory = (
            mappings_directory
            if mappings_directory is not None
            else MAPPINGS_DIRECTORY
        )

    def load_mapping(
        self,
        application_id: str
    ) -> ApplicationMapping:
        """
        Load and validate an application's mapping configuration.
        """

        if not re.fullmatch(
            r"[a-zA-Z0-9_-]+",
            application_id
        ):
            raise ApplicationMappingNotFound(
                "Invalid application identifier."
            )

        config_path = (
            self.mappings_directory
            / f"{application_id}.json"
        )

        if not config_path.exists():
            raise ApplicationMappingNotFound(
                f"No mapping configuration found for "
                f"application '{application_id}'."
            )

        try:
            with config_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                config_data = json.load(file)

            mapping = ApplicationMapping.model_validate(
                config_data
            )

        except FileNotFoundError as exc:
            raise ApplicationMappingNotFound(
                f"No mapping configuration found for "
                f"application '{application_id}'."
            ) from exc

        except json.JSONDecodeError as exc:
            raise NormalizationError(
                f"Invalid JSON in mapping configuration: {exc}"
            ) from exc

        except ValidationError as exc:
            raise NormalizationError(
                f"Invalid mapping configuration: {exc}"
            ) from exc

        if mapping.application_id != application_id:
            raise NormalizationError(
                "Application ID does not match the "
                "mapping configuration."
            )

        return mapping

    @staticmethod
    def get_source_value(
        payload: dict[str, Any],
        source_path: str
    ) -> Any:
        """
        Retrieve a value using dot notation.

        Example:
            customer.profile.id
        """

        current = payload

        for part in source_path.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    @staticmethod
    def set_nested_value(
        target: dict[str, Any],
        target_path: str,
        value: Any
    ) -> None:
        """
        Set a value using dot notation.

        Example:
            user.attributes.preferred_cuisine
        """

        parts = target_path.split(".")
        current = target

        for part in parts[:-1]:

            if part not in current:
                current[part] = {}

            if not isinstance(current[part], dict):
                raise NormalizationError(
                    f"Cannot create nested field "
                    f"'{target_path}'."
                )

            current = current[part]

        current[parts[-1]] = value

    @staticmethod
    def transform_value(
        value: Any,
        transform: str | None
    ) -> Any:
        """
        Apply an optional data transformation.
        """

        if value is None or transform is None:
            return value

        try:

            if transform == "identity":
                return value

            if transform == "lowercase":
                return str(value).lower()

            if transform == "uppercase":
                return str(value).upper()

            if transform == "integer":
                return int(value)

            if transform == "float":
                return float(value)

            if transform == "string":
                return str(value)

            if transform == "boolean":

                if isinstance(value, bool):
                    return value

                if isinstance(value, (int, float)):
                    if value in (0, 1):
                        return bool(value)

                if isinstance(value, str):

                    normalised = value.strip().lower()

                    if normalised in (
                        "true",
                        "1",
                        "yes",
                        "on"
                    ):
                        return True

                    if normalised in (
                        "false",
                        "0",
                        "no",
                        "off"
                    ):
                        return False

                raise ValueError(
                    f"Cannot convert {value!r} to boolean."
                )

            raise NormalizationError(
                f"Unsupported transformation: {transform}"
            )

        except (ValueError, TypeError) as exc:
            raise NormalizationError(
                f"Transformation '{transform}' failed "
                f"for value {value!r}: {exc}"
            ) from exc

    def resolve_field(
        self,
        payload: dict[str, Any],
        field_mapping
    ) -> tuple[bool, Any]:
        """
        Resolve one field using its mapping definition.
        """

        if field_mapping.source is not None:

            value = self.get_source_value(
                payload,
                field_mapping.source
            )

        elif field_mapping.value is not None:

            value = field_mapping.value

        else:

            value = None

        if (
            value is None
            and field_mapping.default is not None
        ):
            value = field_mapping.default

        if value is None:

            if field_mapping.required:
                raise NormalizationError(
                    "Required source field is missing: "
                    f"{field_mapping.source}"
                )

            return False, None

        if field_mapping.value_map:

            lookup_key = str(value)

            if lookup_key in field_mapping.value_map:
                value = field_mapping.value_map[lookup_key]

        value = self.transform_value(
            value,
            field_mapping.transform
        )

        return True, value

    def map_fields(
        self,
        payload: dict[str, Any],
        field_mappings: dict,
        target: dict[str, Any]
    ) -> None:
        """
        Map application fields into canonical fields.
        """

        for (
            target_path,
            field_mapping
        ) in field_mappings.items():

            found, value = self.resolve_field(
                payload,
                field_mapping
            )

            if found:
                self.set_nested_value(
                    target,
                    target_path,
                    value
                )

    def map_collections(
        self,
        payload: dict[str, Any],
        collection_mappings: dict,
        target: dict[str, Any]
    ) -> None:
        """
        Map application collections into
        canonical collections.
        """

        for (
            target_name,
            collection_mapping
        ) in collection_mappings.items():

            records = self.get_source_value(
                payload,
                collection_mapping.source
            )

            if records is None:
                continue

            if not isinstance(records, list):
                raise NormalizationError(
                    f"Collection "
                    f"'{collection_mapping.source}' "
                    "must contain a list."
                )

            normalised_records = []

            for index, record in enumerate(records):

                if not isinstance(record, dict):
                    raise NormalizationError(
                        f"Record {index} in "
                        f"'{collection_mapping.source}' "
                        "must be an object."
                    )

                normalised_record = dict(
                    collection_mapping.defaults
                )

                for (
                    target_field,
                    field_mapping
                ) in collection_mapping.fields.items():

                    found, value = self.resolve_field(
                        record,
                        field_mapping
                    )

                    if found:
                        self.set_nested_value(
                            normalised_record,
                            target_field,
                            value
                        )

                normalised_records.append(
                    normalised_record
                )

            target[target_name] = normalised_records

    def normalize(
        self,
        application_id: str,
        payload: dict[str, Any]
    ) -> RecommendationRequest:
        """
        Convert an application-specific payload into
        the canonical RecommendationRequest model.
        """

        if not isinstance(payload, dict):
            raise NormalizationError(
                "Application payload must be a JSON object."
            )

        mapping = self.load_mapping(
            application_id
        )

        canonical_data: dict[str, Any] = {}

        try:

            # -------------------------------------------------
            # 1. Apply application-level defaults
            # -------------------------------------------------

            for (
                target_path,
                value
            ) in mapping.defaults.items():

                self.set_nested_value(
                    canonical_data,
                    target_path,
                    value
                )

            # -------------------------------------------------
            # 2. Map individual fields
            # -------------------------------------------------

            self.map_fields(
                payload,
                mapping.fields,
                canonical_data
            )

            # -------------------------------------------------
            # 3. Map collections
            # -------------------------------------------------

            self.map_collections(
                payload,
                mapping.collections,
                canonical_data
            )

            # -------------------------------------------------
            # 4. Validate against canonical contract
            # -------------------------------------------------

            return RecommendationRequest.model_validate(
                canonical_data
            )

        except ValidationError as exc:

            raise NormalizationError(
                "Canonical request validation failed: "
                f"{exc}"
            ) from exc


normalization_service = NormalizationService()