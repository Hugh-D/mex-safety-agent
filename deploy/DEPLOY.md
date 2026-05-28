# MEX Safety Platform — VPS Deployment Guide

One-time setup on DigitalOcean. Takes ~30 minutes.

---

## 1. DigitalOcean — Create resources

### Droplet
1. Go to [cloud.digitalocean.com](https://cloud.digitalocean.com) → **Create → Droplet**
2. Image: **Ubuntu 22.04 LTS**
3. Size: **Basic — 2 GB RAM / 1 vCPU** (~$12/month)
4. Region: **Sydney (syd1)**
5. Authentication: SSH key (add your public key)
6. Click **Create Droplet** — note the IP address

### Spaces (photo storage)
1. **Create → Spaces Object Storage**
2. Region: **Sydney (syd1)**
3. Name: `mex-safety-photos`
4. Enable CDN: **yes**
5. Go to **API → Spaces Keys** → Generate New Key
6. Save the **Key** and **Secret** — you won't see the secret again

### Domain
Point `cmse.mexeng.com.au` at the Droplet IP:
- Add an **A record**: `cmse` → `<droplet-ip>`
- Wait ~5 minutes for DNS to propagate

---

## 2. Server setup

SSH into the Droplet:
```bash
ssh root@<droplet-ip>
```

Install Docker:
```bash
apt update && apt upgrade -y
apt install -y docker.io docker-compose-plugin git
systemctl enable docker
```

Clone the repo:
```bash
git clone https://github.com/Hugh-D/mex-safety-agent.git /opt/mex
cd /opt/mex
```

---

## 3. Configure environment

```bash
cp api/.env.example api/.env
nano api/.env
```

Fill in all values:
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
API_KEYS=mex-hugh-2026,mex-eion-2026,mex-jie-2026,mex-sam-2026,mex-russell-2026
SPACES_KEY=<your-spaces-key>
SPACES_SECRET=<your-spaces-secret>
SPACES_BUCKET=mex-safety-photos
SPACES_REGION=syd1
SPACES_ENDPOINT=https://syd1.digitaloceanspaces.com
CORS_ORIGINS=https://cmse.mexeng.com.au
```

---

## 4. SSL certificate (first time only)

Start Nginx in HTTP-only mode first so certbot can verify the domain.

Edit `deploy/nginx.conf` — comment out the entire `server { listen 443 ... }` block temporarily, then:

```bash
docker compose up -d nginx certbot

docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d cmse.mexeng.com.au \
  --email hugh@mexeng.com.au \
  --agree-tos --no-eff-email
```

Restore the full `nginx.conf`, then restart:
```bash
docker compose restart nginx
```

---

## 5. Launch

```bash
cd /opt/mex
docker compose up -d --build
```

Check all containers are running:
```bash
docker compose ps
```

Open `https://cmse.mexeng.com.au` — you should see the key entry screen.

---

## 6. Updates (future deploys)

```bash
cd /opt/mex
git pull
docker compose up -d --build
```

---

## Useful commands

```bash
# View live logs
docker compose logs -f api

# Restart just the API
docker compose restart api

# Check disk usage
df -h
```

---

## Costs summary

| Resource | Cost |
|---|---|
| Droplet (2GB, syd1) | ~$12 USD/month |
| Spaces (250 GB) | ~$5 USD/month |
| **Total** | **~$17 USD/month** |
