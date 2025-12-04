from pyapu.types import Type

class SchemaAdapter:

    @staticmethod
    def to_google(pyapu_schema):
        """Converts PyAPU schema -> Google GenAI Schema"""
        from google.genai import types as g_types

        # Recursive conversion
        props = {k: SchemaAdapter.to_google(v) for k, v in
                 pyapu_schema.properties.items()} if pyapu_schema.properties else None
        items = SchemaAdapter.to_google(pyapu_schema.items) if pyapu_schema.items else None

        # Map Enum (PyAPU Type -> Google Type)
        type_map = {
            Type.STRING: g_types.Type.STRING,
            Type.NUMBER: g_types.Type.NUMBER,
            Type.OBJECT: g_types.Type.OBJECT,
            Type.ARRAY: g_types.Type.ARRAY,
            Type.BOOLEAN: g_types.Type.BOOLEAN,
            Type.INTEGER: g_types.Type.INTEGER
        }

        return g_types.Schema(
            # FIX: Use the Enum directly, NOT .value
            type=type_map[pyapu_schema.type],
            description=pyapu_schema.description,
            properties=props,
            items=items,
            required=pyapu_schema.required,
            nullable=pyapu_schema.nullable
        )

    @staticmethod
    def to_openai(pyapu_schema):
        """Converts PyAPU schema -> OpenAI JSON Schema (Dict)"""
        schema_dict = {
            # OpenAI expects generic strings like "object", "string"
            "type": pyapu_schema.type.value.lower(),
            "description": pyapu_schema.description
        }

        if pyapu_schema.properties:
            schema_dict["properties"] = {
                k: SchemaAdapter.to_openai(v) for k, v in pyapu_schema.properties.items()
            }
            schema_dict["additionalProperties"] = False

        if pyapu_schema.required:
            schema_dict["required"] = pyapu_schema.required

        if pyapu_schema.items:
            schema_dict["items"] = SchemaAdapter.to_openai(pyapu_schema.items)

        return schema_dict