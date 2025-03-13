import torch
import torch.nn as nn
import numpy as np

class GRUSessionMemory(nn.Module):

    """
        Initializes the GRUSessionMemory module.

        Args:
            input_size (int): Size of the input features for the GRU.
            hidden_size (int): Size of the hidden state in the GRU.
            entity_types (list): List of entity types (e.g., ['toyota', 'maruthi suzuki']).
    """

    def __init__(self, input_size, hidden_size, entity_types):
        super(GRUSessionMemory, self).__init__()
        self.hidden_size = hidden_size  # Size of the GRU hidden state
        self.entity_types = entity_types  # List of entity types
        self.gru = nn.GRU(input_size, hidden_size, batch_first=True)  # GRU layer
        self.fc = nn.Linear(hidden_size, len(entity_types))  # Fully connected layer for entity type prediction
        self.embedding_dim = 384  # Default embedding dimension (e.g., for SentenceTransformer)
        self.embedding_projection = nn.Linear(hidden_size, self.embedding_dim)  # Projects GRU output to embedding space
        self.entity_embeddings = {}  # Dictionary to store entity embeddings
        self.current_state = torch.zeros(1, 1, hidden_size)  # Initial hidden state of the GRU

    # processes input data through the GRU and a fully connected layer to predict 
    # entity types, returning both the predictions and the updated hidden state

    def forward(self, x, hidden):
        out, hidden = self.gru(x, hidden)  # Pass input through GRU
        out = self.fc(out)  # Map GRU output to entity type predictions
        return out, hidden
    
    # Updates the memory (hidden state) based on new entity information.

    def update_memory(self, entities):      
        input_tensor = self._entities_to_tensor(entities)  # Convert entities to input tensor
        _, self.current_state = self.gru(input_tensor, self.current_state)  # Update hidden state

    # Retrieves the closest matching entity of a specific type from memory. 

    def get_entity(self, entity_type):
        query_tensor = torch.zeros(1, 1, len(self.entity_types))  # Create a query tensor
        entity_idx = self.entity_types.index(entity_type) if entity_type in self.entity_types else -1  # Find entity index
        
        if entity_idx >= 0:  # If entity type is valid
            query_tensor[0, 0, entity_idx] = 1.0  # One-hot encode the entity type
            with torch.no_grad():  # Disable gradient computation
                hidden = self.current_state  # Use current hidden state
                out, _ = self.gru(query_tensor, hidden)  # Pass query through GRU
                return self._find_closest_entity(out[0, 0].numpy(), entity_type)  # Find closest entity
        return None  # if invalid
    
    # Retrieves all entities stored in memory

    def get_all_entities(self):
        result = {}
        for entity_type in self.entity_types:  # Iterate over all entity types
            entity_value = self.get_entity(entity_type)  # Retrieve entity value
            if entity_value:
                result[entity_type] = entity_value  # Add to result dictionary
        return result
    
    # Converts a dictionary of entities into a tensor suitable for input to the GRU.

    def _entities_to_tensor(self, entities):
        input_tensor = torch.zeros(1, 1, len(self.entity_types))  # Initialize tensor with zeros
        for entity_type, entity_value in entities.items():  # Iterate over entities
            if entity_type in self.entity_types:  # If entity type is valid
                entity_idx = self.entity_types.index(entity_type)  # Get entity index
                input_tensor[0, 0, entity_idx] = 1.0  # One-hot encode the entity type
                if hasattr(self, 'embedding_model'):  # If embedding model is available
                    self.entity_embeddings[f"{entity_type}_{entity_value}"] = self.embedding_model.encode(entity_value)  # Store embedding
        return input_tensor
    
    # Finds the closest matching entity for a given query vector.

    def _find_closest_entity(self, query_vector, entity_type):
        matching_keys = [k for k in self.entity_embeddings.keys() if k.startswith(f"{entity_type}_")]  # Filter matching keys
        if not matching_keys:  # If no matching keys, return None
            return None
            
        query_tensor = torch.tensor(query_vector, dtype=torch.float32).unsqueeze(0)  # Convert query vector to tensor
        with torch.no_grad():  # Disable gradient computation
            projected_query = self.embedding_projection(query_tensor).squeeze(0).numpy()  # Project query to embedding space
        
        closest_entity = None  # Initialize closest entity
        best_score = -float('inf')  # Initialize best similarity score
        
        for key, embedding in self.entity_embeddings.items():  # Iterate over embeddings
            if key.startswith(f"{entity_type}_"):  # If key matches entity type
                try:
                    # Compute cosine similarity
                    score = np.dot(projected_query, embedding) / (np.linalg.norm(projected_query) * np.linalg.norm(embedding))
                    if score > best_score:  # Update best score and closest entity
                        best_score = score
                        closest_entity = key.split('_', 1)[1]
                except ValueError as e:  # Handle dimension mismatch
                    print(f"Warning: Dimension mismatch in similarity calculation: {e}")
                    return matching_keys[-1].split('_', 1)[1]  # Return last matching entity
        
        return closest_entity  # Return closest entity
    
    def clear(self):
        self.current_state = torch.zeros(1, 1, self.hidden_size)  # Reset hidden state
        self.entity_embeddings = {}  # Clear entity embeddings
        
    def set_embedding_model(self, model):
        self.embedding_model = model  # Set embedding model
        if hasattr(model, 'get_sentence_embedding_dimension'):  # If model has embedding dimension
            actual_dim = model.get_sentence_embedding_dimension()  # Get actual embedding dimension
            if actual_dim != self.embedding_dim:  # If dimension differs from default
                print(f"Warning: Updating embedding projection from {self.embedding_dim} to {actual_dim}")
                self.embedding_dim = actual_dim  # Update embedding dimension
                self.embedding_projection = nn.Linear(self.hidden_size, self.embedding_dim)  # Reinitialize projection layer