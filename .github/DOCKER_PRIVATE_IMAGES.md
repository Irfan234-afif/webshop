# GitHub Actions - Pull Private Docker Images

## Problem

GitHub Actions tidak bisa pull private Docker images tanpa authentication.

**Error tanpa login:**

```
Error response from daemon: pull access denied for irfan33/koperasi-webshop, repository does not exist or may require 'docker login'
```

---

## Solution: Login di Workflow

### Method 1: Using docker/login-action (Recommended)

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: irfan33 # or use secret: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}

- name: Pull private image
  run: docker pull irfan33/koperasi-webshop:latest
```

### Method 2: Using docker login command

```yaml
- name: Login to Docker Hub
  run: |
    echo "${{ secrets.DOCKERHUB_TOKEN }}" | docker login -u irfan33 --password-stdin

- name: Pull private image
  run: docker pull irfan33/koperasi-webshop:latest
```

---

## Complete Workflow Examples

### Example 1: Testing with Private Image

```yaml
name: Test with Private Image

on:
  pull_request:
  push:
    branches: [main, dev]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      # Login to pull private image
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: irfan33
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # Pull image
      - name: Pull latest image
        run: docker pull irfan33/koperasi-webshop:latest

      # Run tests
      - name: Run integration tests
        run: |
          docker run --rm irfan33/koperasi-webshop:latest bench --version
          docker run --rm irfan33/koperasi-webshop:latest bench doctor
```

### Example 2: Deploy to Server

```yaml
name: Deploy to Production

on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options:
          - production
          - staging

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}

    steps:
      - uses: actions/checkout@v4

      # Setup SSH for server access
      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh-keyscan -H ${{ secrets.SERVER_HOST }} >> ~/.ssh/known_hosts

      # Deploy: SSH to server and pull private image
      - name: Deploy to server
        run: |
          ssh -i ~/.ssh/deploy_key ${{ secrets.SERVER_USER }}@${{ secrets.SERVER_HOST }} << 'ENDSSH'
            # Login on remote server
            echo "${{ secrets.DOCKERHUB_TOKEN }}" | docker login -u irfan33 --password-stdin
            
            # Navigate to app directory
            cd /opt/webshop
            
            # Update docker-compose.yml if needed
            # Pull latest private image
            docker-compose pull
            
            # Restart services
            docker-compose up -d --no-deps backend
            
            # Verify
            docker-compose ps
          ENDSSH
```

### Example 3: Build Dependent Image

If you have another image that uses your private image as base:

```yaml
# Dockerfile
FROM irfan33/koperasi-webshop:latest
# ... custom additions
```

```yaml
name: Build Custom Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      # MUST login before building (to pull base image)
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: irfan33
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # Now can build (will pull private base image)
      - name: Build custom image
        run: |
          docker build -t irfan33/custom-webshop:latest .
          docker push irfan33/custom-webshop:latest
```

---

## Required Secrets

All workflows that need to pull private images require:

| Secret Name       | Value                            |
| ----------------- | -------------------------------- |
| `DOCKERHUB_TOKEN` | Access token from hub.docker.com |

Optionally (if not hardcoded):
| Secret Name | Value |
|-------------|-------|
| `DOCKERHUB_USERNAME` | `irfan33` |

---

## Usage in docker-compose.yml

### In GitHub Actions:

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: irfan33
    password: ${{ secrets.DOCKERHUB_TOKEN }}

- name: Start services
  run: |
    cd docker/
    docker-compose pull  # Will pull private image
    docker-compose up -d
```

### docker-compose.yml:

```yaml
services:
  backend:
    image: irfan33/koperasi-webshop:latest # Private image
    # ... rest of config
```

---

## On Production Server

### Manual Login (One-time):

```bash
# SSH to server
ssh user@server

# Login to Docker Hub
docker login
# Username: irfan33
# Password: [your password]

# Credentials saved to ~/.docker/config.json
# Now can pull private images
docker pull irfan33/koperasi-webshop:latest
```

### Using docker-compose:

```bash
# After login once, just pull
docker-compose pull
docker-compose up -d
```

### Using GitHub Actions (Automated):

```yaml
- name: Deploy
  run: |
    ssh user@server << 'EOF'
      # Login via token (more secure than password)
      echo "${{ secrets.DOCKERHUB_TOKEN }}" | docker login -u irfan33 --password-stdin
      
      cd /opt/webshop
      docker-compose pull
      docker-compose up -d
    EOF
```

---

## Security Best Practices

### ✅ DO:

1. **Use Access Tokens**, not passwords
2. **Store in GitHub Secrets**, not in code
3. **Limit token scope** to necessary permissions
4. **Rotate tokens regularly**
5. **Use different tokens** for different environments

### ❌ DON'T:

1. **Don't hardcode credentials** in workflows
2. **Don't commit tokens** to git
3. **Don't share tokens** across projects
4. **Don't use personal password** in automation

---

## Troubleshooting

### "pull access denied"

**Cause:** Not logged in or invalid credentials

**Solution:**

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: irfan33
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

### "unauthorized: incorrect username or password"

**Cause:** Wrong token or token expired

**Solution:**

1. Generate new token at hub.docker.com
2. Update `DOCKERHUB_TOKEN` in GitHub Secrets

### "no such host"

**Cause:** Trying to pull before login

**Solution:** Always login BEFORE pulling/building

---

## Quick Reference

```yaml
# Login
- uses: docker/login-action@v3
  with:
    username: irfan33
    password: ${{ secrets.DOCKERHUB_TOKEN }}

# Pull
- run: docker pull irfan33/koperasi-webshop:latest

# Use in compose
- run: docker-compose pull
```
