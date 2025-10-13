@echo off
REM Start Django ASGI Server with WebSocket support
REM This script runs the Django backend with Daphne to support WebSockets

echo 🚀 Starting Django ASGI Server with WebSocket support...
echo 📡 Backend will be available at http://localhost:8000
echo 🔌 WebSocket endpoints will be available at ws://localhost:8000/ws/
echo.

REM Run Daphne ASGI server
daphne -b 0.0.0.0 -p 8000 homeserve_pro.asgi:application
