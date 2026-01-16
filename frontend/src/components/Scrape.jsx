import React, { useState } from 'react';
import { scrapingAPI } from '../api/client';
import { Play, Copy } from 'lucide-react';

export default function Scrape() {
  const [url, setUrl] = useState('');
  const [selector, setSelector] = useState('');
  const [limit, setLimit] = useState(10);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleScrape = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const res = await scrapingAPI.scrape({
        url,
        selector,
        limit: parseInt(limit),
      });
      setResults(res.data);
    } catch (error) {
      alert('Erreur lors du scraping: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-900">Scraper une URL</h2>

      {/* Formulaire */}
      <form onSubmit={handleScrape} className="bg-white rounded-lg shadow p-6 space-y-4">
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">URL</label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            required
            className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">Sélecteur CSS (optionnel)</label>
          <input
            type="text"
            value={selector}
            onChange={(e) => setSelector(e.target.value)}
            placeholder="p, .article, article > h2"
            className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">Limite</label>
          <input
            type="number"
            value={limit}
            onChange={(e) => setLimit(e.target.value)}
            min="1"
            max="100"
            className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <Play size={20} />
          {loading ? 'Scraping en cours...' : 'Commencer le Scraping'}
        </button>
      </form>

      {/* Résultats */}
      {results && (
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold">
              Résultats ({results.count} éléments trouvés)
            </h3>
            <span className="text-sm text-gray-600">{results.content_type}</span>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {results.data && results.data.map((item, idx) => (
              <div key={idx} className="bg-gray-50 p-4 rounded border-l-4 border-blue-500">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-gray-800 flex-1">{item.value}</p>
                  <button className="text-gray-400 hover:text-gray-600 flex-shrink-0">
                    <Copy size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
