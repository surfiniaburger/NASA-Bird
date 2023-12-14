

def extract_topics(lda_model, vectorizer, num_top_words=10):
    # Get the feature names from the vectorizer
    feature_names = vectorizer.get_feature_names_out()

    topics = []

    # Iterate through the components to extract topics
    for topic_idx, topic in enumerate(lda_model.components_):
        # Get the indices of the top words for the current topic
        top_word_indices = topic.argsort()[:-num_top_words - 1:-1]

        # Get the actual words for the top indices
        top_words = [feature_names[i] for i in top_word_indices]

        # Append the topic to the list
        topics.append({
            'topic_idx': topic_idx + 1,
            'top_words': top_words
        })

    return topics
