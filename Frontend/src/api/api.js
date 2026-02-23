import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Dashboard APIs
export function getDashboard() {
  return apiClient.get('/dashboard');
}

export function getAllocations() {
  return apiClient.get('/allocations');
}

export function calculateAllStress() {
  return apiClient.post('/calculate-stress');
}

export function runAllocation() {
  return apiClient.post('/run-allocation');
}

// Villages
export function getAllVillages() {
  return apiClient.get('/villages');
}

export default apiClient;