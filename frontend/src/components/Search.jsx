import React, { useState } from 'react';
import { searchAPI } from '../api/client';
import { Search as SearchIcon, Calendar } from 'lucide-react';

export default function Search() {
  const [keyword, setKeyword] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!keyword.trim()) return;

    try {
      setLoading(true);
      setSearched(true);
      const res = await searchAPI.search(keyword, 50);
      setResults(res.data.results || []);
    } catch (error) {
      alert('Erreur lors de la recherche: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-900">Recherche dans les Documents</h2>

      {/* Formulaire de recherche */}
      <form onSubmit={handleSearch} className="bg-white rounded-lg shadow p-6">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="Rechercher un mot-clé..."
              className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <SearchIcon className="absolute right-3 top-3 text-gray-400" size={20} />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Recherche...' : 'Rechercher'}
          </button>
        </div>
      </form>

      {/* Résultats */}
      {searched && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold mb-4">
            {loading ? 'Recherche...' : `${results.length} résultat(s) trouvé(s)`}
          </h3>

          {results.length === 0 && !loading && (
            <p className="text-gray-600 text-center py-8">Aucun résultat trouvé</p>
          )}

          <div className="space-y-4">
            {results.map((result, idx) => (
              <div key={idx} className="border rounded-lg p-4 hover:shadow-md transition">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h4 className="font-semibold text-gray-900 flex-1">{result.url}</h4>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded flex-shrink-0">
                    Mots: {result.matched_keywords?.join(', ') || 'N/A'}
                  </span>
                </div>

                <p className="text-gray-700 mb-3 line-clamp-2">{result.content}</p>

                <div className="flex items-center text-xs text-gray-500 gap-4">
                  <div className="flex items-center gap-1">
                    <Calendar size={14} />
                    {new Date(result.scraped_at).toLocaleDateString('fr-FR')}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
