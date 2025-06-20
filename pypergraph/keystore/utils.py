import json
import brotli


def remove_nulls(obj):
    if obj is None:
        return None
    if isinstance(obj, list):
        # Process list items and filter out None values
        return [remove_nulls(item) for item in obj if remove_nulls(item) is not None]
    if isinstance(obj, dict):
        # Process dictionary values and remove keys with None values
        return {
            key: remove_nulls(value)
            for key, value in obj.items()
            if remove_nulls(value) is not None
        }
    return obj


def sort_object_keys(obj):
    if isinstance(obj, dict):
        # Sort keys and recursively process values
        return {key: sort_object_keys(obj[key]) for key in sorted(obj)}
    if isinstance(obj, list):
        # Recursively process list items
        return [sort_object_keys(item) for item in obj]
    return obj


def normalize_object(obj, sort=True, remove=True):
    processed = obj
    if remove:
        processed = remove_nulls(processed)
    if sort:
        processed = sort_object_keys(processed)
    return processed


def serialize_brotli(content, compression_level=2):
    normalized = normalize_object(content)
    normalized_json = json.dumps(normalized, separators=(",", ":"), ensure_ascii=False)
    utf8_bytes = normalized_json.encode("utf-8")
    return brotli.compress(utf8_bytes, quality=compression_level)
