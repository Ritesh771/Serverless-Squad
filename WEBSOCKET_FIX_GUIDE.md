# WebSocket Connection Fix Guide

## Problem
WebSocket connections are failing with the error: "WebSocket is closed before the connection is established"

This happens because the standard Django development server (`python manage.py runserver`) **does not support WebSockets**. Django Channels requires an ASGI server like Daphne or Uvicorn.

## Solution

### Step 1: Install Required Dependencies

```bash
pip install -r requirements.txt
```

The requirements.txt now includes:
- `daphne==4.2.0` - ASGI server that supports WebSockets
- `uvicorn==0.32.0` - Alternative ASGI server (optional)

### Step 2: Start the Server Correctly

#### Option A: Using the Provided Scripts (Recommended)

**On macOS/Linux:**
```bash
chmod +x start_server.sh
./start_server.sh
```

**On Windows:**
```cmd
start_server.bat
```

#### Option B: Manual Command

**Using Daphne (Recommended for Django Channels):**
```bash
daphne -b 0.0.0.0 -p 8000 homeserve_pro.asgi:application
```

**Using Uvicorn (Alternative):**
```bash
uvicorn homeserve_pro.asgi:application --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Start the Frontend

In a **separate terminal**, run:
```bash
npm run dev
```

The frontend will be available at http://localhost:8080

## What Changed?

### 1. **Updated requirements.txt**
Added ASGI servers (Daphne and Uvicorn) that support WebSocket connections.

### 2. **Created Start Scripts**
- `start_server.sh` - For macOS/Linux
- `start_server.bat` - For Windows

These scripts run Django with the correct ASGI server.

### 3. **Existing WebSocket Configuration**
Your project already has proper WebSocket configuration:
- ✅ `ASGI_APPLICATION` configured in settings.py
- ✅ Channel layers configured (InMemoryChannelLayer)
- ✅ WebSocket consumers implemented
- ✅ WebSocket routing defined
- ✅ Frontend WebSocket hooks configured

## WebSocket Endpoints Available

Once the ASGI server is running, these WebSocket endpoints will work:

1. **Live Status Updates:**
   ```
   ws://localhost:8000/ws/status/{user_id}/{role}/
   ```

2. **Chat Support:**
   ```
   ws://localhost:8000/ws/chat/{user_id}/{role}/
   ```

3. **Booking Updates:**
   ```
   ws://localhost:8000/ws/bookings/{booking_id}/
   ```

4. **Notifications:**
   ```
   ws://localhost:8000/ws/notifications/{user_id}/
   ```

## Testing WebSocket Connection

After starting the ASGI server:

1. Open your browser console (F12)
2. Login to the application
3. You should see:
   ```
   WebSocket connected successfully
   ```

4. Previously, you saw the error:
   ```
   WebSocket is closed before the connection is established ❌
   ```

5. Now you should see:
   ```
   WebSocket connected ✅
   ```

## Important Notes

### ⚠️ DO NOT Use `python manage.py runserver`

The standard Django development server **DOES NOT** support WebSockets. Always use:
- `daphne` (recommended)
- `uvicorn` (alternative)

### 🔄 Switching Between Servers

**Stop the old server** (Ctrl+C) before starting with the new ASGI server.

### 📝 Development Workflow

**Terminal 1 (Backend):**
```bash
./start_server.sh  # or start_server.bat on Windows
```

**Terminal 2 (Frontend):**
```bash
npm run dev
```

## Troubleshooting

### Issue: "daphne: command not found"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"
**Solution:** Stop the existing Django server
```bash
# Find the process
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Issue: WebSocket still not connecting
**Solution:** Check CORS settings
- Verify `ALLOWED_HOSTS` includes localhost
- Check `CORS_ALLOWED_ORIGINS` includes your frontend URL
- Clear browser cache and reload

### Issue: "InMemoryChannelLayer" warnings
**Solution:** This is normal for development. For production, you would use Redis:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

## Production Deployment

For production, consider:
1. Use Redis for channel layer instead of InMemory
2. Use Daphne with a process manager (systemd, supervisor)
3. Configure a reverse proxy (nginx, Apache)
4. Enable SSL/TLS for wss:// (secure WebSocket)

## Additional Resources

- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Daphne Documentation](https://github.com/django/daphne)
- [WebSocket RFC](https://tools.ietf.org/html/rfc6455)

## Summary

The fix is simple:
1. ✅ Install ASGI server: `pip install -r requirements.txt`
2. ✅ Run with Daphne: `./start_server.sh` (not `python manage.py runserver`)
3. ✅ Start frontend: `npm run dev`
4. ✅ WebSockets now work!

Your WebSocket connections will now work correctly! 🎉
