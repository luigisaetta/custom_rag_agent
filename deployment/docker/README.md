# Docker deployment (UI + Citation Image Server + Nginx)

For Ubuntu-specific setup, see [README-ubuntu.md](./README-ubuntu.md).

This setup runs:
1. Streamlit UI (`assistant_ui_langgraph.py`)
2. A Python static web server for citation images
3. Nginx reverse proxy in front of Streamlit

## Deployment settings

`deployment/docker/docker-compose.yml` configures:

1. `config_private.py` mounted to `/app/config_private.py`
2. Oracle wallet mounted to `/app/wallet_atp`
3. OCI config mounted to `/root/.oci`
4. Citation image root mounted from `/Users/lsaetta/Progetti/work-iren/pages` to `/data/citations`

Current UI service settings:

```yaml
environment:
  - VECTOR_WALLET_DIR=/app/wallet_atp
  - OCI_CONFIG_FILE=/root/.oci/config
  - OCI_CLI_PROFILE=DEFAULT
  - CITATION_BASE_URL=${CITATION_BASE_URL:-http://127.0.0.1:8008/}
expose:
  - "8501"
volumes:
  - ../../config_private.py:/app/config_private.py:ro
  - /Users/lsaetta/Progetti/work-iren/wallet:/app/wallet_atp:ro
  - ${HOME}/.oci:/root/.oci:ro
```

Citation image server settings:

```yaml
ports:
  - "${CITATION_SERVER_BIND_IP:-0.0.0.0}:${CITATION_SERVER_PORT:-8008}:8008"
volumes:
  - /Users/lsaetta/Progetti/work-iren/pages:/data/citations:ro
```

Nginx reverse proxy settings:

```yaml
ports:
  - "8501:80"
volumes:
  - ./nginx/streamlit.conf:/etc/nginx/conf.d/default.conf:ro
  - ./nginx/.htpasswd:/etc/nginx/.htpasswd:ro
```

## Basic Auth setup (Nginx)

Create the password file on the host at:

```text
deployment/docker/nginx/.htpasswd
```

Cross-platform (works on macOS and Linux, requires Docker):

```bash
mkdir -p deployment/docker/nginx
docker run --rm --entrypoint htpasswd httpd:2.4-alpine -Bbn user1 'password1' > deployment/docker/nginx/.htpasswd
docker run --rm --entrypoint htpasswd httpd:2.4-alpine -Bbn user2 'password2' >> deployment/docker/nginx/.htpasswd
```

Native commands (optional):

macOS (Homebrew):

```bash
brew install httpd
mkdir -p deployment/docker/nginx
htpasswd -Bbc deployment/docker/nginx/.htpasswd user1
htpasswd -Bb deployment/docker/nginx/.htpasswd user2
```

Linux (Debian/Ubuntu):

```bash
sudo apt-get update && sudo apt-get install -y apache2-utils
mkdir -p deployment/docker/nginx
htpasswd -Bbc deployment/docker/nginx/.htpasswd user1
htpasswd -Bb deployment/docker/nginx/.htpasswd user2
```

After creating/updating users:

```bash
docker compose -f deployment/docker/docker-compose.yml up -d
docker compose -f deployment/docker/docker-compose.yml restart nginx_streamlit
```

Important checks:

1. `config_private.py` exists in project root.
2. Wallet host path exists and contains `tnsnames.ora`, `sqlnet.ora`, wallet files.
3. `${HOME}/.oci/config` exists and the selected profile is valid.
4. In OCI config, `key_file` must resolve inside the mounted `/root/.oci/...` path in container.
5. `/Users/lsaetta/Progetti/work-iren/pages` contains citation subfolders and `pageNNNN.png` files.
6. `deployment/docker/nginx/.htpasswd` exists before starting Nginx.

## Build

Run from the project root:

```bash
docker build -f deployment/docker/Dockerfile -t custom-rag-agent-ui:latest .
```

## Start (Recommended: Compose)

```bash
docker compose -f deployment/docker/docker-compose.yml up -d --build
```

UI URL (through Nginx):

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

## Alternative: docker run (UI only, no Nginx)

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
