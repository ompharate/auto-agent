import React from 'react';
import ReactMarkdown from 'react-markdown';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[85%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-900 border border-gray-200'
        }`}
      >
        {message.text && !message.result && (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{message.text}</ReactMarkdown>
          </div>
        )}


        {message.image && (
          <div className="mt-2">
            <img
              src={message.image}
              alt="Uploaded"
              className="max-w-full rounded border border-gray-300"
            />
          </div>
        )}

       
        {message.pdf && (
          <div className="mt-2 px-3 py-2 bg-gray-700 bg-opacity-20 rounded flex items-center gap-2">
            <span className="text-xl">📄</span>
            <span className="text-sm">{message.pdf}</span>
          </div>
        )}

      
        {message.audio && (
          <div className="mt-2 px-3 py-2 bg-gray-700 bg-opacity-20 rounded flex items-center gap-2">
            <span className="text-xl">🎵</span>
            <span className="text-sm">{message.audio}</span>
          </div>
        )}

      
        {message.followUpQuestion && (
          <div className="mt-3 pt-3 border-t border-gray-300">
            <p className="font-semibold text-sm mb-2">Clarification needed:</p>
            <p className="italic">{message.followUpQuestion}</p>
          </div>
        )}

   
        {message.result && (
          <div className="space-y-2">
            {message.result.task && (
              <div className="text-xs opacity-75 mb-2 uppercase tracking-wide font-semibold">
                Task: {message.result.task}
              </div>
            )}
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{message.result.final_result || ''}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
