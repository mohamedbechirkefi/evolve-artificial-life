# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Versioned JSON result schema, validated at export and at import.

The schema document is `schemas/run_result-1.0.0.json` (a JSON Schema 2020-12
subset). This module implements the subset it uses (type, const, enum,
required, properties, additionalProperties false, items, minimum, maximum,
minLength, pattern, local $ref) so that no extra dependency is needed.
Non-finite numbers are always rejected. Validation fails closed.
"""

from __future__ import annotations

import json
import math
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from .errors import SchemaError

SCHEMA_NAME = "evolve.run_result"
SCHEMA_VERSION = "1.0.0"
_SCHEMA_DIR = Path(__file__).parent / "schemas"


@lru_cache(maxsize=None)
def load_schema(version: str = SCHEMA_VERSION) -> dict:
    path = _SCHEMA_DIR / f"run_result-{version}.json"
    if not path.exists():
        raise SchemaError(f"unknown schema version {version!r}")
    return json.loads(path.read_text(encoding="utf-8"))


def _type_ok(value: Any, t: str) -> bool:
    if t == "object":
        return isinstance(value, dict)
    if t == "array":
        return isinstance(value, list)
    if t == "string":
        return isinstance(value, str)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "null":
        return value is None
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    raise SchemaError(f"schema uses unsupported type {t!r}")


def _validate(value: Any, schema: dict, root: dict, path: str) -> None:
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            raise SchemaError(f"{path}: only local $ref is supported")
        target: Any = root
        for part in ref[2:].split("/"):
            target = target[part]
        _validate(value, target, root, path)
        return
    if isinstance(value, float) and not math.isfinite(value):
        raise SchemaError(f"{path}: non-finite number")
    if "const" in schema and value != schema["const"]:
        raise SchemaError(f"{path}: expected {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise SchemaError(f"{path}: {value!r} not in {schema['enum']}")
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(value, t) for t in types):
            raise SchemaError(f"{path}: expected type {types}, got {type(value).__name__}")
    if value is None:
        return
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise SchemaError(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            raise SchemaError(f"{path}: {value} > maximum {schema['maximum']}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise SchemaError(f"{path}: string shorter than {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise SchemaError(f"{path}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, dict):
        for k in schema.get("required", []):
            if k not in value:
                raise SchemaError(f"{path}: missing required key {k!r}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(value) - set(props)
            if extra:
                raise SchemaError(f"{path}: unexpected keys {sorted(extra)}")
        for k, sub in props.items():
            if k in value:
                _validate(value[k], sub, root, f"{path}.{k}")
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            _validate(item, schema["items"], root, f"{path}[{i}]")


def validate_result(doc: Any) -> None:
    """Raise SchemaError unless `doc` is a valid run result of a known version."""
    if not isinstance(doc, dict):
        raise SchemaError("$: a run result must be an object")
    if doc.get("schema") != SCHEMA_NAME:
        raise SchemaError(f"$.schema: expected {SCHEMA_NAME!r}")
    schema = load_schema(str(doc.get("schema_version")))
    _validate(doc, schema, schema, "$")
    if doc["status"] == "ok":
        for k in ("metrics", "episodes", "trace"):
            if doc[k] is None:
                raise SchemaError(f"$.{k}: required for status 'ok'")
        if doc["trace"]["returned_index"] >= len(doc["trace"]["train_fitness"]):
            raise SchemaError("$.trace.returned_index out of range")
        if len(doc["trace"]["train_fitness"]) != doc["metrics"]["n_evaluations"]:
            raise SchemaError("$.trace.train_fitness length differs from n_evaluations")
    elif not doc["failure"]:
        raise SchemaError("$.failure: required for status 'failed'")
    if doc["manifest"]["run_id"] != doc["run_id"] or doc["manifest"]["config_hash"] != doc["config_hash"]:
        raise SchemaError("$.manifest: run_id or config_hash differs from the result")


def validate_manifest(doc: Any) -> None:
    schema = load_schema(SCHEMA_VERSION)
    _validate(doc, schema["$defs"]["manifest"], schema, "$")


def dump_result(doc: dict, path: str | Path) -> None:
    """Validate, then write. A document that fails validation is never written."""
    validate_result(doc)
    text = json.dumps(doc, indent=1, sort_keys=True, allow_nan=False)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text + "\n", encoding="utf-8")


def load_result(path: str | Path) -> dict:
    """Read and validate a result file (fails closed)."""
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SchemaError(f"{path}: invalid JSON ({e})") from e
    validate_result(doc)
    return doc
