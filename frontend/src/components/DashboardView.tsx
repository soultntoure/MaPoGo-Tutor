import React, { useState } from 'react';
import SummaryTab from './SummaryTab';
import ExplainTab from './ExplainTab';
import QuizTab from './QuizTab';

const DashboardView: React.FC = () => {
  const [activeTab, setActiveTab] = useState('summary');

  const tabs = [
    { id: 'summary', label: 'Summary' },
    { id: 'explain', label: 'Q&A Chatbot' },
    { id: 'quiz', label: 'Quiz' },
  ];

  return (
    <div className="animate-fade-in">
      <h2 className="text-3xl font-bold text-[#333333] mb-6">
        Document Dashboard
      </h2>

      {/* Tab Navigation */}
      <div className="border-b border-gray-light mb-6">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                py-3 px-4 font-medium transition-all duration-200
                ${activeTab === tab.id
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-gray-600 hover:text-primary hover:border-b-2 hover:border-gray-300'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow-md p-6">
        {activeTab === 'summary' && <SummaryTab />}
        {activeTab === 'explain' && <ExplainTab />}
        {activeTab === 'quiz' && <QuizTab />}
      </div>
    </div>
  );
};

export default DashboardView;
