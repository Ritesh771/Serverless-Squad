import { ChatBot } from '@/components/ChatBot';

export default function OpsChat() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Team Chat</h1>
        <p className="text-muted-foreground mt-1">Operations team communication hub</p>
      </div>

      <ChatBot />
    </div>
  );
}
