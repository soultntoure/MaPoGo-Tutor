
import React, { useState } from 'react';
import UploadView from '../components/UploadView';
import DashboardView from '../components/DashboardView';

const Index: React.FC = () => {
  const [appState, setAppState] = useState<'upload' | 'dashboard'>('upload');

  const handleUploadSuccess = () => {
    setAppState('dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-bg py-8">
      <div className="max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-lg">
        {appState === 'upload' ? (
          <UploadView onUploadSuccess={handleUploadSuccess} />
        ) : (
          <DashboardView />
        )}
      </div>
    </div>
  );
};

export default Index;
