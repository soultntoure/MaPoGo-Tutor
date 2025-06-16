
import React, { useState } from 'react';
import { FileText, Loader2 } from 'lucide-react';

const SummaryTab: React.FC = () => {
  const [summary, setSummary] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasGenerated, setHasGenerated] = useState(false);

  const handleGenerateSummary = async () => {
    setIsLoading(true);
    setSummary('');

    try {
      const response = await fetch('http://localhost:5000/summary');
      const data = await response.json();

      if (response.ok) {
        setSummary(data.summary);
        setHasGenerated(true);
      } else {
        setSummary('Error generating summary. Please try again.');
      }
    } catch (error) {
      setSummary('Network error. Please check if the server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-[#333333] flex items-center space-x-2">
          <FileText className="w-5 h-5" />
          <span>Document Summary</span>
        </h3>
        
        <button
          onClick={handleGenerateSummary}
          disabled={isLoading}
          className={`
            px-6 py-2 rounded-lg font-medium transition-all duration-200
            ${isLoading 
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
              : 'bg-primary text-white hover:bg-blue-600 hover:shadow-md'
            }
          `}
        >
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Generating...</span>
            </div>
          ) : (
            hasGenerated ? 'Regenerate Summary' : 'Generate Summary'
          )}
        </button>
      </div>

      <div className="min-h-[300px] p-4 border border-gray-light rounded-lg bg-gray-50">
        {isLoading ? (
          <div className="flex items-center justify-center h-full text-gray-600">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
              <p>Generating summary...</p>
            </div>
          </div>
        ) : summary ? (
          <div className="prose max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-gray-700 leading-relaxed">
              {summary}
            </pre>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <FileText className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>Click "Generate Summary" to create a summary of your document.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SummaryTab;
