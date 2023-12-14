from sklearn.feature_extraction.text import CountVectorizer

def create_vectorizer(max_df=0.95, min_df=2):
    return CountVectorizer(max_df=max_df, min_df=min_df, stop_words='english')
