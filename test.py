import os
import openai
openai.api_key = "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"
openai.proxy = 'http://127.0.0.1:7000'
model = openai.Embedding
x = model.create(
  model="text-embedding-ada-002",
  input="The food was delicious and the waiter..."
)
print(x["data"][0]["embedding"])