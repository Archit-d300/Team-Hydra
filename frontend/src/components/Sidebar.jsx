import React from 'react';
import { LayoutDashboard, Map, TrendingUp, Truck, Settings, Droplets } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'map', label: 'Regions Map', icon: Map },
    { id: 'forecasts', label: 'ML Forecasts', icon: TrendingUp },
    { id: 'allocation', label: 'Tanker Allocation', icon: Truck },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="sidebar">
      <div className="brand-title">
        <Droplets className="brand-icon" size={28} />
        <span className="text-gradient">PRERNA 18.0</span>
      </div>
      
      <nav className="nav-links">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <div 
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon className="nav-icon" size={20} />
              <span>{item.label}</span>
            </div>
          );
        })}
      </nav>
      
      <div className="sidebar-footer">
        <div className="nav-item">
          <div className="avatar">A</div>
          <div>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)'}}>Admin User</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)'}}>System Operator</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
