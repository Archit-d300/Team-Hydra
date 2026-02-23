import React, { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import MapView from './components/MapView';
import ForecastsView from './components/ForecastsView';
import AllocationView from './components/AllocationView';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'map':
        return <MapView />;
      case 'forecasts':
        return <ForecastsView />;
      case 'allocation':
        return <AllocationView />;
      case 'settings':
        return (
          <div className="glass-panel" style={{ height: 'calc(100vh - 120px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
              <h2>Settings Module</h2>
              <p>Under Construction</p>
            </div>
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="main-content">
        <Header title={activeTab === 'dashboard' ? 'Overview' : activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} />
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
