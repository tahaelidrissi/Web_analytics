import React from 'react';
import { Menu, Settings } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'sources', label: 'Sources' },
    { id: 'scrape', label: 'Scrape' },
    { id: 'search', label: 'Recherche' },
    { id: 'scheduler', label: 'Scheduler' },
  ];

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
              <span className="text-blue-600 font-bold text-lg">WA</span>
            </div>
            <h1 className="text-2xl font-bold">Web Analytics</h1>
          </div>

          <div className="flex items-center gap-1 md:gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 md:px-4 py-2 rounded-lg text-sm md:text-base font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-white text-blue-600 shadow-md'
                    : 'text-blue-100 hover:bg-blue-500'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <button className="p-2 hover:bg-blue-500 rounded-lg">
            <Settings size={20} />
          </button>
        </div>
      </div>
    </nav>
  );
}
