import React, { useState, useEffect } from 'react';
import { analyticsAPI } from '../api/client';
import Plot from 'react-plotly.js';
import { BarChart3, PieChart, TrendingUp, Brain, Zap } from 'lucide-react';

export default function Analytics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const res = await analyticsAPI.getStats();
      setStats(res.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeBatch = async () => {
    try {
      setAnalyzing(true);
      await analyticsAPI.analyzeBatch(10);
      alert('Analyse terminée!');
      loadStats();
    } catch (error) {
      alert('Erreur lors de l\'analyse');
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return <div className="text-center py-10">Chargement...</div>;
  }

  const sentimentColors = {
    positive: '#10B981',
    negative: '#EF4444',
    neutral: '#6B7280'
  };

  const categoryColors = [
    '#3B82F6', '#8B5CF6', '#EC4899', '#F59E0B', 
    '#10B981', '#06B6D4', '#6366F1', '#F97316'
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Analytics & IA</h2>
          <p className="text-gray-600 mt-2">Analyse intelligente des documents avec GPT</p>
        </div>
        <button
          onClick={handleAnalyzeBatch}
          disabled={analyzing}
          className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50"
        >
          <Brain size={20} />
          {analyzing ? 'Analyse en cours...' : 'Analyser 10 documents'}
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 className="text-blue-600" size={24} />
            <h3 className="font-bold text-gray-900">Documents Analysés</h3>
          </div>
          <p className="text-4xl font-bold text-blue-600">{stats?.total_documents || 0}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="text-green-600" size={24} />
            <h3 className="font-bold text-gray-900">Sentiments Positifs</h3>
          </div>
          <p className="text-4xl font-bold text-green-600">
            {stats?.sentiment_distribution?.positive || 0}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <Zap className="text-purple-600" size={24} />
            <h3 className="font-bold text-gray-900">Catégories</h3>
          </div>
          <p className="text-4xl font-bold text-purple-600">
            {Object.keys(stats?.category_distribution || {}).length}
          </p>
        </div>
      </div>

      {/* Sentiment Distribution (Plotly Pie) */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <PieChart size={20} className="text-gray-700" />
          Distribution des Sentiments
        </h3>
        <Plot
          data={[{
            type: 'pie',
            labels: Object.keys(stats?.sentiment_distribution || {}),
            values: Object.values(stats?.sentiment_distribution || {}),
            marker: { colors: Object.keys(stats?.sentiment_distribution || {}).map(s => sentimentColors[s] || '#6B7280') },
            hole: 0.4
          }]}
          layout={{
            autosize: true,
            height: 360,
            margin: { l: 10, r: 10, t: 10, b: 10 },
            showlegend: true
          }}
          style={{ width: '100%' }}
          config={{ displayModeBar: false }}
        />
      </div>

      {/* Category Distribution (Plotly Bar) */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <BarChart3 size={20} className="text-gray-700" />
          Distribution des Catégories
        </h3>
        <Plot
          data={[{
            type: 'bar',
            x: Object.keys(stats?.category_distribution || {}),
            y: Object.values(stats?.category_distribution || {}),
            marker: { color: categoryColors },
          }]}
          layout={{
            autosize: true,
            height: 360,
            margin: { l: 40, r: 10, t: 10, b: 60 },
            xaxis: { tickangle: -30 },
          }}
          style={{ width: '100%' }}
          config={{ displayModeBar: false }}
        />
      </div>

      {/* Top Keywords (Plotly Horizontal Bar) */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-bold text-lg mb-4">Top 20 Mots-clés</h3>
        <Plot
          data={[{
            type: 'bar',
            orientation: 'h',
            x: (stats?.top_keywords || []).map(k => k.count),
            y: (stats?.top_keywords || []).map(k => k.keyword),
            marker: { color: '#3B82F6' },
          }]}
          layout={{
            autosize: true,
            height: 600,
            margin: { l: 150, r: 10, t: 10, b: 10 },
          }}
          style={{ width: '100%' }}
          config={{ displayModeBar: false }}
        />
      </div>
    </div>
  );
}
