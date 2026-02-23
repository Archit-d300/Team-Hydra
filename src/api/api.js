import axios from 'axios';

// In development, vite proxy forwards /api/* to backend (http://localhost:8000)
// In production, set VITE_API_URL to your backend base URL
const API_BASE = import.meta.env.VITE_API_URL || '';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Dashboard APIs
// Backend route: GET /api/dashboard/
export function getDashboard() {
  return apiClient.get('/api/dashboard/');
}

// Backend route: GET /api/tankers/allocations
export function getAllocations() {
  return apiClient.get('/api/tankers/allocations');
}

// Backend route: POST /api/villages/calculate-all-stress
export function calculateAllStress() {
  return apiClient.post('/api/villages/calculate-all-stress');
}

// Backend route: POST /api/tankers/allocate
export function runAllocation() {
  return apiClient.post('/api/tankers/allocate');
}

// Villages
// Backend route: GET /api/villages/
export function getAllVillages() {
  return apiClient.get('/api/villages/');
}

export default apiClient;
