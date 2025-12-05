import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './components/ChatMessage';
import MessageInput from './components/MessageInput';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const handleSend = async ({ text, file, fileType, filePreview }) => {
   
    const userMessage = {
      id: Date.now(),
      role: 'user',
      text: text || null,
      image: fileType === 'image' ? filePreview : null,
      pdf: fileType === 'pdf' ? filePreview : null,
      audio: fileType === 'audio' ? filePreview : null,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      
      const formData = new FormData();
      if (text) formData.append('text', text);
      if (file && fileType === 'image') formData.append('image', file);
      if (file && fileType === 'pdf') formData.append('pdf', file);
      if (file && fileType === 'audio') formData.append('audio', file);


      const response = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

  
      const agentMessage = {
        id: Date.now() + 1,
        role: 'agent',
        text: data.final_result || null,
        followUpQuestion: data.clarification_question || null,
        result: data,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'agent',
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
 
      <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-800">
          Auto-agent
        </h1>
        <p className="text-sm text-gray-600">
          Ask questions, upload images, or get help with tasks
        </p>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center">
              <p className="text-lg">Start a conversation</p>
              <p className="text-sm mt-2">
                Send a message or upload an image to begin
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-100 rounded-lg px-4 py-3 border border-gray-200">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>


      <MessageInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
};

export default App;