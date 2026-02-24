# Docker deployment (UI + citation image server)

This setup runs:
1. Streamlit UI (`assistant_ui_langgraph.py`)
2. A Python static web server for citation images

## Deployment settings

`deployment/docker/docker-compose.yml` expects:

1. `config_private.py` mounted to `/app/config_private.py`
2. Oracle wallet mounted to `/app/wallet_atp`
3. OCI config mounted to `/root/.oci`
4. Citation images root mounted from `/Users/lsaetta/Progetti/work-iren/pages` to `/data/citations`

Current compose settings:

```yaml
environment:
  - VECTOR_WALLET_DIR=/app/wallet_atp
  - OCI_CONFIG_FILE=/root/.oci/config
  - OCI_CLI_PROFILE=DEFAULT
  - CITATION_BASE_URL=${CITATION_BASE_URL:-http://127.0.0.1:8008/}
volumes:
  - ../../config_private.py:/app/config_private.py:ro
  - /Users/lsaetta/Progetti/work-iren/wallet:/app/wallet_atp:ro
  - ${HOME}/.oci:/root/.oci:ro
```

Citation image server compose settings:

```yaml
ports:
  - "${CITATION_SERVER_BIND_IP:-0.0.0.0}:${CITATION_SERVER_PORT:-8008}:8008"
volumes:
  - /Users/lsaetta/Progetti/work-iren/pages:/data/citations:ro
```

Important checks:

1. `config_private.py` exists in project root.
2. Wallet host path exists and contains `tnsnames.ora`, `sqlnet.ora`, wallet files.
3. `${HOME}/.oci/config` exists and the selected profile is valid.
4. In OCI config, `key_file` must resolve inside the mounted `/root/.oci/...` path in container.
5. `/Users/lsaetta/Progetti/work-iren/pages` contains citation subfolders and `pageNNNN.png` images.

## Build

Run from project root:

```bash
docker build -f deployment/docker/Dockerfile -t custom-rag-agent-ui:latest .
```

## Start (recommended: compose)

```bash
docker compose -f deployment/docker/docker-compose.yml up -d --build
```

UI URL:

```text
http://localhost:8501
```

## Stop

```bash
docker compose -f deployment/docker/docker-compose.yml down
```

## Logs

```bash
docker compose -f deployment/docker/docker-compose.yml logs -f
```

## Alternative: docker run

```bash
docker run -d \
  --name custom-rag-agent-ui \
  -p 8501:8501 \
  -e VECTOR_WALLET_DIR=/app/wallet_atp \
  -e OCI_CONFIG_FILE=/root/.oci/config \
  -e OCI_CLI_PROFILE=DEFAULT \
  -v "$(pwd)/config_private.py:/app/config_private.py:ro" \
  -v /Users/lsaetta/Progetti/work-iren/wallet:/app/wallet_atp:ro \
  -v "${HOME}/.oci:/root/.oci:ro" \
  custom-rag-agent-ui:latest
```
