import React, { useEffect, useState } from 'react';
import { Droplets, Activity, AlertTriangle, CloudRain, Shield } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getDashboardData } from '../services/api';

function TrendingIcon({ up }) {
    return up ? (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline><polyline points="16 7 22 7 22 13"></polyline></svg>
    ) : (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"></polyline><polyline points="16 17 22 17 22 11"></polyline></svg>
    );
}

export default function Dashboard() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await getDashboardData();
                if (response.data.success) {
                    setData(response.data.data ? response.data.data : response.data);
                }
            } catch (error) {
                console.error("Failed to fetch dashboard data:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="glass-panel" style={{ height: 'calc(100vh - 120px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <h2 style={{ color: 'var(--text-secondary)' }}>Loading Dashboard API Data...</h2>
            </div>
        );
    }

    // Fallback defaults
    const summary = data?.summary || {};
    const tankers = data?.tankers || {};
    const villages = data?.villages || [];

    // Quick calculations for average
    let totalScore = 0;
    let assessedCount = 0;
    villages.forEach(v => {
        if (v.stress_today?.score) {
            totalScore += v.stress_today.score;
            assessedCount++;
        }
    });
    const avgStress = assessedCount > 0 ? (totalScore / assessedCount).toFixed(1) : 0;

    // Aggregate daily forecast data (simplified average across all villages for charting)
    const chartDataMap = {};
    villages.forEach(v => {
        if (v.forecast_3day && v.forecast_3day.length > 0) {
            v.forecast_3day.forEach(f => {
                if (!chartDataMap[f.day]) chartDataMap[f.day] = { count: 0, total: 0 };
                chartDataMap[f.day].total += f.predicted_stress;
                chartDataMap[f.day].count += 1;
            });
        }
    });
    const aggregatedForecast = Object.keys(chartDataMap).map(day => ({
        day: `Day ${day}`,
        stress: parseFloat((chartDataMap[day].total / chartDataMap[day].count).toFixed(1))
    }));

    // Find critical regions (sorted by anomaly or risk)
    const criticalVillages = villages
        .filter(v => v.stress_today?.severity === 'CRITICAL' || v.anomaly_detected || v.days_to_gw_danger < 7)
        .sort((a, b) => (b.stress_today?.score || 0) - (a.stress_today?.score || 0))
        .slice(0, 5);

    return (
        <div className="dashboard-grid">
            {/* KPI Cards */}
            <div className="glass-panel stat-card">
                <div className="stat-header">
                    <div>
                        <h3 className="stat-title">Avg Water Stress</h3>
                        <div className="stat-value">{avgStress} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ 10</span></div>
                    </div>
                    <div className="icon-wrapper warning">
                        <Activity size={24} />
                    </div>
                </div>
                <div className="stat-trend trend-up">
                    <TrendingIcon up /> Computed from {assessedCount} villages
                </div>
            </div>

            <div className="glass-panel stat-card">
                <div className="stat-header">
                    <div>
                        <h3 className="stat-title">Worsening / Anomalous</h3>
                        <div className="stat-value">{summary.worsening_villages || 0}</div>
                    </div>
                    <div className="icon-wrapper danger">
                        <AlertTriangle size={24} />
                    </div>
                </div>
                <div className="stat-trend trend-down">
                    <Shield size={16} /> {summary.villages_with_anomalies || 0} GW Anomalies found
                </div>
            </div>

            <div className="glass-panel stat-card">
                <div className="stat-header">
                    <div>
                        <h3 className="stat-title">Deployed Tankers</h3>
                        <div className="stat-value">{tankers.deployed || 0}<span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ {tankers.total || 0}</span></div>
                    </div>
                    <div className="icon-wrapper primary">
                        <Droplets size={24} />
                    </div>
                </div>
                <div className="stat-trend trend-up">
                    <TrendingIcon up /> {tankers.available || 0} remaining at depot
                </div>
            </div>

            <div className="glass-panel stat-card">
                <div className="stat-header">
                    <div>
                        <h3 className="stat-title">Overall Risk Levels</h3>
                        <div className="stat-value" style={{ display: 'flex', gap: '8px' }}>
                            <span style={{ color: 'var(--accent-danger)' }}>{summary.CRITICAL || 0}</span>
                            <span style={{ color: 'var(--text-muted)' }}>|</span>
                            <span style={{ color: 'var(--accent-warning)' }}>{summary.HIGH || 0}</span>
                        </div>
                    </div>
                    <div className="icon-wrapper secondary">
                        <Activity size={24} />
                    </div>
                </div>
                <div className="stat-trend style={{color: 'var(--text-secondary)'}}">
                    Crit / High severity counts today
                </div>
            </div>

            {/* Main Chart Region */}
            <div className="glass-panel chart-card">
                <div className="card-header">
                    <h3 className="card-title">Average ML 3-Day Stress Forecast</h3>
                    <button className="action-btn" style={{ width: 'auto', padding: '0 1rem', borderRadius: 'var(--radius-sm)' }}>
                        Detailed Forecasts
                    </button>
                </div>
                <div style={{ height: '300px', width: '100%' }}>
                    {aggregatedForecast.length > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={aggregatedForecast} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorStress" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="var(--accent-warning)" stopOpacity={0.8} />
                                        <stop offset="95%" stopColor="var(--accent-warning)" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" vertical={false} />
                                <XAxis dataKey="day" stroke="var(--text-secondary)" tick={{ fill: 'var(--text-secondary)' }} axisLine={false} tickLine={false} />
                                <YAxis domain={[0, 10]} stroke="var(--text-secondary)" tick={{ fill: 'var(--text-secondary)' }} axisLine={false} tickLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--glass-border)', borderRadius: 'var(--radius-sm)' }}
                                    itemStyle={{ color: 'var(--text-primary)' }}
                                />
                                <Area type="monotone" dataKey="stress" stroke="var(--accent-warning)" fillOpacity={1} fill="url(#colorStress)" strokeWidth={3} />
                            </AreaChart>
                        </ResponsiveContainer>
                    ) : (
                        <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                            No ML forecast data available. Try seeding the database.
                        </div>
                    )}
                </div>
            </div>

            {/* Side Alerts Panel */}
            <div className="glass-panel aside-card" style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="card-header" style={{ marginBottom: '1rem' }}>
                    <h3 className="card-title">Critical Attention Needed</h3>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', overflowY: 'auto', flex: 1, paddingRight: '0.5rem' }}>
                    {criticalVillages.length > 0 ? criticalVillages.map((v, i) => (
                        <div key={i} style={{ padding: '1rem', borderRadius: 'var(--radius-sm)', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--glass-border)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                                <div style={{ fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    {v.name}
                                    {(v.anomaly_detected || v.stress_today?.severity === 'CRITICAL') && <AlertTriangle size={14} color="var(--accent-danger)" />}
                                </div>
                                <span style={{
                                    padding: '0.25rem 0.75rem',
                                    borderRadius: 'var(--radius-full)',
                                    fontSize: '0.75rem',
                                    fontWeight: 600,
                                    backgroundColor: v.stress_today?.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                                    color: v.stress_today?.severity === 'CRITICAL' ? 'var(--accent-danger)' : 'var(--accent-warning)'
                                }}>
                                    {v.stress_today?.score ? v.stress_today.score.toFixed(1) : 'N/A'}/10
                                </span>
                            </div>

                            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                                {v.anomaly_detected && <div style={{ color: 'var(--accent-danger)' }}>• Groundwater drop detected</div>}
                                <div>• Rainfall Trend: <span style={{ textTransform: 'capitalize' }}>{v.rainfall_trend}</span></div>
                                {v.days_to_gw_danger && v.days_to_gw_danger < 7 && <div>• GW Danger in {v.days_to_gw_danger} days</div>}
                                <div>• Tankers required: <strong>{v.stress_today?.tankers_needed || 0}</strong></div>
                            </div>
                        </div>
                    )) : (
                        <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '2rem' }}>
                            All regions are stable.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
