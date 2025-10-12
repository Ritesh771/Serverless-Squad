from django.core.management.base import BaseCommand
from django.test import RequestFactory
from core.views import chat_query, chat_context
import json

class Command(BaseCommand):
    help = 'Test chat functionality'

    def handle(self, *args, **options):
        factory = RequestFactory()
        
        # Test chat_query
        try:
            request = factory.post('/api/chat/query/', 
                                 data=json.dumps({
                                     'user_id': '1',
                                     'role': 'customer',
                                     'message': 'Hello'
                                 }),
                                 content_type='application/json')
            response = chat_query(request)
            self.stdout.write(f"chat_query response: {response.content}")
        except Exception as e:
            self.stdout.write(f"Error in chat_query: {e}")
        
        # Test chat_context
        try:
            request = factory.get('/api/chat/context/', 
                                {'user_id': '1', 'role': 'customer'})
            response = chat_context(request)
            self.stdout.write(f"chat_context response: {response.content}")
        except Exception as e:
            self.stdout.write(f"Error in chat_context: {e}")