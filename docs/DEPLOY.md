# Deploy em Produção (VPS)

## Pré-requisitos

- VPS com Ubuntu 22.04+
- Docker e Docker Compose instalados
- Domínio apontando para o IP do servidor
- Portas 80 e 443 abertas

## Passos

### 1. Clone e configure

```bash
git clone https://github.com/seu-usuario/eventos-culturais-rss.git
cd eventos-culturais-rss
./scripts/setup.sh
```

### 2. Obtenha certificado SSL (Let's Encrypt)

```bash
# Instale o certbot
sudo apt install certbot

# Gere o certificado (com nginx parado)
sudo certbot certonly --standalone -d seudominio.com.br

# Copie os certificados
mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/seudominio.com.br/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/seudominio.com.br/privkey.pem nginx/ssl/
sudo chown $USER nginx/ssl/*.pem
```

### 3. Suba com config de produção

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4. Renovação automática do SSL

```bash
# Adicione ao crontab:
0 0 1 * * certbot renew --quiet && \
  cp /etc/letsencrypt/live/seudominio.com.br/*.pem /path/to/app/nginx/ssl/ && \
  docker compose restart nginx
```
