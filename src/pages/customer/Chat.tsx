import { ChatBot } from '@/components/ChatBot';

export default function CustomerChat() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Customer Support</h1>
        <p className="text-muted-foreground mt-1">Get help with your bookings and services</p>
      </div>

      <ChatBot />
    </div>
  );
}
