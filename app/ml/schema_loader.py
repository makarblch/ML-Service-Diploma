import json
from pathlib import Path


class SchemaLoader:
    @staticmethod
    def load_schema(schema_path: str) -> dict:
        path = Path(schema_path)
        if not path.exists():
            raise FileNotFoundError(f"Feature schema not found: {schema_path}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)