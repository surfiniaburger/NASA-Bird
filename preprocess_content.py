import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

nltk.download('stopwords')
nltk.download('punkt')

def preprocess_content(content):
    """
    Preprocess the educational content using NLTK.

    Parameters:
    - content (list): A list of educational documents or content, which can be strings or lists of strings.

    Returns:
    - processed_content (list): Preprocessed educational content as a list of strings.
    """
    # If content is already a list of strings, return it
    if all(isinstance(doc, str) for doc in content):
        return content

    # Otherwise, flatten the list of lists and preprocess
    flat_content = [item for sublist in content for item in sublist]

    # Tokenize, remove stop words, and perform stemming
    processed_content = []
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()

    for doc in flat_content:
        words = word_tokenize(doc)
        filtered_words = [word for word in words if word.lower() not in stop_words]
        stemmed_words = [stemmer.stem(word) for word in filtered_words]
        processed_content.append(' '.join(stemmed_words))

    return processed_content
