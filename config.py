"""
OCI models configuration and general config
"""

DEBUG = False

AUTH = "API_KEY"
EMBED_MODEL_ID = "cohere.embed-multilingual-v3.0"
LLM_MODEL_ID = "meta.llama-3.3-70b-instruct"
SERVICE_ENDPOINT = "https://inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com"


TEMPERATURE = 0.1
MAX_TOKENS = 1024

TOP_K = 6

COLLECTION_NAME = "BOOKS"

# OCI general
COMPARTMENT_ID = "ocid1.compartment.oc1..aaaaaaaaushuwb2evpuf7rcpl4r7ugmqoe7ekmaiik3ra3m7gec3d234eknq"

# history management
MAX_MSGS_IN_HISTORY = 6

# reranking
ENABLE_RERANKER = False

# integration with APM
AGENT_NAME = "OCI_CUSTOM_RAG_AGENT"

ENABLE_TRACING = True
APM_BASE_URL = "https://aaaadec2jjn3maaaaaaaaach4e.apm-agt.eu-frankfurt-1.oci.oraclecloud.com/20200101"
APM_CONTENT_TYPE = "application/json"
APM_PUBLIC_KEY = "6OXZ45BTT5AHD5KYICGOMLXXAZYTTLGT"
