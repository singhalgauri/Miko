# Deploying Miko on Nebius AI Cloud

> Owner: Person 4  
> Purpose: Production deployment guide for hosting the public Miko demo on a Nebius AI Cloud VM behind HTTPS  
> TODO(person4): Automate Terraform / Ansible provisioning script

---

## 1. Nebius AI Cloud VM Setup

1. **Provision Compute Instance:**
   - In the Nebius console, provision a standard Ubuntu 22.04 LTS VM (e.g., 4 vCPU, 16 GB RAM).
   - Ensure an external static public IP is attached.
   - Open security group ports: `22` (SSH), `80` (HTTP), `443` (HTTPS).

2. **Install Docker & Docker Compose:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y ca-certificates curl gnupg
   # Follow standard Docker CE installation for Ubuntu
   sudo apt-get install -y docker-ce docker-compose-plugin
   ```

3. **Clone Repository & Configure Environment:**
   ```bash
   git clone https://github.com/miko-ai/miko.git /opt/miko
   cd /opt/miko
   cp .env.example .env
   # Set your Nebius Token Factory API key in .env
   ```

---

## 2. Setting Up HTTPS Reverse Proxy (Caddy / Nginx)

Use Caddy for automatic Let's Encrypt TLS:
```Caddyfile
demo.miko.ai {
    reverse_proxy 127.0.0.1:8000
}
```

---

## 3. Rate Limiting Note

> [!WARNING]
> Because this instance powers the public hackathon demo without user authentication, configure rate limiting on the reverse proxy to prevent abuse or rapid exhaustion of Token Factory credits.
>
> **Recommended Limit:** 30 requests/minute per IP address on `/api/agents/*/run`.

---

## 4. Launching the Service
```bash
docker compose -f deploy/docker-compose.yml up -d --build
```
Verify logs:
```bash
docker compose -f deploy/docker-compose.yml logs -f
```
