import React, { useEffect, useState } from 'react';
import { TrendingUp, AlertCircle, Droplets } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getPredictions } from '../services/api';

export default function ForecastsView() {
    const [forecastData, setForecastData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await getPredictions(7);
                if (response.data.success) {
                    setForecastData(response.data);
                }
            } catch (error) {
                console.error("Failed to fetch ML predictions:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="glass-panel" style={{ height: 'calc(100vh - 120px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <h2 style={{ color: 'var(--text-secondary)' }}>Loading Linear Regression Models...</h2>
            </div>
        );
    }

    if (!forecastData || !forecastData.forecasts) {
        return (
            <div className="glass-panel" style={{ height: 'calc(100vh - 120px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <h2 style={{ color: 'var(--text-secondary)' }}>No ML Forecast data found</h2>
            </div>
        );
    }

    return (
        <div className="dashboard-grid">
            <div className="glass-panel stat-card" style={{ gridColumn: 'span 12', padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h2 style={{ margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <TrendingUp color="var(--accent-secondary)" />
                        7-Day Drought Susceptibility Forecast
                    </h2>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                        Linear Regression Model evaluating Rainfall Deficits vs. Groundwater Depletion
                    </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Critical Alerts</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: forecastData.critical_alerts?.length > 0 ? 'var(--accent-danger)' : 'var(--accent-success)' }}>
                        {forecastData.critical_alerts?.length || 0}
                    </div>
                </div>
            </div>

            <div className="glass-panel chart-card" style={{ gridColumn: 'span 12', padding: '1.5rem', display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.5rem' }}>
                {forecastData.forecasts.map((forecast, i) => (
                    <div key={i} style={{
                        gridColumn: 'span 4',
                        background: 'var(--bg-input)',
                        borderRadius: 'var(--radius-md)',
                        padding: '1.25rem',
                        border: '1px solid var(--glass-border)'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                            <div>
                                <h3 style={{ margin: 0, fontSize: '1.125rem' }}>{forecast.village}</h3>
                                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{forecast.district}</div>
                            </div>
                            <span style={{
                                padding: '0.25rem 0.5rem',
                                borderRadius: 'var(--radius-sm)',
                                fontSize: '0.75rem',
                                fontWeight: 600,
                                backgroundColor: forecast.max_severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                                color: forecast.max_severity === 'CRITICAL' ? 'var(--accent-danger)' : 'var(--accent-primary)'
                            }}>
                                {forecast.trend.toUpperCase()}
                            </span>
                        </div>

                        <div style={{ height: '140px', width: '100%', marginBottom: '1rem' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={forecast.predictions.map((p, idx) => ({ day: idx + 1, score: p.predicted_stress_score }))}>
                                    <XAxis dataKey="day" hide />
                                    <YAxis domain={[0, 10]} hide />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--glass-border)', fontSize: '0.75rem', padding: '4px' }}
                                        labelFormatter={() => ''}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="score"
                                        stroke={forecast.trend === 'worsening' ? "var(--accent-danger)" : "var(--accent-secondary)"}
                                        strokeWidth={2}
                                        dot={false}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
                            <div style={{ color: 'var(--text-secondary)' }}>Max Expected:</div>
                            <div style={{ fontWeight: 'bold', color: forecast.max_predicted_score >= 8 ? 'var(--accent-danger)' : 'var(--text-primary)' }}>
                                {forecast.max_predicted_score.toFixed(1)}/10
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
