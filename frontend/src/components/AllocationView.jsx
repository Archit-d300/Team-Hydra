import React, { useEffect, useState } from 'react';
import { Truck, MapPin, Clock } from 'lucide-react';
import { getOptimizedRoutes } from '../services/api';

export default function AllocationView() {
    const [routeInfo, setRouteInfo] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await getOptimizedRoutes();
                if (response.data.success) {
                    setRouteInfo(response.data);
                }
            } catch (error) {
                console.error("Failed to fetch routes:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="glass-panel" style={{ height: 'calc(100vh - 120px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <h2 style={{ color: 'var(--text-secondary)' }}>Loading AI Route Optimizer...</h2>
            </div>
        );
    }

    if (!routeInfo || !routeInfo.route || routeInfo.route.length === 0) {
        return (
            <div className="glass-panel" style={{ height: 'calc(100vh - 120px)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                <Truck size={48} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
                <h2 style={{ color: 'var(--text-secondary)' }}>No Emergency Routing Needed Today</h2>
                <p style={{ color: 'var(--text-muted)' }}>{routeInfo?.message || "All regions are stable."}</p>
            </div>
        );
    }

    return (
        <div className="dashboard-grid">
            <div className="glass-panel stat-card" style={{ gridColumn: 'span 12', padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h2 style={{ margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <Truck color="var(--accent-primary)" />
                        Active Dispatch Route
                    </h2>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                        Greedy Nearest-Neighbor Optimization • Start: {routeInfo.depot}
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '2rem', textAlign: 'right' }}>
                    <div>
                        <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Stops</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{routeInfo.villages_in_route}</div>
                    </div>
                    <div>
                        <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Est. Travel</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{routeInfo.estimated_travel_hours} hrs</div>
                    </div>
                    <div>
                        <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Distance</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{routeInfo.total_distance_km} km</div>
                    </div>
                </div>
            </div>

            <div className="glass-panel chart-card" style={{ gridColumn: 'span 12', padding: '1.5rem' }}>
                <div className="card-header">
                    <h3 className="card-title">Stop Sequence</h3>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {routeInfo.route.map((stop, i) => (
                        <div key={i} style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '1rem',
                            borderRadius: 'var(--radius-sm)',
                            background: 'rgba(255,255,255,0.03)',
                            border: i === 0 ? '1px solid var(--accent-primary)' : '1px solid var(--glass-border)'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <div style={{
                                    width: '32px', height: '32px',
                                    borderRadius: '50%',
                                    background: 'var(--bg-dark)',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    fontWeight: 'bold', border: '1px solid var(--glass-border-highlight)'
                                }}>
                                    {i + 1}
                                </div>
                                <div>
                                    <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{stop.name}</div>
                                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                        <MapPin size={12} /> {stop.distance_from_last_km} km from previous stop
                                    </div>
                                </div>
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                                <div style={{ textAlign: 'center' }}>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Score</div>
                                    <div style={{ fontWeight: 'bold', color: stop.severity === 'CRITICAL' ? 'var(--accent-danger)' : 'var(--accent-warning)' }}>
                                        {stop.stress_score}/10
                                    </div>
                                </div>
                                <div style={{ textAlign: 'center' }}>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Tankers Req</div>
                                    <div style={{ fontWeight: 'bold', color: 'var(--text-primary)' }}>
                                        {stop.tankers_needed}
                                    </div>
                                </div>
                                <button className="action-btn" style={{ width: 'auto', padding: '0 1rem', borderRadius: 'var(--radius-md)' }}>
                                    Dispatch
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
