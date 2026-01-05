# ⚠️ IMPORTANT: Update Redis URL

Your current Redis URL is incorrect. It's using the HTTPS REST API URL instead of the Redis protocol URL.

## How to Get the Correct URL:

1. Go to https://console.upstash.com/redis
2. Click on your database: `large-barnacle-32521`
3. Look for the section **"Connect your database"**
4. Find **"Redis URL"** (NOT "REST API URL")
5. Copy the URL that starts with `rediss://` (with TLS) or `redis://`

## Update .env File

Replace line 31 in `backend/.env`:

**Current (WRONG):**
```
REDIS_URL=redis://default:YOUR_PASSWORD@large-barnacle-32521.upstash.io:6379
```

**Should be (example):**
```
rediss://default:AbcXyz123YourActualPassword@large-barnacle-32521.upstash.io:6379
```

Note: `rediss://` (with double 's') means Redis with TLS encryption.

## Alternative: Use REST API (Simpler)

If you can't find the Redis URL, you can use the REST API instead:

1. Install: `pip install upstash-redis`
2. Update code to use REST API

But for now, please get the Redis protocol URL from Upstash dashboard.
