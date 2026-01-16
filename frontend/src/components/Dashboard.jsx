import React, { useState, useEffect } from 'react';
import { configAPI, sourcesAPI, searchAPI } from '../api/client';
import { Activity, Database, Clock, Search } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const [statsRes, sourcesRes] = await Promise.all([
        configAPI.getStats(),
        sourcesAPI.getAll(),
      ]);
      setStats(statsRes.data);
      setSources(sourcesRes.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, title, value, color }) => (
    <div className="bg-white rounded-lg shadow p-6 border-l-4" style={{ borderColor: color }}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm">{title}</p>
          <p className="text-3xl font-bold mt-2">{value || 0}</p>
        </div>
        <Icon size={40} style={{ color }} className="opacity-20" />
      </div>
    </div>
  );

  if (loading) {
    return <div className="flex items-center justify-center h-96">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Titre */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Tableau de Bord</h2>
        <p className="text-gray-600 mt-2">Bienvenue sur Web Analytics Platform</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={Database}
          title="Documents Collectés"
          value={stats?.total_scraped_documents || 0}
          color="#3B82F6"
        />
        <StatCard
          icon={Activity}
          title="Sources Actives"
          value={sources.filter((s) => s.active).length}
          color="#10B981"
        />
        <StatCard
          icon={Clock}
          title="Dernière Collecte"
          value={stats?.last_scrape_time ? new Date(stats.last_scrape_time).toLocaleString('fr-FR') : 'Jamais'}
          color="#F59E0B"
        />
        <StatCard
          icon={Search}
          title="Total Sources"
          value={sources.length}
          color="#8B5CF6"
        />
      </div>

      {/* Sources actives */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-bold mb-4">Sources Actives</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">Nom</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">URL</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">Type</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">État</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {sources.slice(0, 5).map((source) => (
                <tr key={source._id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{source.name}</td>
                  <td className="px-4 py-3 text-gray-600 truncate">{source.url}</td>
                  <td className="px-4 py-3">
                    <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                      {source.source_type}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        source.active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {source.active ? 'Actif' : 'Inactif'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
