import axios from 'axios';

// Default FastAPI port is usually 8000
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_URL,
});

export const getDashboardData = () => api.get('/dashboard/enhanced');
export const getVillages = () => api.get('/villages/');
export const getPredictions = (days = 7) => api.get(`/predictions/all?days=${days}`);
export const getAnomalies = () => api.get('/predictions/anomalies/all');
export const getOptimizedRoutes = () => api.get('/routes/optimized');

export default api;
