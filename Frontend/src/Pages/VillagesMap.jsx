import { useEffect, useState } from 'react';
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from '@react-google-maps/api';
import { getAllVillages } from '../api/api';
import SeverityBadge from '../Components/SeverityBadge';

const SEVERITY_ICONS = {
    CRITICAL: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
    HIGH: 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png',
    MEDIUM: 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
    LOW: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
};

export default function VillagesMap() {
    const [villages, setVillages] = useState([]);
    const [selected, setSelected] = useState(null);
    const [filter, setFilter] = useState('ALL');

    const { isLoaded } = useJsApiLoader({
        googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_KEY
    });

    useEffect(() => {
        getAllVillages().then(res => setVillages(res.data.data));
    }, []);

    const filtered = filter === 'ALL'
        ? villages
        : villages.filter(v => v.stress_info?.severity === filter);

    if (!isLoaded) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin text-5xl mb-4">🌀</div>
                    <p className="text-gray-500">Loading map...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto">

            {/* Header */}
            <div className="mb-6">
                <h2 className="text-3xl font-extrabold text-blue-950">
                    🗺️ Village Risk Map
                </h2>
                <p className="text-gray-500 mt-1 text-sm">
                    Vidarbha, Maharashtra · Click any marker for details
                </p>
            </div>

            {/* Filter + Legend */}
            <div className="bg-white rounded-2xl shadow-sm p-4 mb-4 flex flex-wrap items-center gap-3">
                <span className="text-sm font-semibold text-gray-600">Filter:</span>
                {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(f => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${filter === f
                            ? 'bg-blue-700 text-white shadow'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                    >
                        {f}
                    </button>
                ))}
                <div className="ml-auto flex gap-4 text-xs text-gray-500">
                    {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(s => (
                        <div key={s} className="flex items-center gap-1">
                            <img
                                src={SEVERITY_ICONS[s]}
                                alt={s}
                                className="w-4 h-4"
                            />
                            {s}
                        </div>
                    ))}
                </div>
            </div>

            {/* Stats strip */}
            <div className="grid grid-cols-4 gap-3 mb-4">
                {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(s => {
                    const count = villages.filter(v => v.stress_info?.severity === s).length;
                    const colors = {
                        CRITICAL: 'bg-red-50 border-red-200 text-red-700',
                        HIGH: 'bg-orange-50 border-orange-200 text-orange-700',
                        MEDIUM: 'bg-yellow-50 border-yellow-200 text-yellow-700',
                        LOW: 'bg-green-50 border-green-200 text-green-700',
                    };
                    return (
                        <div key={s} className={`rounded-xl border p-3 text-center ${colors[s]}`}>
                            <p className="text-2xl font-extrabold">{count}</p>
                            <p className="text-xs font-semibold mt-0.5">{s}</p>
                        </div>
                    );
                })}
            </div>

            {/* Map */}
            <div className="rounded-2xl overflow-hidden shadow-md">
                <GoogleMap
                    mapContainerStyle={{ width: '100%', height: '520px' }}
                    center={{ lat: 20.7096, lng: 78.0 }}
                    zoom={7}
                    options={{
                        styles: [{ featureType: 'poi', stylers: [{ visibility: 'off' }] }],
                        disableDefaultUI: false,
                    }}
                >
                    {filtered.map(v => (
                        <Marker
                            key={v.id}
                            position={{ lat: parseFloat(v.lat), lng: parseFloat(v.lng) }}
                            icon={SEVERITY_ICONS[v.stress_info?.severity] || SEVERITY_ICONS.LOW}
                            onClick={() => setSelected(v)}
                        />
                    ))}

                    {selected && (
                        <InfoWindow
                            position={{ lat: parseFloat(selected.lat), lng: parseFloat(selected.lng) }}
                            onCloseClick={() => setSelected(null)}
                        >
                            <div className="p-2 min-w-[180px]">
                                <h3 className="font-bold text-gray-800 text-base mb-2">{selected.name}</h3>
                                <div className="space-y-1 text-sm text-gray-600">
                                    <p>📍 <b>{selected.district}</b> District</p>
                                    <p>👥 {selected.population?.toLocaleString()} people</p>
                                    {selected.stress_info ? (
                                        <>
                                            <p>💧 Stress Score: <b className="text-gray-800">{selected.stress_info.stress_score}/10</b></p>
                                            <p>🚛 Tankers Needed: <b className="text-gray-800">{selected.stress_info.tankers_needed}</b></p>
                                            <div className="mt-2">
                                                <SeverityBadge severity={selected.stress_info.severity} />
                                            </div>
                                        </>
                                    ) : (
                                        <p className="text-gray-400 italic">No stress data yet</p>
                                    )}
                                </div>
                            </div>
                        </InfoWindow>
                    )}
                </GoogleMap>
            </div>
        </div>
    );
}