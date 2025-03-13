from difflib import get_close_matches
from nltk.corpus import stopwords
from nlp_setup import documents, bm25
from missplet_model import correct_spelling
import numpy as np

STOP_WORDS = {"are", "there", "is", "do", "you", "have", "for", "the", "a", "an", "of", "in", "to", "and", "on", "at", "by"}

def find_closest_match(word, word_list, cutoff=0.5):
    matches = get_close_matches(word, word_list, n=1, cutoff=cutoff)
    return matches[0] if matches else word

def process_input_with_spelling_correction(input_text):
    words = input_text.split()
    corrected_words = []
    
    for word in words:
        if word.lower() in STOP_WORDS:
            corrected_words.append(word)
        else:
            corrected_words.append(correct_spelling(word))
            
    return " ".join(corrected_words).strip().lower()

def get_best_match(query):
    scores = bm25.get_scores(query.split())
    best_index = np.argmax(scores)
    return documents[best_index] if scores[best_index] > 0.5 else None