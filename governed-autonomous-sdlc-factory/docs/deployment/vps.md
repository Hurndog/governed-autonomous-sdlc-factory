# VPS Deployment Guide

## Prerequisites

- Ubuntu 22.04+ or Debian 12+ VPS
- 4+ CPU cores, 8GB+ RAM, 20GB+ disk
- SSH access with sudo privileges
- A domain name pointed at your VPS IP (optional, for SSL)

## Initial Server Setup

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Create a non-root user
adduser deploy
usermod -aG sudo deploy

# Set up basic firewall
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Switch to deploy user
su - deploy
```

## Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Verify
docker --version
docker compose version
```

## Deploy Application

```bash
# Clone repository
git clone https://github.com/your-org/governed-autonomous-sdlc-factory.git
cd governed-autonomous-sdlc-factory

# Configure environment
cp .env.example .env
nano .env
# Set production values:
# - DATABASE_URL with strong password
# - API_SECRET with random string
# - OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.
# - NEXT_PUBLIC_API_URL=https://your-domain.com
# - NEXT_PUBLIC_WS_URL=wss://your-domain.com

# Launch
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run migrations
docker compose exec api python -m alembic upgrade head

# Verify
docker compose ps
```

## Set Up Nginx Reverse Proxy

```bash
sudo apt install nginx -y

# Create nginx config
sudo tee /etc/nginx/sites-available/sdlc-factory << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # SSE
    location /api/v1/operations/events/stream {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding on;
    }
}
EOF

# Enable config
sudo ln -s /etc/nginx/sites-available/sdlc-factory /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Set Up SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
# Test renewal
sudo certbot renew --dry-run
```

## Set Up Automated Backups

```bash
# Create backup script
cat > ~/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/backups/$DATE
mkdir -p $BACKUP_DIR

# Database backup
docker compose exec -T postgres pg_dump -U governance sdlc_factory > $BACKUP_DIR/db.sql

# Keep only last 7 backups
ls -td ~/backups/* | tail -n +8 | xargs rm -rf
EOF

chmod +x ~/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup.sh") | crontab -
```

## Monitoring

```bash
# Install fail2ban
sudo apt install fail2ban -y

# Monitor logs
docker compose logs -f api

# Check disk usage
df -h

# Check memory
free -h

# Check Docker resources
docker stats
```

## Updating

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose build
docker compose up -d

# Run migrations
docker compose exec api python -m alembic upgrade head
```
