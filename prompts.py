"""
Prompts

all the used prompts are here
"""

REFORMULATE_PROMPT_TEMPLATE = """
You're an AI assistant. Given a user request and a chat history reformulate the user question 
in a standalone question using the chat history.

Constraints:
- return only the standalone question, do not add any other text.

User request: {user_request}
Chat history: {chat_history}

Standalone question: 
"""

ANSWER_PROMPT_TEMPLATE = """
You're an AI assistant. Your task is to answer to user questions based on the provided context
and the history of previous messages.
Use always a friendly but polite tone.

## Constraints:
- Answer always in the language of the user question.
- Answer based only on the provided context. If you don't know the answer, say simply **I don't know the answer.**,
  but always use the language of the user question.
- Return the answer using always properly formatted markdown.

Context: {context}

"""

RERANKER_TEMPLATE = """
You are an intelligent ranking assistant. Your task is to rank and filter text chunks 
based on their relevance to a given user query. You will receive:

1. A user query.
2. A list of text chunks.

Your goal is to:
- Rank the text chunks in order of relevance to the user query.
- Remove any text chunks that are completely irrelevant to the query.

### Instructions:
- Assign a **relevance score** to each chunk based on how well it answers or relates to the query.
- Return only the **top-ranked** chunks, filtering out those that are completely irrelevant.
- The output should be a **sorted list** of relevant chunks, from most to least relevant.
- Return only the JSON, don't add other text.
- Don't return the text of the chunk, only the index and the score.

### Input Format:
User Query:
{query}

Text Chunks (list indexed from 0):
{chunks}

### **Output Format:**
Return a **JSON object** with the following format:
```json
{{
  "ranked_chunks": [
    {{"index": 0, "score": X.X}},
    {{"index": 2, "score": Y.Y}},
    ...
  ]
}}
```
Where:
- "index" is the original position of the chunk in the input list.
- "text" is the content of the relevant chunk.
- "score" is the relevance score (higher is better).

Ensure that only relevant chunks are included in the output. If no chunk is relevant, return an empty list.

"""

RERANKER_TEMPLATE_OLD = """
You are an intelligent ranking assistant. Your task is to rank and filter text chunks 
based on their relevance to a given user query. You will receive:

1. A user query.
2. A list of text chunks.

Your goal is to:
- Rank the text chunks in order of relevance to the user query.
- Remove any text chunks that are completely irrelevant to the query.

### Instructions:
- Assign a **relevance score** to each chunk based on how well it answers or relates to the query.
- Return only the **top-ranked** chunks, filtering out those that are completely irrelevant.
- The output should be a **sorted list** of relevant chunks, from most to least relevant.
- Return only the JSON, don't add other text.

### Input Format:
User Query:
{user_request}

Text Chunks (list indexed from 0):
{chunks}

### **Output Format:**
Return a **JSON object** with the following format:
```json
{{
  "ranked_chunks": [
    {{"index": 0, "text": "Relevant chunk 1", "score": X.X}},
    {{"index": 2, "text": "Relevant chunk 2", "score": Y.Y}},
    ...
  ]
}}
```
Where:
- "index" is the original position of the chunk in the input list.
- "text" is the content of the relevant chunk.
- "score" is the relevance score (higher is better).

Ensure that only relevant chunks are included in the output. If no chunk is relevant, return an empty list.

"""
