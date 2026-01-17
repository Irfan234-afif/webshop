# Upgrade Guide: Frappe v15 → v16

## Perubahan yang Telah Dilakukan

File-file berikut telah diupdate untuk Frappe v16:

### 1. Containerfile

- ✅ Python: `3.11.6` → `3.14`
- ✅ Node.js: `20.19.2` → `24.0.0`
- ✅ Frappe branch: `version-15` → `version-16`

### 2. apps.json

- ✅ ERPNext: `version-15` → `version-16`
- ✅ Payments: `version-15` → `version-16`

## Langkah-Langkah Upgrade

### Step 1: Backup Data (PENTING!)

Sebelum melakukan upgrade, pastikan untuk backup database dan files:

```bash
# Masuk ke container backend yang sedang berjalan
docker compose exec backend bash

# Backup semua sites
bench backup-all-sites

# Exit dari container
exit
```

Backup files akan tersimpan di volume `sites` dalam folder masing-masing site di `private/backups/`.

### Step 2: Stop Services

```bash
cd /Users/irfanafifi/Developments/frappe_docker/development/frappe-bench/apps/webshop/docker

# Stop semua services
docker compose down
```

### Step 3: Rebuild Docker Image

```bash
# Rebuild image dengan konfigurasi v16
docker compose build --no-cache

# Atau jika menggunakan script build
./build-and-push.sh
```

> **Note**: Proses build bisa memakan waktu 10-30 menit tergantung koneksi internet dan spesifikasi hardware.

### Step 4: Start Services

```bash
# Start services (configurator akan auto-run)
docker compose up -d
```

### Step 5: Run Database Migration

```bash
# Jalankan service migrate untuk upgrade database schema
docker compose run --rm migrate

# Atau jalankan manual:
# docker compose exec backend bench --site all migrate
```

### Step 6: Rebuild Assets

```bash
# Build ulang frontend assets untuk v16
docker compose exec backend bench build --app frappe

# Build webshop frontend jika diperlukan
docker compose exec backend bash -c "cd apps/webshop/frontend && yarn install && yarn build"
```

### Step 7: Restart All Services

```bash
docker compose restart
```

### Step 8: Verify Upgrade

```bash
# Check Frappe version
docker compose exec backend bench version

# Check site status
docker compose exec backend bench --site all list-apps

# Check logs untuk error
docker compose logs -f backend
```

## Troubleshooting

### Error: ModuleNotFoundError

Jika terjadi error `ModuleNotFoundError` setelah upgrade:

```bash
# Reinstall Python packages
docker compose exec backend bash
pip install --upgrade -e apps/frappe
pip install --upgrade -e apps/erpnext
pip install --upgrade -e apps/payments
pip install --upgrade -e apps/webshop
exit
```

### Error: SyntaxError or Python Version Mismatch

Pastikan image menggunakan Python 3.12:

```bash
docker compose exec backend python --version
# Expected: Python 3.12.x
```

### Error: Node.js Version Issues

Verify Node.js version:

```bash
docker compose exec backend node --version
# Expected: v24.x.x
```

### Database Migration Errors

Jika migration gagal:

```bash
# Check migration log
docker compose exec backend bench --site [site-name] migrate --skip-failing

# Atau retry upgrade
docker compose exec backend bench retry-upgrade
```

## Breaking Changes v15 → v16

> [!WARNING]
> Review breaking changes dari Frappe v16 release notes sebelum production deployment.

Beberapa perubahan penting yang mungkin mempengaruhi webshop app:

1. **Python 3.12+ Required**: Pastikan semua custom code kompatibel dengan Python 3.12
2. **Node.js 24+ Required**: Dependencies di `frontend/package.json` mungkin perlu update
3. **API Changes**: Review Frappe API yang digunakan di webshop untuk compatibility

## Verifikasi Post-Upgrade

Setelah upgrade selesai, test fungsionalitas berikut:

- [ ] Login ke Desk
- [ ] Buat Sales Order baru
- [ ] Test webshop frontend
- [ ] Test checkout flow
- [ ] Test payment gateway (Xendit)
- [ ] Check scheduled jobs
- [ ] Review error logs

## Rollback Plan

Jika terjadi masalah kritis:

1. Stop services: `docker compose down`
2. Restore dari backup database
3. Revert Containerfile dan apps.json ke version-15
4. Rebuild image dengan v15
5. Restore data dari backup

```bash
# Restore database
docker compose exec backend bench --site [site-name] restore [backup-file-path]
```

## Resources

- [Frappe v16 Release Notes](https://github.com/frappe/frappe/releases)
- [ERPNext v16 Release Notes](https://github.com/frappe/erpnext/releases)
- [Frappe Documentation](https://docs.frappe.io/framework)
