export default function StatsCard({ label, value, icon, color }) {
  const borderColors = {
    blue:   'border-blue-500',
    red:    'border-red-500',
    orange: 'border-orange-500',
    green:  'border-green-500',
    yellow: 'border-yellow-500',
  };

  const textColors = {
    blue:   'text-blue-600',
    red:    'text-red-600',
    orange: 'text-orange-600',
    green:  'text-green-600',
    yellow: 'text-yellow-600',
  };

  return (
    <div className={`bg-white rounded-2xl shadow-sm p-6 border-l-4 ${borderColors[color] || borderColors.blue} hover:shadow-md transition-shadow duration-200`}>
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-gray-500">{label}</p>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className={`text-4xl font-extrabold ${textColors[color] || textColors.blue}`}>
        {value ?? '—'}
      </p>
    </div>
  );
}