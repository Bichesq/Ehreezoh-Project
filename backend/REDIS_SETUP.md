# Quick Reference: Get Redis URL from Upstash

## Steps to Get Correct Redis URL

1. Go to https://console.upstash.com/redis
2. Click on your database: `large-barnacle-32521`
3. Scroll down to **"Connect your database"** section
4. Look for **"Redis URL"** (NOT REST API URL)
5. Copy the URL that starts with `redis://`

## Format

The URL should look like:
```
redis://default:YOUR_PASSWORD_HERE@large-barnacle-32521.upstash.io:6379
```

## Update .env File

Replace line 31 in `backend/.evn` with the copied URL:

```bash
REDIS_URL=redis://default:AbcXyz123...@large-barnacle-32521.upstash.io:6379
```

## Important Notes

- ❌ **Don't use** the HTTPS REST API URL
- ✅ **Use** the Redis protocol URL (starts with `redis://`)
- The password is the long string after `default:`
- Port is usually `:6379` or `:6380` (TLS)

## Alternative: Use REST API (Simpler for Development)

If you prefer to use the REST API (no password needed):

1. Install additional package:
   ```bash
   pip install upstash-redis
   ```

2. Use REST URL in code:
   ```python
   from upstash_redis import Redis
   redis = Redis(url="https://large-barnacle-32521.upstash.io", token="YOUR_TOKEN")
   ```

But for now, get the standard Redis URL for compatibility with our code.
