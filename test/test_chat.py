import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')
django.setup()

# Test importing the chat functions
try:
    from core.views import chat_query, chat_context
    print("Successfully imported chat functions")
except Exception as e:
    print(f"Error importing chat functions: {e}")

# Test if we can access the functions
try:
    print(f"chat_query function: {chat_query}")
    print(f"chat_context function: {chat_context}")
except Exception as e:
    print(f"Error accessing functions: {e}")