
def generate_insights_for_topic(topic):
    top_words = topic['top_words']
    insights = []

    # Check for Mars rover-related keywords
    if any(keyword in top_words for keyword in ['rover', 'Mars', 'NASA', 'perseverance']):
        insights.append("This topic is related to NASA's Mars rover missions and Perseverance.")

    # Custom condition: Check for focus on science and technology
    if 'science' in top_words and 'technology' in top_words:
        insights.append(f"Topic {topic['topic_idx']}: Focus on the intersection of science and technology.")

    # Custom condition: Check for trends related to students
    if 'students' in top_words or 'education' in top_words:
        insights.append(f"Topic {topic['topic_idx']}: Trends in science and technology education for students.")


    return insights

def generate_insights(topics):
    all_insights = []

    for topic in topics:
        insights_for_topic = generate_insights_for_topic(topic)
        all_insights.extend(insights_for_topic)

    return {'insights': all_insights}
