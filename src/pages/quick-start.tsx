import React from 'react';
import { Button } from "@/components/ui/button";

const QuickStart: React.FC = () => {
  // 模拟消息数据
  const messages = [
    { id: 1, sender: 'opponent', text: 'Hello! How can I help you today?' },
    { id: 2, sender: 'user', text: 'Hi, I need help with setting up my account.' },
    { id: 3, sender: 'opponent', text: 'Sure, I can assist with that. What seems to be the problem?' },
    { id: 4, sender: 'user', text: 'I am unable to log in.' },
    { id: 5, sender: 'opponent', text: 'Okay, let me check your account status.' },
    { id: 6, sender: 'user', text: 'Thank you!' },
    { id: 7, sender: 'opponent', text: 'Please wait a moment... I see the issue. Your password might have expired.' },
    { id: 8, sender: 'user', text: 'Oh, okay. How can I reset it?' },
    { id: 9, sender: 'opponent', text: 'I can send you a reset link. Please confirm your email address.' },
    { id: 10, sender: 'user', text: 'myemail@example.com' },
  ];

  return (
    // 主容器，使用 flex-col 并占满高度 (假设父容器提供了高度限制)
    <div className="flex flex-col h-full bg-card text-card-foreground shadow-sm rounded-lg overflow-hidden">
      {/* 顶部消息列表区域，flex-1 使其填充剩余空间，overflow-y-auto 允许内部滚动 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <h1 className="text-xl font-semibold mb-4 border-b pb-2">Team Conversation</h1>
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${message.sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}
            >
              {message.text}
            </div>
          </div>
        ))}
      </div>

      {/* 底部按钮区域 */}
      <div className="p-4 border-t bg-background">
        <Button className="w-full" type="button">
          Start Listening
        </Button>
      </div>
    </div>
  );
};

export default QuickStart; 