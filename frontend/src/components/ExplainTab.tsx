import React, { useState } from 'react';
import { MessageSquare, Send, Loader2 } from 'lucide-react';

const ExplainTab: React.FC = () => {
  const [conceptQuery, setConceptQuery] = useState('');
  const [explanation, setExplanation] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleExplain = async () => {
    if (!conceptQuery.trim()) return;

    setIsLoading(true);
    setExplanation('');

    try {
      const response = await fetch('http://localhost:5000/explain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: conceptQuery }),
      });

      const data = await response.json();

      if (response.ok) {
        setExplanation(data.explanation);
      } else {
        setExplanation('Error generating explanation. Please try again.');
      }
    } catch (error) {
      setExplanation('Network error. Please check if the server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleExplain();
    }
  };

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-[#333333] flex items-center space-x-2">
        <MessageSquare className="w-5 h-5" />
        <span>Q&A Chatbot</span>
      </h3>

      <div className="flex space-x-3">
        <input
          type="text"
          value={conceptQuery}
          onChange={(e) => setConceptQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter a question..."
          className="flex-1 px-4 py-3 border border-gray-light rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
        />
        <button
          onClick={handleExplain}
          disabled={isLoading || !conceptQuery.trim()}
          className={`
            px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2
            ${isLoading || !conceptQuery.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
              : 'bg-primary text-white hover:bg-blue-600 hover:shadow-md'
            }
          `}
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
          <span>{isLoading ? 'Processing...' : 'Get Answer'}</span>
        </button>
      </div>

      <div className="min-h-[300px] p-4 border border-gray-light rounded-lg bg-gray-50">
        {isLoading ? (
          <div className="flex items-center justify-center h-full text-gray-600">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
              <p>Generating explanation...</p>
            </div>
          </div>
        ) : explanation ? (
          <div className="prose max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-gray-700 leading-relaxed">
              {explanation}
            </pre>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <MessageSquare className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>Enter a question above to get a detailed answer.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExplainTab;
