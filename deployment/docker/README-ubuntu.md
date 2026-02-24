# Docker Deployment on Ubuntu

This guide explains how to run this project on Ubuntu with Docker Compose, including:
1. Streamlit app
2. Citation image server
3. Nginx reverse proxy with Basic Auth

## 1) Prerequisites

Install Docker and Compose plugin:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Optional: run Docker without `sudo`:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

## 2) Clone project and prepare files

```bash
git clone <YOUR_REPO_URL> custom_rag_agent
cd custom_rag_agent
```

Create private config:

```bash
cp config_private_template.py config_private.py
```

Then edit `config_private.py` with your DB credentials and DSN.

## 3) Update host paths in compose for Ubuntu

The current compose file contains host paths from macOS.  
Before starting on Ubuntu, update these mounts in [docker-compose.yml](./docker-compose.yml):

1. Wallet path:
   - from: `/Users/lsaetta/Progetti/work-iren/wallet`
   - to: your Ubuntu absolute path (example: `/home/ubuntu/work-iren/wallet`)
2. Citation images root:
   - from: `/Users/lsaetta/Progetti/work-iren/pages`
   - to: your Ubuntu absolute path (example: `/home/ubuntu/work-iren/pages`)

Keep these mounts unchanged:
1. `../../config_private.py:/app/config_private.py:ro`
2. `${HOME}/.oci:/root/.oci:ro`

## 4) OCI configuration on Ubuntu host

Ensure OCI files are available on host:

```text
${HOME}/.oci/config
${HOME}/.oci/<private_key_file>
```

In `${HOME}/.oci/config`, verify:
1. profile exists (`[DEFAULT]` unless you changed compose)
2. `key_file` points to a file inside `${HOME}/.oci`
3. tenancy, user, fingerprint, region are valid

## 5) Prepare citation directory structure

Expected structure:

```text
<citation_root>/<document_name_without_pdf>/page0001.png
```

Example:

```text
/home/ubuntu/work-iren/pages/MyDoc/page0007.png
```

## 6) Configure Basic Auth users (Nginx)

Create password file on host:

```bash
mkdir -p deployment/docker/nginx
```

Option A (native Ubuntu tool):

```bash
sudo apt-get update && sudo apt-get install -y apache2-utils
htpasswd -Bbc deployment/docker/nginx/.htpasswd user1
htpasswd -Bb deployment/docker/nginx/.htpasswd user2
```

Option B (no host package, Docker-only):

```bash
docker run --rm --entrypoint htpasswd httpd:2.4-alpine -Bbn user1 'password1' > deployment/docker/nginx/.htpasswd
docker run --rm --entrypoint htpasswd httpd:2.4-alpine -Bbn user2 'password2' >> deployment/docker/nginx/.htpasswd
```

## 7) Build and start

From project root:

```bash
docker compose -f deployment/docker/docker-compose.yml up -d --build
```

Check status:

```bash
docker compose -f deployment/docker/docker-compose.yml ps
```

Follow logs:

```bash
docker compose -f deployment/docker/docker-compose.yml logs -f
```

## 8) Network and firewall

By default:
1. UI is exposed through Nginx on `8501/tcp`
2. Citation server is exposed on `8008/tcp` (if kept enabled in compose)

If using UFW:

```bash
sudo iptables -I INPUT -p tcp -s 0.0.0.0/0 --dport 8501 -j ACCEPT
sudo iptables -I INPUT -p tcp -s 0.0.0.0/0 --dport 8008 -j ACCEPT
sudo service netfilter-persistent save
```

If you want citation server private, remove its `ports:` mapping from compose and keep only internal access.

## 9) Validation checklist

1. Open `http://<UBUNTU_HOST_IP>:8501`
2. Nginx prompts for username/password
3. After login, Streamlit UI loads
4. Citation image links open correctly
5. `docker compose ... ps` shows all services as `Up`

## 10) Common issues

1. `.htpasswd is a directory`
   - fix:
   ```bash
   rm -rf deployment/docker/nginx/.htpasswd
   ```
   then recreate as a file
2. OCI auth failures
   - check `${HOME}/.oci/config` and key path mapping
3. Wallet/DB connection errors
   - verify wallet mount path in compose and files in wallet directory
4. 502 from Nginx
   - check app logs:
   ```bash
   docker compose -f deployment/docker/docker-compose.yml logs -f nginx_streamlit custom-rag-agent-ui
   ```

## 11) Stop and cleanup

Stop stack:

```bash
docker compose -f deployment/docker/docker-compose.yml down
```

Stop and remove images too:

```bash
docker compose -f deployment/docker/docker-compose.yml down --rmi local
```
