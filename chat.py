from gru_mem import GRUSessionMemory
from entity_handling import handle_make_selection, fetch_subcategories, handle_model_selection, get_make_for_model, normalize_make_name, check_subcategory_availability, get_category_for_subcategory
from entity_fetch import makers_list, models_list, variants_list, years_list, fuel_type_list, category_list, sub_category_list
from pattern import extract_entities
from session import should_start_new_session
from preprocess import process_input_with_spelling_correction
from nlp_setup import embedding_model
import ollama
from pattern import entity_dict

def chatbot():
    print("Welcome to the Car Parts Chatbot! Type 'exit' to stop or 'new' to start a new session.")
    
    entity_types = list(entity_dict.keys()) + ["AVAILABLE_SUBCATEGORIES"]
    session_memory = GRUSessionMemory(len(entity_types), 128, entity_types)
    session_memory.set_embedding_model(embedding_model)
    
    while True:
        user_query = input("\nYou: ")
        if user_query.lower() in ["exit", "new"]:
            if user_query.lower() == "new":
                print("Starting a new session...")
                session_memory.clear()
            else:
                print("Goodbye! 😊")
                break
            continue
        
        detected_entities = extract_entities(user_query)
        
        if should_start_new_session(detected_entities, session_memory):
            session_memory.clear()
        
        session_memory.update_memory(detected_entities)
        all_entities = session_memory.get_all_entities()
        
        make = all_entities.get("MAKE")
        model = all_entities.get("MODEL")
        category = all_entities.get("CATEGORY")
        sub_category = all_entities.get("SUB_CATEGORY")
        make_found_through_model = False
        
        if model and not make:
            if detected_make := get_make_for_model(model):
                session_memory.update_memory({"MAKE": detected_make})
                make = detected_make
                make_found_through_model = True
                print(f"\nBot: I see you're interested in a {model}, which is a {make} model.")
        
        if make and not make_found_through_model and not handle_make_selection(make, session_memory):
            continue
        
        if not category and not sub_category:
            print("\nBot: What category of parts are you looking for?")
            corrected_input = process_input_with_spelling_correction(input("You: ").strip())
            session_memory.update_memory({"CATEGORY": corrected_input})
            continue
        
        if not make and not make_found_through_model:
            print(f"\nBot: Which make do you need {category or sub_category} for?")
            make = normalize_make_name(process_input_with_spelling_correction(input("You: ").strip()))
            session_memory.update_memory({"MAKE": make})
            if not handle_make_selection(make, session_memory):
                continue
        
        if not handle_model_selection(make, model, session_memory):
            continue
        
        all_entities = session_memory.get_all_entities()
        model = all_entities.get("MODEL") 
        sub_category = all_entities.get("SUB_CATEGORY")
        category = all_entities.get("CATEGORY")
        
        response_text = ""
        
        if sub_category:
            available_subcategories = all_entities.get("AVAILABLE_SUBCATEGORIES", [])
            if available_subcategories and sub_category.lower() in map(str.lower, available_subcategories):
                is_available = check_subcategory_availability(make, model, sub_category)
                response_text = f"{'Yes' if is_available else 'Sorry'}, '{sub_category}' is {'available' if is_available else 'not available'} for {make} {model}."
            else:
                if not category:
                    if found_category := get_category_for_subcategory(sub_category):
                        session_memory.update_memory({"CATEGORY": found_category})
                        category = found_category
                is_available = check_subcategory_availability(make, model, sub_category)
                response_text = f"{'Yes' if is_available else 'Sorry'}, '{sub_category}' is {'available' if is_available else 'not available'} for {make} {model}."
        elif category:
            subcategories = fetch_subcategories(category)
            session_memory.update_memory({"AVAILABLE_SUBCATEGORIES": subcategories})
            response_text = f"Subcategories under {category}{' for ' + make + ' ' + model if make and model else ''}:\n- " + "\n- ".join(subcategories) if subcategories else f"No subcategories found for {category}{' for ' + make + ' ' + model if make and model else ''}"
        
        print("\nBot:", response_text)
        
        if sub_category and all_entities.get("AVAILABLE_SUBCATEGORIES", []):
            print("\nBot: Generating response with Ollama...")
            stream = ollama.chat(
                model="gemma:2b",
                messages=[{"role": "user", "content": f"User asked: {user_query}\nDatabase says: {response_text}\nProvide a clear response."}],
                options={"max_tokens": 200},
                stream=True,
            )
            print("\nBot: ", end="", flush=True)
            for chunk in stream:
                print(chunk["message"]["content"], end="", flush=True)
            print()

if __name__ == "__main__":
    chatbot()