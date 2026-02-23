import React from 'react';
import { Bell, Search } from 'lucide-react';

export default function Header({ title }) {
    return (
        <header className="header">
            <div>
                <h1 className="header-title">{title}</h1>
                <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Maharashtra Drought Warning System</p>
            </div>

            <div className="header-actions">
                <div style={{ position: 'relative' }}>
                    <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                    <input
                        type="text"
                        placeholder="Search villages, regions..."
                        style={{
                            background: 'var(--bg-input)',
                            border: '1px solid var(--glass-border)',
                            borderRadius: 'var(--radius-full)',
                            padding: '0.625rem 1rem 0.625rem 2.5rem',
                            color: 'var(--text-primary)',
                            width: '240px',
                            outline: 'none',
                            fontFamily: 'inherit'
                        }}
                    />
                </div>

                <button className="action-btn">
                    <Bell size={18} />
                </button>
            </div>
        </header>
    );
}
