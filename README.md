# Custom RAG agent
This repository contains all the code for the development of a **custom RAG Agent**, based on OCI Generative AI, 23AI and **LangGraph**

## Design and implementation
* The agent is implemented using **LangGraph**
* Vector Search is implemented, using Langchain, on top of Oracle 23AI

Design decisions:
* for every node of the graph there is a dedicated Python class (a **Runnable**)
* Reranker is implemented using a LLM (wip). Easy to plug, for example, Cohere reranker
* the agent is integrated with **OCI APM**, for **Observability**; Integration using **py-zipkin**
* UI implemented with **Streamlit**

Support for streaming events from the agent: as soon as a step is completed (Vector Search, Reranking, ...) the UI is updated.
For example links to the documentation' chunks are displayed before the final answer.

## Status
It is a PoC. Some steps need to be done to clean the agent (trasnform all the functions in Python classes). It is wip.

## References
[Integration with OCI APM](https://luigi-saetta.medium.com/enhancing-observability-in-rag-solutions-with-oracle-cloud-6f93b2675f40)