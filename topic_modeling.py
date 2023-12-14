from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.decomposition import LatentDirichletAllocation
from preprocess_content import preprocess_content

# def create_vectorizer(max_df=0.95, min_df=2):
#     return CountVectorizer(max_df=max_df, min_df=min_df, stop_words='english')

# def generate_lda_model(educational_content, vectorizer=None):
#     """
#     Generate an LDA (Latent Dirichlet Allocation) model based on the given educational content.

#     Parameters:
#     - educational_content (list): A list of educational documents or content.

#     Returns:
#     - lda_model (LatentDirichletAllocation): Trained LDA model.
#     """
#     if vectorizer is None:
#         vectorizer = create_vectorizer()

#     # Preprocess the educational content if needed
#     processed_content = preprocess_content(educational_content)

#     # Flatten the list if it's a list of lists
#     if any(isinstance(doc, list) for doc in processed_content):
#         processed_content = [item for sublist in processed_content for item in sublist]

#     # Calculate max_df dynamically based on the number of documents
#     max_df = 0.95 if len(processed_content) > 10 else 1.0

#     vectorizer.set_params(max_df=max_df)
#     X = vectorizer.fit_transform(processed_content)

#     # Apply LDA
#     num_topics = 5  # You can adjust this based on your needs
#     lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
#     lda.fit(X)

#     return lda, vectorizer


# # topic_modeling.py
# import torch
# from transformers import BertTokenizer, BertModel
# from torchtext import data
# import torch.nn.functional as F

# class LDA(torch.nn.Module):
#     def __init__(self, num_topics, num_words, hidden_size=768):
#         super(LDA, self).__init__()
#         self.bert_model = BertModel.from_pretrained('bert-base-uncased')
#         self.hidden2topic = torch.nn.Linear(hidden_size, num_topics)
#         self.topic2word = torch.nn.Linear(num_topics, num_words)

#     def forward(self, input_ids, attention_mask):
#         bert_output = self.bert_model(input_ids, attention_mask=attention_mask)['last_hidden_state'][:, 0, :]
#         topic_dist = F.softmax(self.hidden2topic(bert_output), dim=1)
#         word_dist = F.softmax(self.topic2word(topic_dist), dim=1)
#         return topic_dist, word_dist

# def generate_lda_model(educational_content, tokenizer, num_topics=5, num_words=10):
#     processed_content = preprocess_content(educational_content, tokenizer)
#     fields = [('text', data.Field(sequential=True, tokenize=tokenizer.tokenize))]
#     examples = [data.Example.fromlist([doc], fields) for doc in processed_content]
#     dataset = data.Dataset(examples, fields)

#     TEXT = data.Field(sequential=True, tokenize=tokenizer.tokenize)
#     BATCH_SIZE = 64
#     device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#     train_iterator, _ = data.BucketIterator.splits(
#         (dataset, dataset),
#         sort=False,
#         batch_size=BATCH_SIZE,
#         device=device
#     )

#     model = LDA(num_topics=num_topics, num_words=num_words).to(device)
#     optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)

#     for epoch in range(5):  # You can adjust the number of epochs
#         for batch in train_iterator:
#             input_ids = batch.text[0]
#             attention_mask = (input_ids != 1)  # Attention mask excluding padding tokens
#             target_topic_dist, target_word_dist = model(input_ids, attention_mask)

#             loss = torch.nn.KLDivLoss()(target_word_dist.log(), target_topic_dist)
#             optimizer.zero_grad()
#             loss.backward()
#             optimizer.step()

#     return model

# def extract_topics(lda_model, tokenizer, num_words=10):
#     topics = []

#     for topic_idx in range(lda_model.hidden2topic.out_features):
#         topic = lda_model.hidden2topic.weight[topic_idx]
#         top_word_indices = torch.topk(topic, num_words).indices.tolist()

#         # Convert word indices back to words using the tokenizer's vocabulary
#         top_words = [tokenizer.convert_ids_to_tokens(idx) for idx in top_word_indices]

#         topics.append({
#             'topic_idx': topic_idx + 1,
#             'top_words': top_words
#         })

#     return topics

# def preprocess_content(content, tokenizer):
#     return [tokenizer.tokenize(doc) for doc in content]


# topic_modeling.py
import torch
from transformers import BertTokenizer, BertModel
from sklearn.feature_extraction.text import CountVectorizer
from vectorizer import create_vectorizer

class TransformerLDA(torch.nn.Module):
    def __init__(self, num_topics, num_words):
        super(TransformerLDA, self).__init__()
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.count_vectorizer = CountVectorizer()

    def forward(self, x):
        input_ids = self.tokenizer(x, return_tensors='pt', padding=True, truncation=True)['input_ids']
        with torch.no_grad():
            outputs = self.bert_model(input_ids)
        return outputs.last_hidden_state.mean(dim=1)

def generate_lda_model(educational_content, vectorizer=None):
    if vectorizer is None:
        vectorizer = create_vectorizer()

    processed_content = preprocess_content(educational_content, vectorizer.get_feature_names_out())
    if any(isinstance(doc, list) for doc in processed_content):
        processed_content = [item for sublist in processed_content for item in sublist]

    X = vectorizer.fit_transform(processed_content)
    num_topics = 5

    X = torch.tensor(X.toarray(), dtype=torch.float32)

    num_words = X.shape[1]
    model = TransformerLDA(num_topics, num_words)

    return model, vectorizer

def extract_topics(lda_model, vectorizer, num_top_words=10):
    feature_names = vectorizer.get_feature_names_out()

    topics = []

    with torch.no_grad():
        outputs = lda_model(processed_content)
        beta = outputs.last_hidden_state.mean(dim=1).numpy()

    for topic_idx in range(lda_model.num_topics):
        top_word_indices = beta[:, topic_idx].argsort()[:-num_top_words - 1:-1]
        top_words = [feature_names[i] for i in top_word_indices]

        topics.append({
            'topic_idx': topic_idx + 1,
            'top_words': top_words
        })

    return topics
