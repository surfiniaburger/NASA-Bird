from gensim import corpora
from gensim.models import LdaModel
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string

# Load the dataset
with open(r'C:\Users\CCL\Downloads\mars.txt', 'r', encoding='utf-8') as file:

    documents = file.readlines()

# Tokenize, remove stopwords, and stem
stop_words = set(stopwords.words('english'))
porter = PorterStemmer()

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [porter.stem(token) for token in tokens if token.isalpha() and token not in stop_words]
    return tokens

# Preprocess all documents
processed_documents = [preprocess_text(doc) for doc in documents]

# Create a dictionary representation of the documents
dictionary = corpora.Dictionary(processed_documents)

# Create a bag-of-words representation of the documents
corpus = [dictionary.doc2bow(doc) for doc in processed_documents]

# Train the LDA model
num_topics = 5  # Adjust based on your dataset
lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)
lda_model.save('lda_model')

# Save the dictionary
dictionary.save('dictionary')

print(dictionary)