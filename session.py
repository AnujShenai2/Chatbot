def should_start_new_session(detected_entities, session_memory):
    session_entities = session_memory.get_all_entities()
    available_subcategories = session_entities.get("AVAILABLE_SUBCATEGORIES", [])
    
    if "SUB_CATEGORY" in detected_entities and available_subcategories:
        if detected_entities["SUB_CATEGORY"].lower() in map(str.lower, available_subcategories):
            return False
    
    if "CATEGORY" in detected_entities or ("MAKE" in detected_entities and "MAKE" in session_entities and detected_entities["MAKE"].lower() != session_entities["MAKE"].lower()):
        return True
    
    return False