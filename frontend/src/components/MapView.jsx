import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import { getDashboardData } from '../services/api';

// Create a custom icon function based on severity
const getMarkerColor = (severity) => {
    switch (severity) {
        case 'CRITICAL': return '#ef4444'; // Red
        case 'HIGH': return '#f59e0b'; // Orange
        case 'MEDIUM': return '#3b82f6'; // Blue
        default: return '#10b981'; // Green
    }
};

export default function MapView() {
    const [villages, setVillages] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await getDashboardData();
                if (response.data.success) {
                    setVillages(response.data.data ? response.data.data.villages : response.data.villages || []);
                }
            } catch (error) {
                console.error("Failed to fetch map data:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="glass-panel" style={{ height: 'calc(100vh - 120px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
                    <h2>Loading Regional Data...</h2>
                </div>
            </div>
        );
    }

    // Default center to Vidarbha region approximate center
    const center = villages.length > 0 ? [villages[0].lat, villages[0].lng] : [20.9374, 77.7796];

    return (
        <div className="glass-panel" style={{ height: 'calc(100vh - 120px)', padding: 0, overflow: 'hidden' }}>
            <MapContainer center={center} zoom={8} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    className="map-tiles-dark"
                />

                {villages.map((village) => {
                    const severity = village.stress_today?.severity || 'LOW';
                    const color = getMarkerColor(severity);

                    return (
                        <CircleMarker
                            key={village.id}
                            center={[village.lat, village.lng]}
                            radius={8}
                            pathOptions={{ fillColor: color, color: color, fillOpacity: 0.7 }}
                        >
                            <Popup className="custom-popup">
                                <div style={{ padding: '4px' }}>
                                    <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 'bold' }}>{village.name}</h3>
                                    <div style={{ fontSize: '12px', margin: '4px 0' }}><strong>District:</strong> {village.district}</div>
                                    <div style={{ fontSize: '12px', margin: '4px 0' }}>
                                        <strong>Stress Level:</strong>
                                        <span style={{ color, marginLeft: '4px', fontWeight: 'bold' }}>{severity}</span>
                                    </div>
                                    {village.anomaly_detected && (
                                        <div style={{ color: '#ef4444', fontSize: '12px', marginTop: '8px', fontWeight: 'bold' }}>
                                            ⚠️ Groundwater Anomaly Detected
                                        </div>
                                    )}
                                    <div style={{ fontSize: '12px', margin: '8px 0 0 0', display: 'flex', justifyContent: 'space-between' }}>
                                        <span>Tankers Req:</span>
                                        <strong>{village.stress_today?.tankers_needed || 0}</strong>
                                    </div>
                                </div>
                            </Popup>
                        </CircleMarker>
                    );
                })}
            </MapContainer>

            {/* Add some CSS for dark mode map tiles if you prefer */}
            <style>{`
        .map-tiles-dark {
          filter: brightness(0.6) invert(1) contrast(3) hue-rotate(200deg) saturate(0.3) brightness(0.7);
        }
        .leaflet-popup-content-wrapper, .leaflet-popup-tip {
          background: rgba(30, 41, 59, 0.9);
          backdrop-filter: blur(10px);
          color: #f8fafc;
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
        }
        .leaflet-container a.leaflet-popup-close-button {
          color: #94a3b8;
        }
      `}</style>
        </div>
    );
}
