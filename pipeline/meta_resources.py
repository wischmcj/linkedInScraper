from __future__ import annotations

import json

import dlt


def as_resource(name, data, **kwargs):
    @dlt.resource(name=name, **kwargs)
    def data_resource():
        if isinstance(data, list):
            yield data
        else:
            yield [data]

    return data_resource


def file_resource(
    file_name,
):
    with open(file_name) as f:
        data = json.load(f)
        recipes = []
        mappings = []
        all_fields_rows = []
        for recipe_id, datum in data.items():
            fields_details = datum["fields"]
            fields = datum["fields"].keys()
            recipe = [
                {
                    "table_name": "recipes",
                    "recipe_id": recipe_id,
                    "baseType": datum["baseType"],
                    "fields": list(fields),
                }
            ]
            fields_to_recipe = [
                {
                    "table_name": "fields_to_recipe",
                    "recipe_id": recipe_id,
                    "field": field,
                }
                for field in fields
            ]
            field_rows = []
            for field, details in fields_details.items():
                row = {"table_name": "fields", "field": field}
                for name, value in details.items():
                    row[name] = value
                field_rows.append(row)
            recipes.extend(recipe)
            mappings.extend(fields_to_recipe)
            all_fields_rows.extend(field_rows)

        return recipes, mappings, all_fields_rows


@dlt.source
def schemata_resources():
    import glob

    files = glob.glob("data/endpoint_responses/schemata/*.json")
    all_recipes = []
    all_mappings = []
    all_fields_rows = []
    for file in files:
        data = file_resource(file)
        recipes, mappings, fields_rows = data
        all_recipes.extend(recipes)
        all_mappings.extend(mappings)
        all_fields_rows.extend(fields_rows)

    resources = []
    kwargs = {"max_table_nesting": 0, "table_name": lambda row: row["table_name"]}
    kwargs["primary_key"] = "recipe_id"
    resources.append(as_resource("recipe_resource", all_recipes, **kwargs))
    _ = kwargs.pop("primary_key")
    resources.append(as_resource("mapping_resource", all_mappings, **kwargs))
    kwargs["primary_key"] = "field"
    resources.append(as_resource("field_resource", all_fields_rows, **kwargs))
    return resources
