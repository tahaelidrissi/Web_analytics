import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import Sources from './components/Sources';
import Scrape from './components/Scrape';
import Search from './components/Search';
import Scheduler from './components/Scheduler';
import Analytics from './components/Analytics';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'sources':
        return <Sources />;
      case 'scrape':
        return <Scrape />;
      case 'search':
        return <Search />;
      case 'scheduler':
        return <Scheduler />;
            case 'analytics':
              return <Analytics />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="max-w-7xl mx-auto px-6 py-8">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;

