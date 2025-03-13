# Chatbot
Contains the main chat file along with its dependencies

1. **db.py** -
This file handles the database connection to MySQL. It contains a function connect_db that establishes a connection to the specified database using the provided credentials. Two database connections are initialized: one for car_detail_db (containing car details like make, model, variant, etc.) and another for car_part_spares_db (containing parts and categories). If the connection fails, the program exits.

2. **entity_fetch.py** -
This file is responsible for fetching entities (e.g., car makes, models, variants, fuel types, categories, etc.) from the database. It uses the database cursors from db.py to execute SQL queries and retrieve data. The fetched data is cleaned and converted into lowercase for consistency. The results are stored in lists like makers_list, models_list, etc., which are used throughout the application.

3. **entity_handling.py** -
This file contains functions to handle and validate user inputs related to car makes, models, categories, and subcategories. It includes functions like check_make_exists, get_available_makes, get_available_models, and normalize_make_name to ensure the user's input matches the data in the database. It also handles spelling corrections and user prompts for invalid inputs.

4. **gru_mem.py** -
This file implements a GRU (Gated Recurrent Unit) based session memory system. It stores and retrieves entities (e.g., car make, model, category) during a user session. The GRU model helps in maintaining context and predicting the next entity based on user input. It also includes functions to update memory, retrieve entities, and clear the session.

5. **misspelt_model.py** -
This file contains a spelling correction model trained using TF-IDF and K-Nearest Neighbors (KNN). It generates common misspellings for words in the dataset (e.g., car makes, models, categories) and trains a model to correct user inputs. The correct_spelling function is exported and used in other files to preprocess user queries.

6. **nlp_setup.py** -
This file sets up the NLP (Natural Language Processing) pipeline for the chatbot. It uses the SentenceTransformer library to generate embeddings for car-related entities. These embeddings are indexed using FAISS for fast similarity search. Additionally, it initializes a BM25 model for keyword-based matching.

7. **pattern.py** -
This file uses spaCy and a phrase matcher to extract entities (e.g., car make, model, category) from user queries. It preprocesses the input by removing stopwords and correcting spelling errors. The extracted entities are then matched against predefined patterns to identify relevant information.

8. **preprocess.py** -
This file contains utility functions for preprocessing user input. It includes functions like find_closest_match (for fuzzy matching), process_input_with_spelling_correction (for correcting misspelled words), and get_best_match (for retrieving the most relevant entity using BM25 scoring).

9. **session.py** -
This file defines the logic for managing user sessions. The should_start_new_session function determines whether a new session should be started based on the detected entities and the current session memory. This ensures that the chatbot maintains context during a conversation.

10. **chainlit.py** -
This file configures the Chainlit interface for the chatbot. It sets up the chatbot's title, description, theme, and UI settings. Chainlit is used to create an interactive web-based interface for the chatbot.

11. **chain_bot.py** -
This is the main file for the Chainlit-based chatbot. It handles user interactions, extracts entities from queries, and manages session memory. It also integrates with Ollama for generating enhanced responses. The chatbot guides users through selecting car makes, models, categories, and subcategories, and provides information about part availability.

12. **chain_bot.py** -
This is the main file for the Chainlit-based chatbot. It handles user interactions, extracts entities from queries, and manages session memory. It also integrates with Ollama for generating enhanced responses. The chatbot guides users through selecting car makes, models, categories, and subcategories, and provides information about part availability.

13. **chat.py** -
This file implements a command-line version of the chatbot. It uses the same logic as chain_bot.py but runs in a terminal instead of a web interface. It includes functions for handling user input, managing sessions, and interacting with the database and NLP models.
