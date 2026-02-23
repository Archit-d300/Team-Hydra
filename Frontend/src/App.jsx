import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './Components/Navbar';
import Dashboard from './Pages/Dashboard';
import VillagesMap from './Pages/VillagesMap';
import Allocations from './Pages/Allocations';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-100">
        <Navbar />
        <main className="max-w-7xl mx-auto px-6 py-8">
          <Routes>
            <Route path="/"            element={<Dashboard />} />
            <Route path="/map"         element={<VillagesMap />} />
            <Route path="/allocations" element={<Allocations />} />
          </Routes>
        </main>
        <footer className="text-center text-xs text-gray-400 py-6">
          Hack A Cause · PRERNA 18.0 · SDG 6 Clean Water & Sanitation · Ramdeobaba University
        </footer>
      </div>
    </BrowserRouter>
  );
}