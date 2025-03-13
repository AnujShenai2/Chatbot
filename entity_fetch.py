from db import cursor_1, cursor_2

def fetch_entities(cursor, table, column):
    try:
        cursor.execute(f"SELECT {column} FROM {table}")
        return list(set(str(row[0]).strip().lower() for row in cursor.fetchall() if row[0]))
    except Exception as e:
        print(f"Error fetching {column} from {table}: {e}")
        return []

makers_list = fetch_entities(cursor_1, "vehicle_make", "make_name")
models_list = fetch_entities(cursor_1, "vehicle_model", "model_name")
variants_list = fetch_entities(cursor_1, "vehicle_variant", "variant_name")
years_list = fetch_entities(cursor_1, "vehicle_year", "release_year")
fuel_type_list = fetch_entities(cursor_1, "vehicle_fuel_type", "fuel_type_name")
category_list = fetch_entities(cursor_2, "category", "category_name")
sub_category_list = fetch_entities(cursor_2, "sub_category", "sub_category_name")