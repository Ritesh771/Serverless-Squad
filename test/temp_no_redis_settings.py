# Temporary settings override for testing without Redis
# Add this to the bottom of homeserve_pro/settings.py

import os

# Override cache settings for development without Redis
if os.environ.get('NO_REDIS', 'false').lower() == 'true':
    print("⚠️  Running with in-memory cache (Redis disabled)")
    
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'homeserve-cache',
            'TIMEOUT': 300,  # 5 minutes
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
            }
        }
    }
    
    # Disable Celery for testing (run tasks synchronously)
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    
    # Use console email backend for testing
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    
    print("✅ Temporary cache settings applied")

# Production Redis settings (default)
else:
    # Your existing Redis CACHES configuration stays as is
    pass