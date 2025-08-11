# MASAK Watchbot (Daily Watchlist Monitor)

Bu repo, MASAK'taki (ve benzeri kaynaklardaki) günlük eklemeleri indirip ayrıştırır,
kendi müşteri veriniz ile ID bazlı/fuzzy eşleştirir ve değişiklikleri bildirir.

## Hızlı Başlangıç

1. **Depoyu oluştur** ve bu dosyaları yükle.
2. `requirements.txt` ile bağımlılıkları kur:
   ```bash
   pip install -r requirements.txt
   ```
3. `.env` dosyanızı oluşturun (bkz. `.env.example`) ve
   - `DATABASE_URL` (PostgreSQL),
   - `SLACK_WEBHOOK_URL` (opsiyonel) ayarlayın.
4. PostgreSQL şemasını oluşturmak için `python -m src.main` çalıştırın
   (ilk çalıştırmada tablo şemaları oluşur).
5. **Müşteri tablonuzu** oluşturun (örnek SQL aşağıda).
6. `src/fetchers.py` içindeki `MASAK_URLS` listesini gerçek kaynak URL’leriyle doldurun.
7. GitHub Actions için repoda **Secrets** oluşturun:
   - `DATABASE_URL`
   - `SLACK_WEBHOOK_URL` (opsiyonel)
8. Zamanlayıcı `.github/workflows/daily.yml` ile her gün 07:30 (TR) tetiklenir.

### Örnek müşteri tablosu (minimum)
```sql
CREATE TABLE IF NOT EXISTS your_customers(
  customer_id TEXT PRIMARY KEY,
  full_name   TEXT,
  tckn        TEXT,
  passport_no TEXT,
  birth_date  DATE
);
```

### Yerel çalışma
```bash
export DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
python -m src.main
```

### Notlar
- PDF’ler çok farklı formatlarda olabilir. `src/parsers.py` içindeki regex/çıkarım
  mantığını kaynaklara göre özelleştirin.
- Eşleştirme eşiği (`rapidfuzz`) ve doğum tarihi kontrollerini `src/matcher.py`’da ayarlayabilirsiniz.
- KVKK/Uyum için gereksiz kişisel verileri loglamayın ve saklama sürelerini politika ile belirleyin.
