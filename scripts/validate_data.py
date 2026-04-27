#!/usr/bin/env python3
"""Validate static Xi'an carbohydrates guide data."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STORE_DATA_PATH = ROOT / "data" / "stores.json"
KNOWLEDGE_DATA_PATH = ROOT / "data" / "knowledge.json"
TAXONOMY_DATA_PATH = ROOT / "data" / "taxonomy.json"
REQUIRED_FIELDS = [
    "store_id",
    "brand_name",
    "branch_name",
    "district",
    "area",
    "address",
    "primary_category_id",
    "dish_types",
    "food_tags",
]
ENUM_FIELDS = {
    "takeout_supported": {"yes", "no", "unknown"},
    "delivery_supported": {"yes", "no", "unknown"},
    "wifi_policy": {"public", "ask_staff", "none", "unknown"},
    "confidence": {"high", "medium", "low", "unknown"},
}
KNOWLEDGE_ENUM_FIELDS = {
    "intent_type": {"history", "craft", "taste", "etiquette"},
    "confidence": {"high", "medium", "low", "unknown"},
}
TIME_VALUE_RE = re.compile(
    r"^(unknown|closed|([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)(;([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d))*)$"
)
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def load_data(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"{path.name} must contain a JSON array")
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"{path.name}[{index}] must be an object")
    return raw


def load_taxonomy_ids() -> set[str]:
    taxonomy = load_data(TAXONOMY_DATA_PATH)
    taxonomy_ids: set[str] = set()
    for item in taxonomy:
        category_id = str(item.get("category_id", "")).strip()
        if category_id:
            taxonomy_ids.add(category_id)
    return taxonomy_ids


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def validate_store(store: dict[str, Any], seen_ids: set[str], taxonomy_ids: set[str]) -> list[str]:
    errors: list[str] = []
    store_id = str(store.get("store_id", "")).strip()
    label = store_id or "<missing-store-id>"

    for field in REQUIRED_FIELDS:
        value = store.get(field)
        if value is None:
            errors.append(f"{label}: missing required field `{field}`")
            continue
        if isinstance(value, str) and not value.strip():
            errors.append(f"{label}: empty required field `{field}`")
        if isinstance(value, list) and not value:
            errors.append(f"{label}: empty required list `{field}`")

    if store_id:
        if store_id in seen_ids:
            errors.append(f"{label}: duplicate store_id")
        seen_ids.add(store_id)

    for field, allowed in ENUM_FIELDS.items():
        value = store.get(field)
        if value is None or value == "":
            continue
        normalized = str(value).strip().lower()
        if normalized not in allowed:
            errors.append(
                f"{label}: invalid `{field}` value `{value}`; allowed: {sorted(allowed)}"
            )

    for coord_field in ("lat", "lng"):
        value = store.get(coord_field)
        if value is None or value == "":
            continue
        if not isinstance(value, (int, float)):
            errors.append(f"{label}: `{coord_field}` must be numeric")

    if "priority_score" in store and store.get("priority_score") not in (None, ""):
        if not isinstance(store["priority_score"], int):
            errors.append(f"{label}: `priority_score` must be an integer")

    food_tags = as_list(store.get("food_tags"))
    if food_tags and not all(str(item).strip() for item in food_tags):
        errors.append(f"{label}: `food_tags` contains empty value")

    signature_dishes = as_list(store.get("signature_dishes"))
    if signature_dishes and not all(str(item).strip() for item in signature_dishes):
        errors.append(f"{label}: `signature_dishes` contains empty value")

    dish_types = as_list(store.get("dish_types"))
    if dish_types and not all(str(item).strip() for item in dish_types):
        errors.append(f"{label}: `dish_types` contains empty value")

    for list_field in ("secondary_category_ids", "search_keywords_zh", "search_keywords_en"):
        values = as_list(store.get(list_field))
        if values and not all(str(value).strip() for value in values):
            errors.append(f"{label}: `{list_field}` contains empty value")

    primary_category_id = str(store.get("primary_category_id", "")).strip()
    if primary_category_id and primary_category_id not in taxonomy_ids:
        errors.append(f"{label}: unknown `primary_category_id` `{primary_category_id}`")

    for category_id in as_list(store.get("secondary_category_ids")):
        current = str(category_id).strip()
        if current and current not in taxonomy_ids:
            errors.append(f"{label}: unknown secondary category `{current}`")

    hours = store.get("hours")
    if hours is not None:
        if not isinstance(hours, dict):
            errors.append(f"{label}: `hours` must be an object")
        else:
            for day in DAYS:
                value = str(hours.get(day, "unknown")).strip().lower()
                if not TIME_VALUE_RE.match(value):
                    errors.append(
                        f"{label}: invalid hours for `{day}` -> `{hours.get(day)}`"
                    )

    return errors


def validate_knowledge(
    item: dict[str, Any], seen_ids: set[str], taxonomy_ids: set[str]
) -> list[str]:
    errors: list[str] = []
    entry_id = str(item.get("entry_id", "")).strip()
    label = entry_id or "<missing-entry-id>"

    required_fields = [
        "entry_id",
        "topic_slug",
        "intent_type",
        "category_id",
        "dish_types",
        "question_zh",
        "answer_zh",
    ]
    for field in required_fields:
        value = item.get(field)
        if value is None:
            errors.append(f"{label}: missing required field `{field}`")
            continue
        if isinstance(value, str) and not value.strip():
            errors.append(f"{label}: empty required field `{field}`")
        if isinstance(value, list) and not value:
            errors.append(f"{label}: empty required list `{field}`")

    if entry_id:
        if entry_id in seen_ids:
            errors.append(f"{label}: duplicate entry_id")
        seen_ids.add(entry_id)

    for field, allowed in KNOWLEDGE_ENUM_FIELDS.items():
        value = item.get(field)
        if value is None or value == "":
            continue
        normalized = str(value).strip().lower()
        if normalized not in allowed:
            errors.append(
                f"{label}: invalid `{field}` value `{value}`; allowed: {sorted(allowed)}"
            )

    for list_field in ("dish_types", "dish_types_en", "keywords_zh", "keywords_en"):
        values = as_list(item.get(list_field))
        if values and not all(str(value).strip() for value in values):
            errors.append(f"{label}: `{list_field}` contains empty value")

    category_id = str(item.get("category_id", "")).strip()
    if category_id and category_id not in taxonomy_ids:
        errors.append(f"{label}: unknown `category_id` `{category_id}`")

    if "priority_score" in item and item.get("priority_score") not in (None, ""):
        if not isinstance(item["priority_score"], int):
            errors.append(f"{label}: `priority_score` must be an integer")

    return errors


def main() -> int:
    missing = [
        path for path in (STORE_DATA_PATH, KNOWLEDGE_DATA_PATH, TAXONOMY_DATA_PATH) if not path.exists()
    ]
    if missing:
        print(f"Missing data file: {missing[0]}")
        return 1

    try:
        taxonomy_ids = load_taxonomy_ids()
        stores = load_data(STORE_DATA_PATH)
        knowledge = load_data(KNOWLEDGE_DATA_PATH)
    except Exception as exc:
        print(f"Failed to load data: {exc}")
        return 1

    seen_store_ids: set[str] = set()
    seen_knowledge_ids: set[str] = set()
    errors: list[str] = []
    for store in stores:
        errors.extend(validate_store(store, seen_store_ids, taxonomy_ids))
    for item in knowledge:
        errors.extend(validate_knowledge(item, seen_knowledge_ids, taxonomy_ids))

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validation passed: {len(stores)} store(s), {len(knowledge)} knowledge item(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
