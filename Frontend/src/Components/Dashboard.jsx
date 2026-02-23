import { useEffect, useState } from 'react';
import { getDashboard, calculateAllStress, runAllocation } from '../api/api';
import SeverityBadge from '../Components/SeverityBadge';
import StatsCard from '../Components/StatsCard';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from 'recharts';

const BAR_COLORS = {
  Critical: '#ef4444',
  High:     '#f97316',
  Medium:   '#eab308',
  Low:      '#22c55e',
};

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('');
  const [running, setRunning] = useState(false);

  const fetchData = async () => {
    try {
      const res = await getDashboard();
      setData(res.data.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleRecalculate = async () => {
    setRunning(true);
    setStatus('⏳ Calculating stress scores for all villages...');
    await calculateAllStress();
    setStatus('🚛 Running priority-based tanker allocation...');
    await runAllocation();
    setStatus('✅ Done! Dashboard updated.');
    fetchData();
    setRunning(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin text-5xl mb-4">🌀</div>
          <p className="text-gray-500 font-medium">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const chartData = [
    { name: 'Critical', count: data?.summary.critical_villages   ?? 0 },
    { name: 'High',     count: data?.summary.high_risk_villages  ?? 0 },
    { name: 'Medium',   count: data?.summary.medium_risk_villages ?? 0 },
    { name: 'Low',      count: data?.summary.low_risk_villages   ?? 0 },
  ];

  return (
    <div className="max-w-7xl mx-auto">

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-blue-950">
            📊 Drought Monitoring Dashboard
          </h1>
          <p className="text-gray-500 mt-1 text-sm">
            Real-time Water Stress Monitoring · Vidarbha, Maharashtra
          </p>
        </div>
        <button
          onClick={handleRecalculate}
          disabled={running}
          className={`flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-white shadow-md transition-all duration-200 ${
            running
              ? 'bg-blue-300 cursor-not-allowed'
              : 'bg-blue-700 hover:bg-blue-800 active:scale-95'
          }`}
        >
          {running ? '⏳ Running...' : '🔄 Recalculate & Allocate'}
        </button>
      </div>

      {/* Status message */}
      {status && (
        <div className="mb-6 bg-blue-50 border border-blue-200 text-blue-800 px-4 py-3 rounded-xl text-sm font-medium">
          {status}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mb-8">
        <StatsCard label="Total Villages"     value={data?.summary.total_villages}       icon="🏘️" color="blue"   />
        <StatsCard label="Critical Villages"  value={data?.summary.critical_villages}    icon="🚨" color="red"    />
        <StatsCard label="High Risk"          value={data?.summary.high_risk_villages}   icon="⚠️" color="orange" />
        <StatsCard label="Tankers Deployed"   value={data?.tankers.deployed}             icon="🚛" color="green"  />
      </div>

      {/* Tanker Summary Row */}
      <div className="grid grid-cols-3 gap-5 mb-8">
        <div className="bg-white rounded-2xl shadow-sm p-5 text-center">
          <p className="text-gray-400 text-sm mb-1">Total Tankers</p>
          <p className="text-3xl font-bold text-gray-800">{data?.tankers.total}</p>
        </div>
        <div className="bg-white rounded-2xl shadow-sm p-5 text-center">
          <p className="text-gray-400 text-sm mb-1">Available</p>
          <p className="text-3xl font-bold text-green-600">{data?.tankers.available}</p>
        </div>
        <div className="bg-white rounded-2xl shadow-sm p-5 text-center">
          <p className="text-gray-400 text-sm mb-1">Allocations Today</p>
          <p className="text-3xl font-bold text-blue-600">{data?.allocations_today}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">

        {/* Bar Chart */}
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h3 className="font-bold text-gray-800 text-lg mb-4">
            Village Risk Distribution
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} barSize={40}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 13 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 13 }} />
              <Tooltip
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
              />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={BAR_COLORS[entry.name]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Severity Breakdown */}
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h3 className="font-bold text-gray-800 text-lg mb-4">
            Severity Breakdown
          </h3>
          <div className="space-y-4">
            {[
              { label: 'Critical', value: data?.summary.critical_villages, total: data?.summary.total_villages, color: 'bg-red-500' },
              { label: 'High',     value: data?.summary.high_risk_villages, total: data?.summary.total_villages, color: 'bg-orange-500' },
              { label: 'Medium',   value: data?.summary.medium_risk_villages, total: data?.summary.total_villages, color: 'bg-yellow-500' },
              { label: 'Low',      value: data?.summary.low_risk_villages, total: data?.summary.total_villages, color: 'bg-green-500' },
            ].map(item => {
              const pct = item.total > 0 ? Math.round((item.value / item.total) * 100) : 0;
              return (
                <div key={item.label}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-gray-700">{item.label}</span>
                    <span className="text-gray-500">{item.value} villages ({pct}%)</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full transition-all duration-700 ${item.color}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Village Stress Table */}
      <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="font-bold text-gray-800 text-lg">
            Village Water Stress Index — Today
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600 uppercase text-xs tracking-wider">
              <tr>
                {['Village ID', 'Stress Score', 'Risk Level', 'Tankers Needed'].map(h => (
                  <th key={h} className="px-6 py-3 text-left font-semibold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data?.village_stress_map.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-10 text-center text-gray-400">
                    No stress data yet. Click "Recalculate & Allocate" above.
                  </td>
                </tr>
              ) : data?.village_stress_map.map((v, i) => (
                <tr key={i} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 font-semibold text-gray-700">Village #{v.village_id}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            v.score >= 8 ? 'bg-red-500' :
                            v.score >= 6 ? 'bg-orange-500' :
                            v.score >= 4 ? 'bg-yellow-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${v.score * 10}%` }}
                        />
                      </div>
                      <span className="font-bold text-gray-800">{v.score}/10</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <SeverityBadge severity={v.severity} />
                  </td>
                  <td className="px-6 py-4 font-semibold text-gray-700">
                    {v.tankers_needed} 🚛
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}