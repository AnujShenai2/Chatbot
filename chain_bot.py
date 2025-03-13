import chainlit as cl
import ollama
import spacy
from db import cursor_1, cursor_2
from entity_handling import (
    get_make_for_model, handle_make_selection, handle_model_selection,
    fetch_subcategories, check_subcategory_availability, get_category_for_subcategory
)
from pattern import extract_entities, nlp, matcher
from preprocess import process_input_with_spelling_correction
# Modified import to handle the session properly
# from session import should_start_new_session

# Define our own function based on the error message
def should_start_new_session(detected_entities, session_memory):
    """
    Determine if we should start a new session based on detected entities
    and existing session memory.
    """
    # If no entities are detected, continue with the current session
    if not detected_entities:
        return False
    
    # If session is empty, no need to start a new one
    if not session_memory:
        return False
    
    # Check if a new make or model is detected that's different from session
    session_make = session_memory.get("MAKE")
    session_model = session_memory.get("MODEL")
    
    detected_make = detected_entities.get("MAKE")
    detected_model = detected_entities.get("MODEL")
    
    # If a different make is detected, start a new session
    if detected_make and session_make and detected_make.lower() != session_make.lower():
        return True
        
    # If a different model is detected, start a new session
    if detected_model and session_model and detected_model.lower() != session_model.lower():
        return True
    
    return False

# Store user sessions
user_sessions = {}

@cl.on_chat_start
async def start():
    # Initialize a new session for the user
    # Use a unique identifier for the session
    session_id = cl.user_session.get("session_id", str(id(cl.user_session)))
    cl.user_session.set("session_id", session_id)
    
    # Initialize empty session memory
    user_sessions[session_id] = {}
    
    # Welcome message
    await cl.Message(
        content="Welcome to the Car Parts Chatbot! You can ask about car parts for different makes and models.",
        author="Car Parts Assistant"
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    # Get the session ID
    session_id = cl.user_session.get("session_id", str(id(cl.user_session)))
    
    # Get or create session memory for this user
    if session_id not in user_sessions:
        user_sessions[session_id] = {}
    
    session_memory = user_sessions[session_id]
    user_query = message.content
    
    # Handle exit or new session commands
    if user_query.lower() == "exit":
        await cl.Message(content="Goodbye! 😊", author="Car Parts Assistant").send()
        return
    elif user_query.lower() == "new":
        user_sessions[session_id] = {}
        await cl.Message(content="Starting a new session...", author="Car Parts Assistant").send()
        return
    
    # Extract entities from the query
    detected_entities = extract_entities(user_query)
    
    # Check if we should start a new session
    if should_start_new_session(detected_entities, session_memory):
        user_sessions[session_id] = {}
        session_memory = user_sessions[session_id]
    
    # Update session with newly detected entities
    session_memory.update(detected_entities)
    
    # Get entity variables
    make = session_memory.get("MAKE")
    model = session_memory.get("MODEL")
    category = session_memory.get("CATEGORY")
    sub_category = session_memory.get("SUB_CATEGORY")
    
    # Flag to track if make has been found through model
    make_found_through_model = False
    
    if model and not make:
        detected_make = get_make_for_model(model)
        if detected_make:
            session_memory["MAKE"] = detected_make
            make = detected_make
            make_found_through_model = True
            await cl.Message(
                content=f"I see you're interested in a {model}, which is a {make} model.",
                author="Car Parts Assistant"
            ).send()
    
    # Handle make selection (only if make is present and not already found via model)
    if make and not make_found_through_model:
        make_valid = handle_make_selection(make, session_memory)
        if not make_valid:
            await cl.Message(
                content=f"Sorry, I couldn't find {make} in our database. Please try another make.",
                author="Car Parts Assistant"
            ).send()
            return
    
    if not category and not sub_category:
        await cl.Message(
            content="What category of parts are you looking for?",
            author="Car Parts Assistant"
        ).send()
        return
    
    # Ask for make if not present and not already found through model
    if not make and not make_found_through_model:
        await cl.Message(
            content=f"Which make do you need {category or sub_category} for?",
            author="Car Parts Assistant"
        ).send()
        return
    
    # Handle model selection if make is present but model is not
    make = session_memory.get("MAKE")
    if make and not model:
        model_valid = handle_model_selection(make, model, session_memory)
        if not model_valid:
            await cl.Message(
                content=f"Please specify a valid model for {make}.",
                author="Car Parts Assistant"
            ).send()
            return
    
    # Prepare response
    model = session_memory.get("MODEL")
    sub_category = session_memory.get("SUB_CATEGORY")
    category = session_memory.get("CATEGORY")
    
    # Build the response
    response_text = ""
    
    if sub_category:
        if "AVAILABLE_SUBCATEGORIES" in session_memory and any(sc.lower() == sub_category.lower() for sc in session_memory["AVAILABLE_SUBCATEGORIES"]):
            # Check actual availability for the make/model
            is_available = check_subcategory_availability(make, model, sub_category)
            
            if is_available:
                response_text = f"Yes, '{sub_category}' is available for {make} {model}."
            else:
                response_text = f"Sorry, '{sub_category}' is not currently available for {make} {model}."
        else:
            # This is a new subcategory not from the list
            # Get the category if not already present
            if not category:
                found_category = get_category_for_subcategory(sub_category)
                if found_category:
                    category = found_category
                    session_memory["CATEGORY"] = category
            
            is_available = check_subcategory_availability(make, model, sub_category)
            if is_available:
                response_text = f"Yes, '{sub_category}' is available for {make} {model}."
            else:
                response_text = f"Sorry, '{sub_category}' is not currently available for {make} {model}."
    elif category:
        # Fetch subcategories for this category
        subcategories = fetch_subcategories(category)
        
        session_memory["AVAILABLE_SUBCATEGORIES"] = subcategories
        if subcategories:
            response_text = f"Subcategories under {category}"
            if make and model:
                response_text += f" for {make} {model}:\n- " + "\n- ".join(subcategories)
            else:
                response_text += ":\n- " + "\n- ".join(subcategories)
        else:
            if make and model:
                response_text = f"No subcategories found for {category} for {make} {model}"
            else:
                response_text = f"No subcategories found for {category}"
    
    await cl.Message(content=response_text, author="Car Parts Assistant").send()
    
    # Use Ollama for enhanced responses when appropriate
    use_ollama = False
    if sub_category and "AVAILABLE_SUBCATEGORIES" in session_memory:
        use_ollama = True
    
    if use_ollama:
        # Show typing indicator
        async with cl.Step(name="Generating enhanced response..."):
            # Generate response using Ollama
            try:
                response = ollama.chat(
                    model="gemma:2b",
                    messages=[{"role": "user", "content": f"User asked: {user_query}\nDatabase says: {response_text}\nProvide a clear response."}],
                    options={"max_tokens": 200}
                )
                ollama_response = response["message"]["content"]
                await cl.Message(content=ollama_response, author="Car Parts Assistant").send()
            except Exception as e:
                await cl.Message(
                    content=f"I encountered an issue generating an enhanced response. Please rely on the information provided above.",
                    author="Car Parts Assistant"
                ).send()

if __name__ == "__main__":
    # This part will not be executed when run through the chainlit run command
    pass