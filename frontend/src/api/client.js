import axios from 'axios';

// Base URL de l'API configurable via variables d'environnement Vite
// Défaut: http://localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Sources
export const sourcesAPI = {
  getAll: () => client.get('/sources/'),
  create: (data) => client.post('/sources/', data),
  update: (id, data) => client.put(`/sources/${id}`, data),
  delete: (id) => client.delete(`/sources/${id}`),
};

// Scraping
export const scrapingAPI = {
  scrape: (data) => client.post('/scrape', data),
  scrapeBySource: (data) => client.post('/scrape-source', data),
};

// Config
export const configAPI = {
  get: () => client.get('/config'),
  update: (data) => client.put('/config', data),
  getStats: () => client.get('/config/stats'),
};

// Scheduler
export const schedulerAPI = {
  getStatus: () => client.get('/scheduler/status'),
  schedule: (data) => client.post('/scheduler/schedule', data),
  unschedule: (sourceId) => client.delete(`/scheduler/unschedule/${sourceId}`),
  start: () => client.post('/scheduler/start'),
  stop: () => client.post('/scheduler/stop'),
};

// Search
export const searchAPI = {
  search: (keyword, limit = 50) => client.get('/search', { 
    params: { keyword, limit } 
  }),
};

// Analytics
export const analyticsAPI = {
  analyzeDocument: (documentId) =>
    client.post('/analytics/analyze-document', { document_id: documentId }),
  analyzeBatch: (limit = 10) =>
    client.post('/analytics/analyze-batch', { limit }),
  getStats: () => client.get('/analytics/stats'),
  getByCategory: (category, limit = 50) =>
    client.get(`/analytics/documents-by-category/${category}`, { params: { limit } }),
  searchByKeywords: (keywords, limit = 20) =>
    client.get('/analytics/search-by-keywords', { params: { keywords, limit } }),
};

export default client;
