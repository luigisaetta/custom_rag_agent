#!/bin/bash

# Source conda to make the `conda` command available
source /Users/lsaetta/miniforge3/etc/profile.d/conda.sh

# Activate the desired environment
conda activate custom_rag_agent

# Run the Python script
python $HOME/Progetti/custom_rag_agent/mcp_semantic_search_stdio.py


