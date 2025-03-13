from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
from entity_fetch import makers_list, models_list, variants_list, years_list, fuel_type_list, category_list, sub_category_list

def generate_misspellings(word):
    misspellings = set()
    
    if len(word) > 2:
        misspellings.add(word[:-1])  # Dropping last letter
        misspellings.add(word[1:])  # Dropping first letter
        
        for i in range(len(word) - 1):
            swapped = word[:i] + word[i+1] + word[i] + word[i+2:]
            misspellings.add(swapped)

    qwerty_errors = {'a': 'qwsz', 's': 'awedxz', 'd': 'serfcx', 'f': 'drtgvc', 'b': 'vghn'}
    for i, char in enumerate(word):
        if char in qwerty_errors:
            for typo in qwerty_errors[char]:
                misspellings.add(word[:i] + typo + word[i+1:])
    
    return list(misspellings)

# Step 2: Prepare Training Data
correct_words = (
    makers_list + models_list + variants_list + 
    [str(year) for year in years_list] +  
    fuel_type_list + category_list + sub_category_list
)

misspelled_pairs = []

for word in correct_words:
    misspelled = generate_misspellings(word)
    for wrong in misspelled:
        misspelled_pairs.append((wrong, word))

# Step 3: Train the Model
X_train, y_train = zip(*misspelled_pairs)
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
X_train_tfidf = vectorizer.fit_transform(X_train)

knn = KNeighborsClassifier(n_neighbors=3, metric='cosine')
knn.fit(X_train_tfidf, y_train)

# Function to correct spelling
def correct_spelling(word):
    word_tfidf = vectorizer.transform([word])
    prediction = knn.predict(word_tfidf)[0]
    return prediction

# **Export model components for other files**
__all__ = ["correct_spelling"]  # Exports only this function