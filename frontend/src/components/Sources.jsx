import React, { useState, useEffect } from 'react';
import { sourcesAPI } from '../api/client';
import { Trash2, Edit2, Plus } from 'lucide-react';

export default function Sources() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    source_type: 'website',
    frequency: 24,
    selector: '',
    description: '',
  });

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    try {
      setLoading(true);
      const res = await sourcesAPI.getAll();
      setSources(res.data);
    } catch (error) {
      alert('Erreur lors du chargement des sources');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await sourcesAPI.create(formData);
      setFormData({
        name: '',
        url: '',
        source_type: 'website',
        frequency: 24,
        selector: '',
        description: '',
      });
      setShowForm(false);
      loadSources();
      alert('Source créée avec succès!');
    } catch (error) {
      alert('Erreur lors de la création de la source');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Êtes-vous sûr?')) {
      try {
        await sourcesAPI.delete(id);
        loadSources();
        alert('Source supprimée');
      } catch (error) {
        alert('Erreur lors de la suppression');
      }
    }
  };

  if (loading) {
    return <div className="text-center py-10">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold text-gray-900">Gestion des Sources</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          <Plus size={20} />
          Nouvelle Source
        </button>
      </div>

      {/* Formulaire */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Nom"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="border rounded px-3 py-2"
            />
            <input
              type="url"
              placeholder="URL"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              required
              className="border rounded px-3 py-2"
            />
            <select
              value={formData.source_type}
              onChange={(e) => setFormData({ ...formData, source_type: e.target.value })}
              className="border rounded px-3 py-2"
            >
              <option value="website">Site Web</option>
              <option value="rss">RSS</option>
              <option value="twitter">Twitter</option>
              <option value="instagram">Instagram</option>
            </select>
            <input
              type="number"
              placeholder="Fréquence (heures)"
              value={formData.frequency}
              onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
              className="border rounded px-3 py-2"
            />
            <input
              type="text"
              placeholder="Sélecteur CSS"
              value={formData.selector}
              onChange={(e) => setFormData({ ...formData, selector: e.target.value })}
              className="border rounded px-3 py-2 md:col-span-2"
            />
            <textarea
              placeholder="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="border rounded px-3 py-2 md:col-span-2"
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Créer
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500"
            >
              Annuler
            </button>
          </div>
        </form>
      )}

      {/* Tableau des sources */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Nom</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">URL</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Type</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Fréquence</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {sources.map((source) => (
              <tr key={source._id} className="hover:bg-gray-50">
                <td className="px-6 py-3 font-medium">{source.name}</td>
                <td className="px-6 py-3 text-gray-600 truncate">{source.url}</td>
                <td className="px-6 py-3">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                    {source.source_type}
                  </span>
                </td>
                <td className="px-6 py-3">{source.frequency}h</td>
                <td className="px-6 py-3 flex gap-2">
                  <button className="text-blue-600 hover:text-blue-800">
                    <Edit2 size={18} />
                  </button>
                  <button
                    onClick={() => handleDelete(source._id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 size={18} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
