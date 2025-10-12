import { ChatBot } from '@/components/ChatBot';

export default function VendorChat() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Support Chat</h1>
        <p className="text-muted-foreground mt-1">Get help from operations team</p>
      </div>

      <ChatBot />
    </div>
  );
}
