#!/bin/bash

# script to start the MCP server in stdio, to integrate locally with Claude
# modify the path to align to your environment

# Source conda to make the `conda` command available
source $HOME/miniforge3/etc/profile.d/conda.sh

# Activate the desired conda environment
conda activate custom_rag_agent

# Run the Python script
python $HOME/Progetti/custom_rag_agent/mcp_semantic_search_stdio.py