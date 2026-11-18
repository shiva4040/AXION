import React, { useState, useRef, useEffect } from 'react';
import { Paperclip, ArrowUp, X, FileText, AlertCircle } from 'lucide-react';
import { ingestText } from '../api/client';

interface Props {
  onSubmitQuestion: (query: string, documentId?: string) => void;
  isLoading: boolean;
}

export const Homepage: React.FC<Props> = ({ onSubmitQuestion, isLoading }) => {
  const [query, setQuery] = useState('');
  const [attachedFile, setAttachedFile] = useState<{ id?: string; name: string } | null>(null);
  const [uploading, setUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuery(e.target.value);
    setErrorMessage(null);
    // Auto-expand textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 220)}px`;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    const trimmed = query.trim();
    if (!trimmed || isLoading || uploading) return;
    setErrorMessage(null);
    onSubmitQuestion(trimmed, attachedFile?.id);
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setErrorMessage(null);
    try {
      const text = await file.text();
      const doc = await ingestText(file.name, text, `upload://${file.name}`, 'PEER_REVIEWED');
      setAttachedFile({ id: doc.id, name: file.name });
    } catch (err: any) {
      setErrorMessage(err.message || 'File upload and text ingestion failed.');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const removeAttachment = () => {
    setAttachedFile(null);
  };

  return (
    <main className="flex-1 flex flex-col justify-center items-center px-4 py-12 w-full max-w-4xl mx-auto min-h-[calc(100vh-80px)]">
      <div className="w-full max-w-2xl flex flex-col items-center">
        {/* Minimalist AXION Brand Title */}
        <h1 className="text-3xl font-medium tracking-tight text-gray-900 mb-8 select-none">
          AXION
        </h1>

        {/* Central Question Input Box */}
        <div className="w-full bg-white border border-gray-200 rounded-2xl p-4 shadow-sm focus-within:border-blue-600 focus-within:ring-4 focus-within:ring-blue-50/50 transition-all">
          <textarea
            ref={textareaRef}
            value={query}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder="What would you like to understand or solve?"
            rows={2}
            className="w-full resize-none border-none outline-none text-base text-gray-900 placeholder:text-gray-400 bg-transparent leading-relaxed"
          />

          {/* Input Action Bar */}
          <div className="flex items-center justify-between pt-3 border-t border-gray-50 mt-1">
            {/* Attachment Button & Active File Pill */}
            <div className="flex items-center gap-2">
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.pdf,.md,.json,.csv"
                onChange={handleFileChange}
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading || isLoading}
                title="Attach research document or data (.txt, .md, .csv, .json)"
                className="p-2 text-gray-400 hover:text-gray-700 hover:bg-gray-50 rounded-xl transition-colors disabled:opacity-50"
              >
                <Paperclip className="w-4 h-4" />
              </button>

              {uploading && (
                <span className="text-xs text-blue-600 animate-pulse font-medium">
                  Uploading & indexing...
                </span>
              )}

              {attachedFile && (
                <div className="flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 border border-blue-100 rounded-lg text-xs text-blue-800 font-medium">
                  <FileText className="w-3.5 h-3.5 text-blue-600" />
                  <span className="max-w-[140px] truncate">{attachedFile.name}</span>
                  <button
                    onClick={removeAttachment}
                    className="text-blue-400 hover:text-blue-700 ml-0.5"
                    title="Remove attachment"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="button"
              onClick={handleSubmit}
              disabled={!query.trim() || isLoading || uploading}
              className={`p-2.5 rounded-xl transition-all flex items-center justify-center ${
                query.trim() && !isLoading && !uploading
                  ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm cursor-pointer'
                  : 'bg-gray-100 text-gray-300 cursor-not-allowed'
              }`}
              title="Submit question (Enter)"
            >
              <ArrowUp className="w-4 h-4 stroke-[2.5]" />
            </button>
          </div>
        </div>

        {/* Error Alert Message */}
        {errorMessage && (
          <div className="mt-4 flex items-center gap-2 text-xs text-red-600 bg-red-50 border border-red-200 px-3.5 py-2 rounded-xl w-full">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}
      </div>
    </main>
  );
};
