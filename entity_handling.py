from db import cursor_1, cursor_2
from preprocess import find_closest_match, process_input_with_spelling_correction

def check_make_exists(make_name):
    cursor_1.execute("SELECT id FROM vehicle_make WHERE make_name = %s", (make_name,))
    return cursor_1.fetchone() is not None

def get_available_makes():
    cursor_1.execute("SELECT make_name FROM vehicle_make")
    return [row[0] for row in cursor_1.fetchall()]

def get_available_models(make):
    query = "SELECT vm.model_name FROM vehicle_model vm JOIN vehicle_make v ON vm.vehicle_make_id = v.id WHERE v.make_name = %s"
    cursor_1.execute(query, (make,))
    result = [row[0] for row in cursor_1.fetchall()]
    print(f"SQL query for '{make}' returned {len(result)} models: {result}")
    return result

def get_make_for_model(model):
    query = """
    SELECT v.make_name 
    FROM vehicle_make v 
    JOIN vehicle_model vm ON v.id = vm.vehicle_make_id 
    WHERE vm.model_name = %s
    """
    cursor_1.execute(query, (model,))
    result = cursor_1.fetchone()
    return result[0] if result else None

def fetch_subcategories(category):
    cursor_2.execute(
        "SELECT sc.sub_category_name FROM sub_category sc JOIN category c ON sc.category_id = c.category_id WHERE c.category_name = %s",
        (category,)
    )
    return [row[0] for row in cursor_2.fetchall()]

def check_subcategory_availability(make, model, subcategory):
    try:
        return True
    except Exception as e:
        print(f"Error checking availability: {e}")
        return False

def get_category_for_subcategory(subcategory):
    try:
        cursor_2.execute("""
            SELECT c.category_name 
            FROM category c 
            JOIN sub_category sc ON c.category_id = sc.category_id 
            WHERE sc.sub_category_name = %s
        """, (subcategory,))
        result = cursor_2.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error getting category for subcategory: {e}")
        return None

def normalize_make_name(make):
    make_lower = make.lower()
    if make_lower in ["maruti", "suzuki", "maruti suzuki"]:
        if check_make_exists("Maruti Suzuki"): return "Maruti Suzuki"
        elif check_make_exists("Maruti"): return "Maruti"
        elif check_make_exists("Suzuki"): return "Suzuki"
    return make

def handle_make_selection(make, session_memory):
    make = normalize_make_name(make)
    session_memory.update({"MAKE": make})
    print(f"Debug - Normalized make: '{make}'")
    
    original_makes = get_available_makes()
    original_makes_lower = [m.lower().strip() for m in original_makes]

    def get_valid_make_from_user():
        print("\nBot: The detected make is not valid. Here are the available makes:")
        print("- " + "\n- ".join(original_makes))
        user_input = process_input_with_spelling_correction(input("You: ").strip())
        
        if user_input.lower() in original_makes_lower:
            return original_makes[original_makes_lower.index(user_input.lower())]
        
        best_match = find_closest_match(user_input.lower(), original_makes_lower)
        return original_makes[original_makes_lower.index(best_match)] if best_match in original_makes_lower else user_input

    if make.lower() in original_makes_lower:
        valid_make = original_makes[original_makes_lower.index(make.lower())]
        session_memory.update({"MAKE": valid_make})
        return True

    corrected_make_lower = find_closest_match(make.lower(), original_makes_lower)

    if corrected_make_lower != make.lower():
        corrected_make = original_makes[original_makes_lower.index(corrected_make_lower)]
        print(f"\nBot: Did you mean '{corrected_make}'? (yes/no)")
        
        if input("You: ").strip().lower().startswith('y'):
            session_memory.update({"MAKE": corrected_make})
            return True

    valid_make = get_valid_make_from_user()
    session_memory.update({"MAKE": valid_make})
    return False

def handle_model_selection(make, model, session_memory):
    available_models = get_available_models(make)
    available_models_lower = [m.lower().strip() for m in available_models]

    def get_model_from_user():
        print(f"\nBot: Please select a valid model for {make}. Available models:")
        print("- " + "\n- ".join(available_models))
        user_input = input("You: ").strip().lower()
        return process_input_with_spelling_correction(user_input)

    if not model or model.lower().strip() not in available_models_lower:
        if model:
            corrected_model = find_closest_match(model.lower().strip(), available_models_lower)
            if corrected_model in available_models_lower:
                original_case_model = available_models[available_models_lower.index(corrected_model)]
                print(f"\nBot: Did you mean '{original_case_model}'? (yes/no)")
                if input("You: ").strip().lower().startswith('y'):
                    session_memory.update({"MODEL": original_case_model})
                    return True
        
        while True:
            corrected_input = get_model_from_user()
            if corrected_input in available_models_lower:
                session_memory.update({"MODEL": available_models[available_models_lower.index(corrected_input)]})
                return True
            print("\nBot: Invalid model. Try again or type 'exit' to quit.")
            if input("You: ").strip().lower() == 'exit':
                print("\nBot: Exiting model selection.")
                return False

    session_memory.update({"MODEL": model})
    return True