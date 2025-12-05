import React, { useState, useRef } from 'react';

const MessageInput = ({ onSend, disabled }) => {
  const [text, setText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);
  const [fileType, setFileType] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type.startsWith('image/')) {
      setSelectedFile(file);
      setFileType('image');
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setFilePreview(reader.result);
      };
      reader.readAsDataURL(file);
    } else if (file.type === 'application/pdf') {
      setSelectedFile(file);
      setFileType('pdf');
      setFilePreview(file.name);
    } else if (file.type.startsWith('audio/')) {
      setSelectedFile(file);
      setFileType('audio');
      setFilePreview(file.name);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setFilePreview(null);
    setFileType(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!text.trim() && !selectedFile) return;

    onSend({
      text: text.trim(),
      file: selectedFile,
      fileType: fileType,
      filePreview: filePreview,
    });

    setText('');
    setSelectedFile(null);
    setFilePreview(null);
    setFileType(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-white p-4">

      {filePreview && (
        <div className="mb-3 relative inline-block">
          {fileType === 'image' ? (
            <img
              src={filePreview}
              alt="Preview"
              className="max-h-32 rounded border border-gray-300"
            />
          ) : (
            <div className="px-4 py-2 bg-gray-100 border border-gray-300 rounded flex items-center gap-2">
              <span className="text-2xl">{fileType === 'audio' ? '🎵' : '📄'}</span>
              <span className="text-sm text-gray-700">{filePreview}</span>
            </div>
          )}
          <button
            type="button"
            onClick={handleRemoveFile}
            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600 transition"
          >
            ×
          </button>
        </div>
      )}

    
      <div className="flex gap-2">
      
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept="image/*,application/pdf,audio/*"
          className="hidden"
          disabled={disabled}
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          📎
        </button>

      
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type your message or upload a file (image/PDF/audio)..."
          disabled={disabled}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        />

    
        <button
          type="submit"
          disabled={disabled || (!text.trim() && !selectedFile)}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>
    </form>
  );
};

export default MessageInput;
