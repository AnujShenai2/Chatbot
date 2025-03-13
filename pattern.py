import spacy
from spacy.matcher import PhraseMatcher
from preprocess import get_best_match, process_input_with_spelling_correction
from entity_fetch import makers_list, models_list, variants_list, years_list, fuel_type_list, category_list, sub_category_list

STOP_WORDS = {"are", "there", "is", "do", "you", "have", "for", "the", "a", "an", "of", "in", "to", "and", "on", "at", "by"}

nlp = spacy.blank("en")
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

entity_dict = {
    "MAKE": makers_list, "MODEL": models_list, "VARIANT": variants_list, 
    "YEAR": years_list, "FUEL_TYPE": fuel_type_list, 
    "CATEGORY": category_list, "SUB_CATEGORY": sub_category_list
}

def create_patterns(phrase_list):
    return [nlp.make_doc(phrase.lower()) for phrase in phrase_list if phrase]

for entity_type, entity_list in entity_dict.items():
    if entity_list:
        matcher.add(entity_type, create_patterns(entity_list))

def extract_entities(query):
    words = query.split()
    filtered_words = [word for word in words if word.lower() not in STOP_WORDS]
    cleaned_query = " ".join(filtered_words)
    
    corrected_query = process_input_with_spelling_correction(cleaned_query)
    print(f"Debug - Filtered and corrected query: '{corrected_query}'")
    
    doc = nlp(corrected_query)
    matches = matcher(doc)
    entities = {nlp.vocab.strings[m_id]: doc[start:end].text for m_id, start, end in matches}
    
    if not entities:
        best_match = get_best_match(corrected_query)
        if best_match:
            return {"UNKNOWN": best_match}
    return entities