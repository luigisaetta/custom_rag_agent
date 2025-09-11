"""
Streamlit UI for MCP servers
"""

import asyncio
import streamlit as st
from mcp_servers_config import MCP_SERVERS_CONFIG

# this one contains the test code only for console
from llm_with_mcp import AgentWithMCP, default_jwt_supplier

# ---------- Page setup ----------
st.set_page_config(page_title="MCP UI", page_icon="🛠️", layout="wide")
st.title("🛠️ LLM powered by MCP")

# ---------- Sidebar: connection settings ----------
with st.sidebar:
    st.header("Connection")
    mcp_url = st.text_input(
        "MCP URL", value=MCP_SERVERS_CONFIG["oci-semantic-search"]["url"]
    )
    model_id = st.selectbox("Model", ["cohere.command-a-03-2025"], index=0)
    timeout = st.number_input(
        "Timeout (s)", min_value=5, max_value=300, value=60, step=5
    )

    st.caption("JWT will be fetched on each call via default_jwt_supplier()")
    connect = st.button("🔌 Connect / Reload tools", use_container_width=True)

# ---------- Session state ----------
if "agent" not in st.session_state:
    st.session_state.agent = None
if "chat" not in st.session_state:
    # list of {"role": "user"|"assistant", "content": str}
    st.session_state.chat = []

# ---------- Connect / reload ----------
if connect:
    with st.spinner("Connecting to MCP and loading tools…"):
        try:
            # Create an agent (async factory) and cache it in session_state
            st.session_state.agent = asyncio.run(
                AgentWithMCP.create(
                    mcp_url=mcp_url,
                    jwt_supplier=default_jwt_supplier,  # returns a fresh raw JWT
                    timeout=timeout,
                    model_id=model_id,
                )
            )
            st.success("Connected. Tools loaded.")
        except Exception as e:
            st.session_state.agent = None
            st.error(f"Failed to connect: {e}")

# ---------- Chat history (display) ----------
for msg in st.session_state.chat:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.write(msg["content"])

# ---------- Input box ----------
prompt = st.chat_input("Ask your question…")  # one per page; lives at the bottom

if prompt:
    # Show the user message immediately
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    if st.session_state.agent is None:
        st.warning(
            "Not connected. Click ‘Connect / Reload tools’ in the sidebar first."
        )
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking with MCP tools…"):
                try:
                    answer = asyncio.run(st.session_state.agent.answer(prompt))
                except Exception as e:
                    answer = f"Error: {e}"
                st.write(answer)
                st.session_state.chat.append({"role": "assistant", "content": answer})

# ---------- Optional: small debug panel ----------
with st.expander("🔎 Debug / State"):
    st.json(
        {
            "connected": st.session_state.agent is not None,
            "messages_in_memory": len(st.session_state.chat),
            "mcp_url": mcp_url,
            "model_id": model_id,
            "timeout": timeout,
        }
    )
