from flask import Flask, render_template, request
from gensim.models.ldamodel import LdaModel
from gensim.corpora.dictionary import Dictionary

app = Flask(__name__)

# Load the trained Gensim LDA model and dictionary
model = LdaModel.load('lda_model')
dictionary = Dictionary.load('dictionary')

def is_related_to_mars_rovers(text):
    # Preprocess the input text and convert it to a bag-of-words representation
    bow_vector = dictionary.doc2bow(text.lower().split())

    # Get the topic distribution for the input text
    topic_distribution = model[bow_vector]

    # Check if there is a significant topic related to Mars rovers
    for topic, score in topic_distribution:
        if score > 0.9:  # Adjust the threshold based on your model
            return True

    return False, None

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None

    if request.method == 'POST':
        content = request.form['content']

        # Check if the provided content is related to Mars rovers
        result = is_related_to_mars_rovers(content)

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
