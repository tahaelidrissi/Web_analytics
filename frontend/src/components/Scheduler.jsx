import React, { useState, useEffect } from 'react';
import { schedulerAPI, sourcesAPI } from '../api/client';
import { Play, Pause, Plus, Trash2 } from 'lucide-react';

export default function Scheduler() {
  const [jobs, setJobs] = useState([]);
  const [status, setStatus] = useState(null);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    source_id: '',
    frequency_hours: 1,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statusRes, sourcesRes] = await Promise.all([
        schedulerAPI.getStatus(),
        sourcesAPI.getAll(),
      ]);
      setStatus(statusRes.data);
      setJobs(statusRes.data.jobs || []);
      setSources(sourcesRes.data);
      console.log('Sources chargées:', sourcesRes.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSchedule = async (e) => {
    e.preventDefault();
    try {
      await schedulerAPI.schedule(formData);
      setFormData({ source_id: '', frequency_hours: 1 });
      setShowForm(false);
      loadData();
      alert('Tâche planifiée!');
    } catch (error) {
      alert('Erreur lors de la planification');
    }
  };

  const handleToggleScheduler = async () => {
    try {
      if (status?.running) {
        await schedulerAPI.stop();
      } else {
        await schedulerAPI.start();
      }
      loadData();
    } catch (error) {
      alert('Erreur');
    }
  };

  const handleRemoveJob = async (sourceId) => {
    if (window.confirm('Supprimer cette tâche?')) {
      try {
        await schedulerAPI.unschedule(sourceId);
        loadData();
      } catch (error) {
        alert('Erreur');
      }
    }
  };

  if (loading) {
    return <div className="text-center py-10">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold text-gray-900">Planificateur</h2>
        <button
          onClick={handleToggleScheduler}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-white ${
            status?.running
              ? 'bg-red-600 hover:bg-red-700'
              : 'bg-green-600 hover:bg-green-700'
          }`}
        >
          {status?.running ? <Pause size={20} /> : <Play size={20} />}
          {status?.running ? 'Arrêter' : 'Démarrer'}
        </button>
      </div>

      {/* Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-bold mb-3">État du Scheduler</h3>
        <div className="space-y-2">
          <p className="text-gray-700">
            État:{' '}
            <span className={`font-bold ${status?.running ? 'text-green-600' : 'text-red-600'}`}>
              {status?.running ? '🟢 En cours d\'exécution' : '🔴 Arrêté'}
            </span>
          </p>
          <p className="text-gray-700">Tâches actives: {jobs.length}</p>
        </div>
      </div>

      {/* Ajouter une tâche */}
      <button
        onClick={() => setShowForm(!showForm)}
        className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
      >
        <Plus size={20} />
        Planifier une Source
      </button>

      {showForm && (
        <form onSubmit={handleSchedule} className="bg-white rounded-lg shadow p-6 space-y-4">
          <select
            value={formData.source_id}
            onChange={(e) => setFormData({ ...formData, source_id: e.target.value })}
            required
            className="w-full border rounded px-3 py-2"
          >
            <option value="">Sélectionnez une source</option>
            {sources.map((source) => (
              <option key={source.id} value={source.id}>
                {source.name}
              </option>
            ))}
          </select>

          <div>
            <label className="block text-sm font-medium mb-2">Fréquence (heures)</label>
            <input
              type="number"
              value={formData.frequency_hours}
              onChange={(e) =>
                setFormData({ ...formData, frequency_hours: parseFloat(e.target.value) })
              }
              min="0.01"
              step="0.01"
              className="w-full border rounded px-3 py-2"
            />
            <p className="text-xs text-gray-500 mt-1">
              Minimum: 0.01 heure. Pour tester: 0.02 = 1.2 minutes
            </p>
          </div>

          <div className="flex gap-2">
            <button
              type="submit"
              className="flex-1 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Planifier
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="flex-1 bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500"
            >
              Annuler
            </button>
          </div>
        </form>
      )}

      {/* Liste des jobs */}
      <div className="bg-white rounded-lg shadow">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-left font-semibold">Tâche</th>
              <th className="px-6 py-3 text-left font-semibold">Intervalle</th>
              <th className="px-6 py-3 text-left font-semibold">État</th>
              <th className="px-6 py-3 text-left font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {jobs.length === 0 ? (
              <tr>
                <td colSpan="4" className="px-6 py-6 text-center text-gray-500">
                  Aucune tâche planifiée
                </td>
              </tr>
            ) : (
              jobs.map((job) => (
                <tr key={job.job_id} className="hover:bg-gray-50">
                  <td className="px-6 py-3 font-medium">{job.job_id}</td>
                  <td className="px-6 py-3">{job.frequency_hours}h</td>
                  <td className="px-6 py-3">
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
                      Planifiée
                    </span>
                  </td>
                  <td className="px-6 py-3">
                    <button
                      onClick={() => handleRemoveJob(job.source_id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
