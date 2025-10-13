# 🚀 Redis Setup for HomeServe Pro

## Problem: Redis Connection Error
The authentication system requires Redis for OTP storage, but Redis is not running.

**Error**: `Error 10061 connecting to localhost:6379. No connection could be made because the target machine actively refused it.`

## Solution Options

### Option 1: Install Redis Locally (Recommended)

#### For Windows:

**Method A: Using Chocolatey (Easiest)**
```powershell
# Install Chocolatey first (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Redis
choco install redis-64

# Start Redis service
redis-server
```

**Method B: Download Binary (Alternative)**
1. Download from: https://github.com/tporadowski/redis/releases
2. Extract to `C:\Redis\`
3. Run `redis-server.exe`

#### For Mac:
```bash
# Install Redis using Homebrew
brew install redis

# Start Redis service
brew services start redis

# Or start manually
redis-server
```

#### For Linux:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Option 2: Use Redis Cloud (Free Tier)

1. Sign up at: https://redis.com/try-free/
2. Create a free database
3. Get the connection URL
4. Update your `.env` file:
```env
REDIS_URL=redis://username:password@hostname:port
```

### Option 3: Temporary Fix - Disable Redis (Testing Only)

For immediate testing, you can temporarily use in-memory cache:

**Update `homeserve_pro/settings.py`:**
```python
# Temporary cache settings for testing (NO REDIS)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'homeserve-cache',
        'TIMEOUT': 300,  # 5 minutes
    }
}

# Disable Celery for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
```

## Testing Redis Connection

After installing Redis, test the connection:

```bash
# Test Redis directly
redis-cli ping
# Should return: PONG

# Test Django cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'hello')
>>> cache.get('test')
# Should return: 'hello'
```

## Restart Services After Redis Setup

```bash
# 1. Start Redis (keep running)
redis-server

# 2. Start Django backend (new terminal)
python manage.py runserver 8000

# 3. Test authentication
python test_auth_endpoints.py
```

## Expected Success Output

After Redis is running, you should see:
```
🔧 Testing HomeServe Pro Authentication Endpoints

1. Testing Login Endpoint...
   Status: 401
   ❌ Login failed (Expected - need to create users)

2. Testing Send OTP Endpoint...
   Status: 200
   ✅ Send OTP endpoint working
   Message: User created and OTP sent successfully via email
   DEBUG OTP: 123456

3. Testing Endpoint Availability...
   ✅ All endpoints available
```

## Production Setup

For production, configure Redis with:
- **Persistence**: Enable RDB/AOF backups
- **Security**: Set password and restrict access
- **Memory**: Configure appropriate memory limits
- **Monitoring**: Set up Redis monitoring

## Benefits of Redis

Once Redis is running, you'll have:
- ✅ **OTP Authentication** working properly
- ✅ **Fast API responses** via caching
- ✅ **Background tasks** for notifications
- ✅ **Session management** for users
- ✅ **Real-time features** via WebSocket support

Choose **Option 1** for development and testing!