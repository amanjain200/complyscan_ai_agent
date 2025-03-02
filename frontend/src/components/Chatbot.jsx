import { useState } from 'react';
import { useImmer } from 'use-immer';
import api from '@/api';
// import { parseSSEStream } from '@/utils';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';

function Chatbot() {
  const [chatId, setChatId] = useState(null);
  const [messages, setMessages] = useImmer([]);
  const [newMessage, setNewMessage] = useState('');

  const isLoading = messages.length && messages[messages.length - 1].loading;

  async function submitNewMessage() {
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage || isLoading) return;
  
    setMessages(draft => [...draft,
      { role: 'user', content: trimmedMessage },
      { role: 'assistant', content: '', loading: true }
    ]);
    setNewMessage('');
  
    let chatIdOrNew = chatId;
    try {
      if (!chatId) {
        const { id } = await api.createChat();
        setChatId(id);
        chatIdOrNew = id;
      }
  
      const response = await api.sendChatMessage(chatIdOrNew, trimmedMessage);
  
      setMessages(draft => {
        draft[draft.length - 1].content = response.message; // Assuming API response has { message: "..." }
        draft[draft.length - 1].loading = false;
      });
  
    } catch (err) {
      console.error(err);
      setMessages(draft => {
        draft[draft.length - 1].loading = false;
        draft[draft.length - 1].error = true;
        draft[draft.length - 1].content = "Error processing request.";
      });
    }
  }
  

  return (
    <div className='relative grow flex flex-col gap-6 pt-6'>
      {messages.length === 0 && (
        <div className='mt-3 font-urbanist text-primary-blue text-xl font-light space-y-2'>
           <h2>👋 Welcome to <strong>ComplyScan!</strong></h2>
           <p>I’m <strong>ComplyScan – your AI Agent for Web Accessibility & Compliance.</strong></p>
           <p>🌐 <strong>Enter the URL</strong> of the website you want to check, and I will scan, analyze and report the Compliance and Accessibility issues present in it 🚀</p>
           
        </div>
      )}
      <ChatMessages
        messages={messages}
        isLoading={isLoading}
      />
      <ChatInput
        newMessage={newMessage}
        isLoading={isLoading}
        setNewMessage={setNewMessage}
        submitNewMessage={submitNewMessage}
      />
    </div>
  );
}

export default Chatbot;