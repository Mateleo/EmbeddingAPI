from sentence_transformers import SentenceTransformer

model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1');
model.save_pretrained('./app/model_data')