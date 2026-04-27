#!/usr/bin/env python3
"""Query static Xi'an carbohydrates guide data."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STORE_DATA_PATH = ROOT / "data" / "stores.json"
KNOWLEDGE_DATA_PATH = ROOT / "data" / "knowledge.json"
TAXONOMY_DATA_PATH = ROOT / "data" / "taxonomy.json"
COMMUNITY_SUBMISSIONS_PATH = ROOT / "data" / "community_submissions.json"
COMMUNITY_COMMENTS_PATH = ROOT / "data" / "community_comments.json"
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_LABELS = {
    "mon": "周一",
    "tue": "周二",
    "wed": "周三",
    "thu": "周四",
    "fri": "周五",
    "sat": "周六",
    "sun": "周日",
}
YES_VALUES = {"yes", "true", "1", "y"}
TIME_RANGE_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)$")


def load_json_array(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"{path} must contain a JSON array")
    return [item for item in raw if isinstance(item, dict)]


def load_stores() -> list[dict[str, Any]]:
    return load_json_array(STORE_DATA_PATH)


def load_knowledge() -> list[dict[str, Any]]:
    return load_json_array(KNOWLEDGE_DATA_PATH)


def load_community_submissions() -> list[dict[str, Any]]:
    return load_json_array(COMMUNITY_SUBMISSIONS_PATH)


def load_community_comments() -> list[dict[str, Any]]:
    return load_json_array(COMMUNITY_COMMENTS_PATH)


@lru_cache(maxsize=1)
def load_taxonomy() -> tuple[dict[str, Any], ...]:
    return tuple(load_json_array(TAXONOMY_DATA_PATH))


def save_json_array(path: Path, items: list[dict[str, Any]]) -> None:
    path.write_text(
        json.dumps(items, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize(text: Any) -> str:
    if text is None:
        return ""
    text = str(text).strip().lower()
    return re.sub(r"[\s,，、/|;；:：()（）【】\[\]\-]+", "", text)


def ensure_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        parts = re.split(r"[,，、/|;；]+", value)
        return [part.strip() for part in parts if part.strip()]
    return [str(value).strip()]


def current_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def build_local_id(prefix: str, items: list[dict[str, Any]]) -> str:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{stamp}_{len(items) + 1:03d}"


def default_author_name(lang: str) -> str:
    return "Anonymous User" if lang == "en" else "匿名用户"


@lru_cache(maxsize=1)
def taxonomy_by_id() -> dict[str, dict[str, Any]]:
    return {str(item.get("category_id", "")).strip(): dict(item) for item in load_taxonomy()}


@lru_cache(maxsize=1)
def taxonomy_indexes() -> dict[str, dict[str, set[str]]]:
    category_aliases: dict[str, set[str]] = {}
    dish_aliases: dict[str, set[str]] = {}

    for item in load_taxonomy():
        category_id = str(item.get("category_id", "")).strip()
        if not category_id:
            continue
        category_terms = [
            category_id,
            item.get("name_zh", ""),
            item.get("name_en", ""),
            *ensure_list(item.get("query_keywords_zh")),
            *ensure_list(item.get("query_keywords_en")),
        ]
        for term in category_terms:
            normalized = normalize(term)
            if normalized:
                category_aliases.setdefault(normalized, set()).add(category_id)

        dishes_zh = ensure_list(item.get("dishes_zh"))
        dishes_en = ensure_list(item.get("dishes_en"))
        for index, dish_zh in enumerate(dishes_zh):
            aliases = [dish_zh]
            if index < len(dishes_en):
                aliases.append(dishes_en[index])
            for alias in aliases:
                normalized = normalize(alias)
                if normalized:
                    dish_aliases.setdefault(normalized, set()).add(dish_zh)

    return {"category_aliases": category_aliases, "dish_aliases": dish_aliases}


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return normalize(value) in YES_VALUES


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lng2 - lng1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    )
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_day_ranges(value: Any) -> list[tuple[int, int]]:
    text = str(value or "").strip().lower()
    if not text or text == "unknown" or text == "closed":
        return []
    ranges: list[tuple[int, int]] = []
    for part in text.split(";"):
        part = part.strip()
        match = TIME_RANGE_RE.match(part)
        if not match:
            continue
        start_h, start_m, end_h, end_m = map(int, match.groups())
        start = start_h * 60 + start_m
        end = end_h * 60 + end_m
        ranges.append((start, end))
    return ranges


def time_in_range(current_minutes: int, start: int, end: int) -> bool:
    if start <= end:
        return start <= current_minutes <= end
    return current_minutes >= start or current_minutes <= end


def previous_day_key(now: datetime) -> str:
    return DAYS[(now.weekday() - 1) % 7]


def is_open_now(store: dict[str, Any], now: datetime | None = None) -> bool:
    now = now or datetime.now()
    day_key = DAYS[now.weekday()]
    schedule = store.get("hours", {})
    if not isinstance(schedule, dict):
        return False
    current_minutes = now.hour * 60 + now.minute

    day_value = schedule.get(day_key)
    ranges = parse_day_ranges(day_value)
    for start, end in ranges:
        if time_in_range(current_minutes, start, end):
            return True

    prev_day = previous_day_key(now)
    prev_value = schedule.get(prev_day)
    prev_ranges = parse_day_ranges(prev_value)
    for start, end in prev_ranges:
        if start > end and current_minutes <= end:
            return True

    return False


def active_hours_text(store: dict[str, Any], now: datetime | None = None) -> str:
    now = now or datetime.now()
    day_key = DAYS[now.weekday()]
    schedule = store.get("hours", {})
    if not isinstance(schedule, dict):
        return "unknown"
    current_minutes = now.hour * 60 + now.minute
    current_value = str(schedule.get(day_key, "unknown"))
    current_ranges = parse_day_ranges(current_value)
    for start, end in current_ranges:
        if time_in_range(current_minutes, start, end):
            return current_value

    prev_day = previous_day_key(now)
    prev_value = str(schedule.get(prev_day, "unknown"))
    prev_ranges = parse_day_ranges(prev_value)
    for start, end in prev_ranges:
        if start > end and current_minutes <= end:
            return f"{DAY_LABELS[prev_day]}延续 {prev_value}"

    return current_value


def today_hours(store: dict[str, Any], now: datetime | None = None) -> str:
    return active_hours_text(store, now=now)


def display_name(store: dict[str, Any]) -> str:
    brand = str(store.get("brand_name", "")).strip()
    branch = str(store.get("branch_name", "")).strip()
    if brand and branch:
        return f"{brand} {branch}"
    return brand or branch or str(store.get("store_id", "")).strip()


def collect_search_blob(store: dict[str, Any]) -> str:
    fields: list[str] = [
        store.get("brand_name", ""),
        store.get("brand_name_en", ""),
        store.get("branch_name", ""),
        store.get("branch_name_en", ""),
        store.get("district", ""),
        store.get("district_en", ""),
        store.get("area", ""),
        store.get("area_en", ""),
        store.get("address", ""),
        store.get("address_en", ""),
        store.get("recommended_reason", ""),
        store.get("recommended_reason_en", ""),
        store.get("queue_notes", ""),
        store.get("queue_notes_en", ""),
        store.get("notes", ""),
        store.get("notes_en", ""),
        store.get("primary_category_id", ""),
    ]
    for key in (
        "secondary_category_ids",
        "aliases",
        "aliases_en",
        "landmarks",
        "landmarks_en",
        "dish_types",
        "dish_types_en",
        "search_keywords_zh",
        "search_keywords_en",
        "food_tags",
        "food_tags_en",
        "signature_dishes",
        "signature_dishes_en",
    ):
        fields.extend(ensure_list(store.get(key)))
    return normalize(" ".join(str(field) for field in fields))


def bool_label(value: Any) -> str:
    raw = normalize(value)
    if raw in {"yes", "true", "1", "y"}:
        return "yes"
    if raw in {"no", "false", "0", "n"}:
        return "no"
    return "unknown"


def localized_value(item: dict[str, Any], key: str, lang: str) -> Any:
    if lang == "en":
        en_key = f"{key}_en"
        en_value = item.get(en_key)
        if isinstance(en_value, str) and en_value.strip():
            return en_value
        if isinstance(en_value, list) and en_value:
            return en_value
    return item.get(key)


def localized_knowledge_value(item: dict[str, Any], key: str, lang: str) -> Any:
    if lang == "en":
        value = item.get(f"{key}_en")
        if isinstance(value, str) and value.strip():
            return value
        if isinstance(value, list) and value:
            return value
    value = item.get(f"{key}_zh")
    if isinstance(value, str) and value.strip():
        return value
    if isinstance(value, list) and value:
        return value
    return item.get(key)


def localized_submission_value(item: dict[str, Any], key: str, lang: str) -> Any:
    if lang == "en":
        value = item.get(f"{key}_en")
        if isinstance(value, str) and value.strip():
            return value
    value = item.get(f"{key}_zh")
    if isinstance(value, str) and value.strip():
        return value
    return item.get(key)


def localized_display_name(store: dict[str, Any], lang: str) -> str:
    if lang == "en":
        brand = str(store.get("brand_name_en", "")).strip()
        branch = str(store.get("branch_name_en", "")).strip()
        if brand and branch:
            return f"{brand} {branch}"
        if brand:
            return brand
    return display_name(store)


def submission_display_name(item: dict[str, Any]) -> str:
    brand = str(item.get("brand_name", "")).strip()
    branch = str(item.get("branch_name", "")).strip()
    if brand and branch:
        return f"{brand} {branch}"
    return brand or branch or str(item.get("submission_id", "")).strip()


def localized_category_name(category_id: Any, lang: str) -> str:
    category = taxonomy_by_id().get(str(category_id or "").strip())
    if not category:
        return str(category_id or "")
    if lang == "en":
        return str(category.get("name_en") or category.get("name_zh") or category_id)
    return str(category.get("name_zh") or category.get("name_en") or category_id)


def resolve_category_ids(values: list[str]) -> list[str]:
    if not values:
        return []
    aliases = taxonomy_indexes()["category_aliases"]
    resolved: set[str] = set()
    for value in values:
        normalized = normalize(value)
        if normalized in aliases:
            resolved.update(aliases[normalized])
    return sorted(resolved)


def detect_taxonomy_terms(text: str) -> tuple[list[str], list[str]]:
    normalized_query = normalize(text)
    if not normalized_query:
        return [], []

    category_ids: set[str] = set()
    dishes: set[str] = set()
    indexes = taxonomy_indexes()

    for alias, ids in indexes["category_aliases"].items():
        if alias and alias in normalized_query:
            category_ids.update(ids)

    for alias, canonical_dishes in indexes["dish_aliases"].items():
        if alias and alias in normalized_query:
            dishes.update(canonical_dishes)

    return sorted(category_ids), sorted(dishes)


def store_category_ids(store: dict[str, Any]) -> set[str]:
    category_ids = {str(store.get("primary_category_id", "")).strip()}
    category_ids.update(str(item).strip() for item in ensure_list(store.get("secondary_category_ids")))
    return {item for item in category_ids if item}


def store_dish_names(store: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for key in ("dish_types", "dish_types_en", "signature_dishes", "signature_dishes_en"):
        names.update(normalize(item) for item in ensure_list(store.get(key)) if normalize(item))
    return names


def knowledge_dish_names(item: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for key in ("dish_types", "dish_types_en"):
        names.update(normalize(value) for value in ensure_list(item.get(key)) if normalize(value))
    return names


def normalized_values(*values: Any) -> set[str]:
    normalized: set[str] = set()
    for value in values:
        if isinstance(value, list):
            for item in value:
                current = normalize(item)
                if current:
                    normalized.add(current)
        else:
            current = normalize(value)
            if current:
                normalized.add(current)
    return normalized


def wifi_match(store: dict[str, Any]) -> bool:
    policy = normalize(store.get("wifi_policy"))
    return policy in {"public", "askstaff", "ask_staff"}


def enrich_store(
    store: dict[str, Any],
    now: datetime | None = None,
    near_lat: float | None = None,
    near_lng: float | None = None,
    lang: str = "zh",
) -> dict[str, Any]:
    enriched = dict(store)
    enriched["display_name"] = display_name(store)
    enriched["display_name_localized"] = localized_display_name(store, lang)
    enriched["primary_category_name_localized"] = localized_category_name(
        store.get("primary_category_id"), lang
    )
    enriched["secondary_category_names_localized"] = [
        localized_category_name(item, lang) for item in ensure_list(store.get("secondary_category_ids"))
    ]
    enriched["district_localized"] = localized_value(store, "district", lang)
    enriched["area_localized"] = localized_value(store, "area", lang)
    enriched["address_localized"] = localized_value(store, "address", lang)
    enriched["dish_types_localized"] = ensure_list(localized_value(store, "dish_types", lang))
    enriched["food_tags_localized"] = ensure_list(localized_value(store, "food_tags", lang))
    enriched["signature_dishes_localized"] = ensure_list(
        localized_value(store, "signature_dishes", lang)
    )
    enriched["recommended_reason_localized"] = str(
        localized_value(store, "recommended_reason", lang) or ""
    )
    enriched["queue_notes_localized"] = str(localized_value(store, "queue_notes", lang) or "")
    enriched["notes_localized"] = str(localized_value(store, "notes", lang) or "")
    enriched["today_hours"] = today_hours(store, now=now)
    enriched["open_now"] = is_open_now(store, now=now)
    if near_lat is not None and near_lng is not None:
        lat = store.get("lat")
        lng = store.get("lng")
        if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
            enriched["distance_km"] = round(haversine_km(near_lat, near_lng, lat, lng), 2)
        else:
            enriched["distance_km"] = None
    return enriched


def search_stores(args: argparse.Namespace) -> dict[str, Any]:
    stores = load_stores()
    now = datetime.fromisoformat(args.at) if args.at else datetime.now()
    query_blob = normalize(args.query)
    tag_filters = [normalize(item) for item in args.tag]
    dish_filters = [normalize(item) for item in args.dish]
    explicit_category_ids = resolve_category_ids(args.category)
    inferred_category_ids, inferred_dishes = detect_taxonomy_terms(args.query)
    effective_category_ids = sorted(set(explicit_category_ids) | set(inferred_category_ids))
    near_lat = args.near_lat
    near_lng = args.near_lng
    results: list[dict[str, Any]] = []

    for store in stores:
        score = int(store.get("priority_score", 0) or 0)
        searchable = collect_search_blob(store)
        category_ids = store_category_ids(store)
        dish_names = store_dish_names(store)
        raw_query_match = False

        if query_blob:
            raw_query_match = query_blob in searchable
            if not raw_query_match and not effective_category_ids and not inferred_dishes:
                continue
            if raw_query_match:
                score += 10

        if effective_category_ids:
            matched_categories = category_ids.intersection(effective_category_ids)
            if not matched_categories:
                continue
            score += 4 * len(matched_categories)

        if inferred_dishes:
            matched_inferred_dishes = dish_names.intersection(
                {normalize(item) for item in inferred_dishes}
            )
            if matched_inferred_dishes:
                score += 3 * len(matched_inferred_dishes)
            elif not raw_query_match:
                continue

        if args.district:
            district_query = normalize(args.district)
            district_values = normalized_values(store.get("district"), store.get("district_en"))
            if district_query not in district_values:
                continue
            score += 4

        if args.area:
            area_query = normalize(args.area)
            area_values = normalized_values(
                store.get("area"),
                store.get("area_en"),
                ensure_list(store.get("landmarks")),
                ensure_list(store.get("landmarks_en")),
            )
            if area_query not in area_values:
                continue
            score += 4

        if args.landmark:
            landmark_query = normalize(args.landmark)
            landmark_values = normalized_values(
                ensure_list(store.get("landmarks")),
                ensure_list(store.get("landmarks_en")),
                store.get("address"),
                store.get("address_en"),
            )
            if landmark_query not in landmark_values:
                continue
            score += 4

        tags = [normalize(item) for item in ensure_list(store.get("food_tags"))]
        if tag_filters:
            if not all(tag in tags for tag in tag_filters):
                continue
            score += 3 * len(tag_filters)

        if dish_filters:
            if not all(dish in dish_names for dish in dish_filters):
                continue
            score += 2 * len(dish_filters)

        if args.delivery and bool_label(store.get("delivery_supported")) != "yes":
            continue
        if args.wifi and not wifi_match(store):
            continue
        if args.open_now and not is_open_now(store, now=now):
            continue

        enriched = enrich_store(
            store, now=now, near_lat=near_lat, near_lng=near_lng, lang=args.lang
        )
        if args.radius_km is not None:
            distance = enriched.get("distance_km")
            if distance is None or distance > args.radius_km:
                continue

        enriched["_score"] = score
        results.append(enriched)

    def sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
        distance = item.get("distance_km")
        distance_sort = distance if isinstance(distance, (int, float)) else 999999
        return (-item.get("_score", 0), distance_sort, item.get("display_name", ""))

    results.sort(key=sort_key)
    limited = results[: args.limit]
    for item in limited:
        item.pop("_score", None)

    return {
        "query": {
            "query": args.query,
            "district": args.district,
            "area": args.area,
            "landmark": args.landmark,
            "category": args.category,
            "tag": args.tag,
            "dish": args.dish,
            "detected_category_ids": effective_category_ids,
            "detected_dish_types": inferred_dishes,
            "open_now": args.open_now,
            "delivery": args.delivery,
            "wifi": args.wifi,
            "near_lat": args.near_lat,
            "near_lng": args.near_lng,
            "radius_km": args.radius_km,
            "evaluated_at": now.isoformat(timespec="minutes"),
        },
        "count": len(limited),
        "total_matches": len(results),
        "results": limited,
    }


def detail_store(args: argparse.Namespace) -> dict[str, Any]:
    stores = load_stores()
    now = datetime.fromisoformat(args.at) if args.at else datetime.now()
    for store in stores:
        if str(store.get("store_id")) == args.store_id:
            payload = enrich_store(
                store,
                now=now,
                near_lat=args.near_lat,
                near_lng=args.near_lng,
                lang=args.lang,
            )
            if getattr(args, "include_comments", False):
                comment_items = [
                    enrich_comment(item, args.lang)
                    for item in load_community_comments()
                    if str(item.get("target_type", "")).strip() == "store"
                    and str(item.get("target_id", "")).strip() == args.store_id
                    and str(item.get("status", "")).strip() == "visible"
                ]
                comment_items.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
                payload["community_comments"] = comment_items[: args.comments_limit]
                payload["community_comments_count"] = len(comment_items)
            return payload
    return {"error": f"store_id not found: {args.store_id}"}


def enrich_knowledge(item: dict[str, Any], lang: str) -> dict[str, Any]:
    enriched = dict(item)
    enriched["category_name_localized"] = localized_category_name(item.get("category_id"), lang)
    enriched["question_localized"] = str(localized_knowledge_value(item, "question", lang) or "")
    enriched["answer_localized"] = str(localized_knowledge_value(item, "answer", lang) or "")
    enriched["dish_types_localized"] = ensure_list(
        localized_knowledge_value(item, "dish_types", lang)
    )
    enriched["keywords_localized"] = ensure_list(
        localized_knowledge_value(item, "keywords", lang)
    )
    return enriched


def enrich_submission(item: dict[str, Any], lang: str) -> dict[str, Any]:
    enriched = dict(item)
    enriched["display_name"] = submission_display_name(item)
    enriched["display_name_localized"] = submission_display_name(item)
    enriched["category_name_localized"] = localized_category_name(
        item.get("primary_category_id"), lang
    )
    if lang == "en" and ensure_list(item.get("dish_types_en")):
        enriched["dish_types_localized"] = ensure_list(item.get("dish_types_en"))
    else:
        enriched["dish_types_localized"] = ensure_list(item.get("dish_types"))
    enriched["recommended_reason_localized"] = str(
        localized_submission_value(item, "recommended_reason", lang) or ""
    )
    enriched["submitter_note_localized"] = str(
        localized_submission_value(item, "submitter_note", lang) or ""
    )
    return enriched


def resolve_comment_target(item: dict[str, Any], lang: str) -> str:
    target_type = str(item.get("target_type", "")).strip()
    target_id = str(item.get("target_id", "")).strip()
    if target_type == "store":
        for store in load_stores():
            if str(store.get("store_id", "")).strip() == target_id:
                return localized_display_name(store, lang)
    if target_type == "submission":
        for submission in load_community_submissions():
            if str(submission.get("submission_id", "")).strip() == target_id:
                return submission_display_name(submission)
    return target_id


def enrich_comment(item: dict[str, Any], lang: str) -> dict[str, Any]:
    enriched = dict(item)
    if lang == "en" and str(item.get("comment_en", "")).strip():
        enriched["comment_localized"] = str(item.get("comment_en", "")).strip()
    else:
        enriched["comment_localized"] = str(item.get("comment_zh", "")).strip()
    enriched["target_name_localized"] = resolve_comment_target(item, lang)
    return enriched


def collect_knowledge_blob(item: dict[str, Any]) -> str:
    fields: list[str] = [
        item.get("entry_id", ""),
        item.get("topic_slug", ""),
        item.get("intent_type", ""),
        item.get("category_id", ""),
        item.get("question_zh", ""),
        item.get("question_en", ""),
        item.get("answer_zh", ""),
        item.get("answer_en", ""),
        item.get("notes", ""),
    ]
    for key in ("dish_types", "dish_types_en", "keywords_zh", "keywords_en"):
        fields.extend(ensure_list(item.get(key)))
    return normalize(" ".join(str(field) for field in fields))


def search_knowledge(args: argparse.Namespace) -> dict[str, Any]:
    items = load_knowledge()
    query_blob = normalize(args.query)
    intent_type = normalize(args.intent_type)
    explicit_category_ids = resolve_category_ids(args.category)
    inferred_category_ids, inferred_dishes = detect_taxonomy_terms(args.query)
    effective_category_ids = sorted(set(explicit_category_ids) | set(inferred_category_ids))
    results: list[dict[str, Any]] = []

    for item in items:
        score = int(item.get("priority_score", 0) or 0)
        searchable = collect_knowledge_blob(item)
        dish_names = knowledge_dish_names(item)
        raw_query_match = False

        if query_blob:
            raw_query_match = query_blob in searchable
            if not raw_query_match and not effective_category_ids and not inferred_dishes:
                continue
            if raw_query_match:
                score += 10

        if effective_category_ids:
            if str(item.get("category_id", "")).strip() not in effective_category_ids:
                continue
            score += 4

        if inferred_dishes:
            matched_inferred_dishes = dish_names.intersection(
                {normalize(value) for value in inferred_dishes}
            )
            if matched_inferred_dishes:
                score += 3 * len(matched_inferred_dishes)
            elif not raw_query_match:
                continue

        if intent_type:
            current_type = normalize(item.get("intent_type"))
            if current_type != intent_type:
                continue
            score += 3

        for dish in args.dish:
            dish_query = normalize(dish)
            if dish_query not in dish_names:
                break
            score += 2
        else:
            enriched = enrich_knowledge(item, args.lang)
            enriched["_score"] = score
            results.append(enriched)

    results.sort(key=lambda item: (-item.get("_score", 0), item.get("entry_id", "")))
    limited = results[: args.limit]
    for item in limited:
        item.pop("_score", None)

    return {
        "query": {
            "query": args.query,
            "intent_type": args.intent_type,
            "category": args.category,
            "dish": args.dish,
            "detected_category_ids": effective_category_ids,
            "detected_dish_types": inferred_dishes,
            "lang": args.lang,
        },
        "count": len(limited),
        "total_matches": len(results),
        "results": limited,
    }


def detail_knowledge(args: argparse.Namespace) -> dict[str, Any]:
    items = load_knowledge()
    for item in items:
        if str(item.get("entry_id")) == args.entry_id:
            return enrich_knowledge(item, args.lang)
    return {"error": f"entry_id not found: {args.entry_id}"}


def resolve_single_category_id(value: str) -> str:
    category_ids = resolve_category_ids([value])
    if not category_ids:
        raise ValueError(f"unknown category: {value}")
    if len(category_ids) > 1:
        raise ValueError(f"ambiguous category: {value}")
    return category_ids[0]


def target_identity_from_args(args: argparse.Namespace) -> tuple[str, str]:
    store_id = str(getattr(args, "store_id", "") or "").strip()
    submission_id = str(getattr(args, "submission_id", "") or "").strip()
    if bool(store_id) == bool(submission_id):
        raise ValueError("provide exactly one of --store-id or --submission-id")
    if store_id:
        if not any(str(item.get("store_id", "")).strip() == store_id for item in load_stores()):
            raise ValueError(f"store_id not found: {store_id}")
        return "store", store_id
    if not any(
        str(item.get("submission_id", "")).strip() == submission_id
        for item in load_community_submissions()
    ):
        raise ValueError(f"submission_id not found: {submission_id}")
    return "submission", submission_id


def collect_submission_blob(item: dict[str, Any]) -> str:
    fields: list[str] = [
        item.get("submission_id", ""),
        item.get("status", ""),
        item.get("brand_name", ""),
        item.get("branch_name", ""),
        item.get("district", ""),
        item.get("area", ""),
        item.get("address", ""),
        item.get("primary_category_id", ""),
        item.get("recommended_reason_zh", ""),
        item.get("recommended_reason_en", ""),
        item.get("submitter_name", ""),
        item.get("submitter_note_zh", ""),
        item.get("submitter_note_en", ""),
    ]
    for key in ("dish_types", "dish_types_en"):
        fields.extend(ensure_list(item.get(key)))
    return normalize(" ".join(str(field) for field in fields))


def suggest_store(args: argparse.Namespace) -> dict[str, Any]:
    if not any([args.reason_zh, args.reason_en, args.note_zh, args.note_en]):
        raise ValueError("at least one of reason or note is required")
    category_id = resolve_single_category_id(args.category)
    items = load_community_submissions()
    created_at = current_timestamp()
    submitter_name = args.submitter_name.strip() or default_author_name(args.lang)
    submission = {
        "submission_id": build_local_id("submission", items),
        "status": "pending",
        "brand_name": args.brand_name.strip(),
        "branch_name": args.branch_name.strip(),
        "district": args.district.strip(),
        "area": args.area.strip(),
        "address": args.address.strip(),
        "primary_category_id": category_id,
        "dish_types": ensure_list(args.dish),
        "dish_types_en": ensure_list(args.dish_en),
        "recommended_reason_zh": args.reason_zh.strip(),
        "recommended_reason_en": args.reason_en.strip(),
        "submitter_name": submitter_name,
        "submitter_note_zh": args.note_zh.strip(),
        "submitter_note_en": args.note_en.strip(),
        "source_url": args.source_url.strip(),
        "created_at": created_at,
        "updated_at": created_at,
        "scope": "local_installation",
    }
    items.append(submission)
    save_json_array(COMMUNITY_SUBMISSIONS_PATH, items)
    payload = enrich_submission(submission, args.lang)
    payload["message"] = (
        "已记录这条用户推荐，当前状态为 pending。注意：这条提交只保存在当前安装副本里。"
        if args.lang == "zh"
        else "Saved this community suggestion with pending status. Note: it is stored only in this local installation."
    )
    return payload


def list_suggestions(args: argparse.Namespace) -> dict[str, Any]:
    items = load_community_submissions()
    query_blob = normalize(args.query)
    explicit_category_ids = resolve_category_ids(args.category)
    results: list[dict[str, Any]] = []

    for item in items:
        score = 0
        searchable = collect_submission_blob(item)
        if query_blob:
            if query_blob not in searchable:
                continue
            score += 10
        if args.status:
            if normalize(item.get("status")) != normalize(args.status):
                continue
            score += 2
        if explicit_category_ids:
            if str(item.get("primary_category_id", "")).strip() not in explicit_category_ids:
                continue
            score += 4
        if args.district:
            district_values = normalized_values(item.get("district"))
            if normalize(args.district) not in district_values:
                continue
            score += 3
        if args.area:
            area_values = normalized_values(item.get("area"), item.get("address"))
            if normalize(args.area) not in area_values:
                continue
            score += 3
        enriched = enrich_submission(item, args.lang)
        enriched["_score"] = score
        results.append(enriched)

    results.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
    results.sort(key=lambda item: item.get("_score", 0), reverse=True)
    limited = results[: args.limit]
    for item in limited:
        item.pop("_score", None)

    return {
        "query": {
            "query": args.query,
            "status": args.status,
            "district": args.district,
            "area": args.area,
            "category": args.category,
            "lang": args.lang,
        },
        "count": len(limited),
        "total_matches": len(results),
        "results": limited,
    }


def comment_store(args: argparse.Namespace) -> dict[str, Any]:
    target_type, target_id = target_identity_from_args(args)
    if not (args.comment_zh.strip() or args.comment_en.strip()):
        raise ValueError("at least one of --comment-zh or --comment-en is required")
    if args.rating is not None and not 1 <= args.rating <= 5:
        raise ValueError("rating must be between 1 and 5")

    items = load_community_comments()
    created_at = current_timestamp()
    author_name = args.author_name.strip() or default_author_name(args.lang)
    comment = {
        "comment_id": build_local_id("comment", items),
        "target_type": target_type,
        "target_id": target_id,
        "status": "visible",
        "author_name": author_name,
        "comment_zh": args.comment_zh.strip(),
        "comment_en": args.comment_en.strip(),
        "rating": args.rating,
        "tags": ensure_list(args.tag),
        "created_at": created_at,
        "updated_at": created_at,
        "scope": "local_installation",
    }
    items.append(comment)
    save_json_array(COMMUNITY_COMMENTS_PATH, items)
    payload = enrich_comment(comment, args.lang)
    payload["message"] = (
        "已记录这条评论，当前仅保存在当前安装副本里。"
        if args.lang == "zh"
        else "Saved this comment. It is currently stored only in this local installation."
    )
    return payload


def list_comments(args: argparse.Namespace) -> dict[str, Any]:
    target_type, target_id = target_identity_from_args(args)
    items = load_community_comments()
    results = [
        enrich_comment(item, args.lang)
        for item in items
        if str(item.get("target_type", "")).strip() == target_type
        and str(item.get("target_id", "")).strip() == target_id
        and (not args.status or normalize(item.get("status")) == normalize(args.status))
    ]
    results.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
    limited = results[: args.limit]
    return {
        "query": {
            "target_type": target_type,
            "target_id": target_id,
            "status": args.status,
            "lang": args.lang,
        },
        "count": len(limited),
        "total_matches": len(results),
        "results": limited,
    }


def render_text(payload: dict[str, Any]) -> str:
    if "results" in payload:
        lines = [
            f"count: {payload.get('count', 0)}",
            f"total_matches: {payload.get('total_matches', 0)}",
        ]
        for store in payload.get("results", []):
            lines.append("")
            if "store_id" in store:
                lines.append(f"- {store.get('display_name_localized', store.get('display_name', ''))}")
                lines.append(f"  store_id: {store.get('store_id', '')}")
                lines.append(
                    "  category: "
                    f"{store.get('primary_category_name_localized', '')}"
                )
                lines.append(
                    f"  area: {store.get('district_localized', '')} / {store.get('area_localized', '')}"
                )
                lines.append(f"  address: {store.get('address_localized', '')}")
                lines.append(f"  today_hours: {store.get('today_hours', 'unknown')}")
                lines.append(f"  open_now: {store.get('open_now', False)}")
                lines.append(
                    f"  dish_types: {', '.join(ensure_list(store.get('dish_types_localized')))}"
                )
                lines.append(
                    f"  tags: {', '.join(ensure_list(store.get('food_tags_localized')))}"
                )
                lines.append(
                    "  signature_dishes: "
                    f"{', '.join(ensure_list(store.get('signature_dishes_localized')))}"
                )
                lines.append(
                    f"  delivery_supported: {store.get('delivery_supported', 'unknown')}"
                )
                lines.append(f"  wifi_policy: {store.get('wifi_policy', 'unknown')}")
                if "distance_km" in store:
                    lines.append(f"  distance_km: {store.get('distance_km')}")
            elif "submission_id" in store:
                lines.append(f"- {store.get('display_name_localized', store.get('display_name', ''))}")
                lines.append(f"  submission_id: {store.get('submission_id', '')}")
                lines.append(f"  status: {store.get('status', '')}")
                lines.append(f"  category: {store.get('category_name_localized', '')}")
                lines.append(f"  area: {store.get('district', '')} / {store.get('area', '')}")
                lines.append(f"  address: {store.get('address', '')}")
                lines.append(
                    f"  dish_types: {', '.join(ensure_list(store.get('dish_types_localized')))}"
                )
                lines.append(
                    f"  recommended_reason: {store.get('recommended_reason_localized', '')}"
                )
                lines.append(f"  submitter_name: {store.get('submitter_name', '')}")
                lines.append(f"  note: {store.get('submitter_note_localized', '')}")
                lines.append(f"  created_at: {store.get('created_at', '')}")
            elif "comment_id" in store:
                lines.append(f"- {store.get('author_name', '')}")
                lines.append(f"  comment_id: {store.get('comment_id', '')}")
                lines.append(f"  target_type: {store.get('target_type', '')}")
                lines.append(f"  target_id: {store.get('target_id', '')}")
                lines.append(
                    f"  target_name: {store.get('target_name_localized', store.get('target_id', ''))}"
                )
                lines.append(f"  rating: {store.get('rating', '')}")
                lines.append(f"  tags: {', '.join(ensure_list(store.get('tags')))}")
                lines.append(f"  comment: {store.get('comment_localized', '')}")
                lines.append(f"  created_at: {store.get('created_at', '')}")
            else:
                lines.append(f"- {store.get('entry_id', '')}")
                lines.append(f"  category: {store.get('category_name_localized', '')}")
                lines.append(f"  intent_type: {store.get('intent_type', '')}")
                lines.append(
                    f"  dish_types: {', '.join(ensure_list(store.get('dish_types_localized')))}"
                )
                lines.append(f"  question: {store.get('question_localized', '')}")
                lines.append(f"  answer: {store.get('answer_localized', '')}")
        return "\n".join(lines)

    if payload.get("error"):
        return payload["error"]

    if "entry_id" in payload:
        return "\n".join(
            [
                f"entry_id: {payload.get('entry_id', '')}",
                f"topic_slug: {payload.get('topic_slug', '')}",
                f"category: {payload.get('category_name_localized', '')}",
                f"intent_type: {payload.get('intent_type', '')}",
                f"dish_types: {', '.join(ensure_list(payload.get('dish_types_localized')))}",
                f"question: {payload.get('question_localized', '')}",
                f"answer: {payload.get('answer_localized', '')}",
                f"last_verified_at: {payload.get('last_verified_at', '')}",
                f"source_url: {payload.get('source_url', '')}",
                f"confidence: {payload.get('confidence', '')}",
            ]
        )

    if "submission_id" in payload:
        return "\n".join(
            [
                str(payload.get("message", "")).strip(),
                f"submission_id: {payload.get('submission_id', '')}",
                f"display_name: {payload.get('display_name_localized', payload.get('display_name', ''))}",
                f"status: {payload.get('status', '')}",
                f"category: {payload.get('category_name_localized', '')}",
                f"district: {payload.get('district', '')}",
                f"area: {payload.get('area', '')}",
                f"address: {payload.get('address', '')}",
                f"dish_types: {', '.join(ensure_list(payload.get('dish_types_localized')))}",
                f"recommended_reason: {payload.get('recommended_reason_localized', '')}",
                f"submitter_name: {payload.get('submitter_name', '')}",
                f"note: {payload.get('submitter_note_localized', '')}",
                f"created_at: {payload.get('created_at', '')}",
            ]
        )

    if "comment_id" in payload:
        return "\n".join(
            [
                str(payload.get("message", "")).strip(),
                f"comment_id: {payload.get('comment_id', '')}",
                f"author_name: {payload.get('author_name', '')}",
                f"target_type: {payload.get('target_type', '')}",
                f"target_id: {payload.get('target_id', '')}",
                f"target_name: {payload.get('target_name_localized', payload.get('target_id', ''))}",
                f"rating: {payload.get('rating', '')}",
                f"tags: {', '.join(ensure_list(payload.get('tags')))}",
                f"comment: {payload.get('comment_localized', '')}",
                f"created_at: {payload.get('created_at', '')}",
            ]
        )

    lines = [
        f"display_name: {payload.get('display_name_localized', payload.get('display_name', ''))}",
        f"store_id: {payload.get('store_id', '')}",
        f"primary_category: {payload.get('primary_category_name_localized', '')}",
        f"district: {payload.get('district_localized', '')}",
        f"area: {payload.get('area_localized', '')}",
        f"address: {payload.get('address_localized', '')}",
        f"today_hours: {payload.get('today_hours', 'unknown')}",
        f"open_now: {payload.get('open_now', False)}",
        f"recommended_reason: {payload.get('recommended_reason_localized', '')}",
        f"dish_types: {', '.join(ensure_list(payload.get('dish_types_localized')))}",
        f"food_tags: {', '.join(ensure_list(payload.get('food_tags_localized')))}",
        f"signature_dishes: {', '.join(ensure_list(payload.get('signature_dishes_localized')))}",
        f"queue_notes: {payload.get('queue_notes_localized', '')}",
        f"delivery_supported: {payload.get('delivery_supported', 'unknown')}",
        f"delivery_platforms: {', '.join(ensure_list(payload.get('delivery_platforms')))}",
        f"wifi_policy: {payload.get('wifi_policy', 'unknown')}",
        f"wifi_name: {payload.get('wifi_name', '')}",
        f"wifi_password: {payload.get('wifi_password', '')}",
        f"notes: {payload.get('notes_localized', '')}",
        f"last_verified_at: {payload.get('last_verified_at', '')}",
    ]
    if "distance_km" in payload:
        lines.append(f"distance_km: {payload.get('distance_km')}")
    if "community_comments_count" in payload:
        lines.append(f"community_comments_count: {payload.get('community_comments_count')}")
        for index, comment in enumerate(payload.get("community_comments", []), start=1):
            author = str(comment.get("author_name", "")).strip()
            text = str(comment.get("comment_localized", "")).strip()
            rating = comment.get("rating")
            suffix = f" ({rating}/5)" if rating else ""
            lines.append(f"community_comment_{index}: {author}{suffix} - {text}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query Xi'an carbohydrates guide data")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Search stores")
    search.add_argument("--query", default="", help="Free-text keyword search")
    search.add_argument("--district", default="", help="District name")
    search.add_argument("--area", default="", help="Business area or neighborhood")
    search.add_argument("--landmark", default="", help="Nearby landmark")
    search.add_argument("--category", action="append", default=[], help="Category filter")
    search.add_argument("--tag", action="append", default=[], help="Food tag filter")
    search.add_argument("--dish", action="append", default=[], help="Signature dish filter")
    search.add_argument("--open-now", action="store_true", help="Only return open stores")
    search.add_argument("--delivery", action="store_true", help="Only return delivery stores")
    search.add_argument("--wifi", action="store_true", help="Only return stores with usable Wi-Fi")
    search.add_argument("--near-lat", type=float, default=None, help="User latitude")
    search.add_argument("--near-lng", type=float, default=None, help="User longitude")
    search.add_argument("--radius-km", type=float, default=None, help="Distance radius filter")
    search.add_argument("--limit", type=int, default=5, help="Result limit")
    search.add_argument("--at", default="", help="Datetime override in ISO format")
    search.add_argument("--lang", choices=["zh", "en"], default="zh")
    search.add_argument("--format", choices=["json", "text"], default="json")

    detail = subparsers.add_parser("detail", help="Get store detail")
    detail.add_argument("--store-id", required=True, help="Store identifier")
    detail.add_argument("--near-lat", type=float, default=None, help="User latitude")
    detail.add_argument("--near-lng", type=float, default=None, help="User longitude")
    detail.add_argument("--at", default="", help="Datetime override in ISO format")
    detail.add_argument("--include-comments", action="store_true", help="Include community comments")
    detail.add_argument("--comments-limit", type=int, default=3, help="Community comments limit")
    detail.add_argument("--lang", choices=["zh", "en"], default="zh")
    detail.add_argument("--format", choices=["json", "text"], default="json")

    knowledge_search = subparsers.add_parser("knowledge-search", help="Search knowledge entries")
    knowledge_search.add_argument("--query", default="", help="Free-text keyword search")
    knowledge_search.add_argument("--intent-type", default="", help="history/craft/taste/etiquette")
    knowledge_search.add_argument("--category", action="append", default=[], help="Category filter")
    knowledge_search.add_argument("--dish", action="append", default=[], help="Dish filter")
    knowledge_search.add_argument("--limit", type=int, default=5, help="Result limit")
    knowledge_search.add_argument("--lang", choices=["zh", "en"], default="zh")
    knowledge_search.add_argument("--format", choices=["json", "text"], default="json")

    knowledge_detail = subparsers.add_parser("knowledge-detail", help="Get knowledge detail")
    knowledge_detail.add_argument("--entry-id", required=True, help="Knowledge entry identifier")
    knowledge_detail.add_argument("--lang", choices=["zh", "en"], default="zh")
    knowledge_detail.add_argument("--format", choices=["json", "text"], default="json")

    suggest_store_parser = subparsers.add_parser(
        "suggest-store", help="Submit a community store suggestion"
    )
    suggest_store_parser.add_argument("--brand-name", required=True, help="Brand or store name")
    suggest_store_parser.add_argument("--branch-name", default="", help="Branch name")
    suggest_store_parser.add_argument("--district", required=True, help="District")
    suggest_store_parser.add_argument("--area", required=True, help="Area or neighborhood")
    suggest_store_parser.add_argument("--address", required=True, help="Address")
    suggest_store_parser.add_argument("--category", required=True, help="Primary category")
    suggest_store_parser.add_argument("--dish", action="append", required=True, help="Dish type")
    suggest_store_parser.add_argument("--dish-en", action="append", default=[], help="Dish type in English")
    suggest_store_parser.add_argument("--submitter-name", default="", help="Submitter name")
    suggest_store_parser.add_argument("--reason-zh", default="", help="Recommendation reason in Chinese")
    suggest_store_parser.add_argument("--reason-en", default="", help="Recommendation reason in English")
    suggest_store_parser.add_argument("--note-zh", default="", help="Submitter note in Chinese")
    suggest_store_parser.add_argument("--note-en", default="", help="Submitter note in English")
    suggest_store_parser.add_argument("--source-url", default="", help="Optional source URL")
    suggest_store_parser.add_argument("--lang", choices=["zh", "en"], default="zh")
    suggest_store_parser.add_argument("--format", choices=["json", "text"], default="json")

    list_suggestions_parser = subparsers.add_parser(
        "list-suggestions", help="List community store suggestions"
    )
    list_suggestions_parser.add_argument("--query", default="", help="Free-text keyword search")
    list_suggestions_parser.add_argument("--status", default="", help="pending/approved/rejected")
    list_suggestions_parser.add_argument("--district", default="", help="District filter")
    list_suggestions_parser.add_argument("--area", default="", help="Area filter")
    list_suggestions_parser.add_argument("--category", action="append", default=[], help="Category filter")
    list_suggestions_parser.add_argument("--limit", type=int, default=10, help="Result limit")
    list_suggestions_parser.add_argument("--lang", choices=["zh", "en"], default="zh")
    list_suggestions_parser.add_argument("--format", choices=["json", "text"], default="json")

    comment_store_parser = subparsers.add_parser(
        "comment-store", help="Add a community comment to a store or submission"
    )
    comment_store_parser.add_argument("--store-id", default="", help="Target store id")
    comment_store_parser.add_argument("--submission-id", default="", help="Target submission id")
    comment_store_parser.add_argument("--author-name", default="", help="Comment author name")
    comment_store_parser.add_argument("--comment-zh", default="", help="Comment in Chinese")
    comment_store_parser.add_argument("--comment-en", default="", help="Comment in English")
    comment_store_parser.add_argument("--rating", type=int, default=None, help="Optional rating 1-5")
    comment_store_parser.add_argument("--tag", action="append", default=[], help="Comment tag")
    comment_store_parser.add_argument("--lang", choices=["zh", "en"], default="zh")
    comment_store_parser.add_argument("--format", choices=["json", "text"], default="json")

    list_comments_parser = subparsers.add_parser(
        "list-comments", help="List community comments for a store or submission"
    )
    list_comments_parser.add_argument("--store-id", default="", help="Target store id")
    list_comments_parser.add_argument("--submission-id", default="", help="Target submission id")
    list_comments_parser.add_argument("--status", default="visible", help="visible/hidden")
    list_comments_parser.add_argument("--limit", type=int, default=10, help="Result limit")
    list_comments_parser.add_argument("--lang", choices=["zh", "en"], default="zh")
    list_comments_parser.add_argument("--format", choices=["json", "text"], default="json")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "search":
            payload = search_stores(args)
        elif args.command == "detail":
            payload = detail_store(args)
        elif args.command == "knowledge-search":
            payload = search_knowledge(args)
        elif args.command == "knowledge-detail":
            payload = detail_knowledge(args)
        elif args.command == "suggest-store":
            payload = suggest_store(args)
        elif args.command == "list-suggestions":
            payload = list_suggestions(args)
        elif args.command == "comment-store":
            payload = comment_store(args)
        elif args.command == "list-comments":
            payload = list_comments(args)
        else:
            parser.error(f"Unsupported command: {args.command}")
            return 2
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    if args.format == "text":
        print(render_text(payload))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
