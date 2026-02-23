import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
  const { pathname } = useLocation();

  const links = [
    { to: '/', label: '📊 Dashboard' },
    { to: '/map', label: '🗺️ Village Map' },
    { to: '/allocations', label: '🚛 Allocations' },
  ];

  return (
    <nav className="bg-blue-950 shadow-lg">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-8">
        <span className="text-white font-bold text-xl tracking-tight">
          🚰 Drought Warning System
        </span>
        <div className="flex gap-6">
          {links.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`text-sm font-medium transition-colors duration-200 ${
                pathname === link.to
                  ? 'text-white border-b-2 border-blue-400 pb-1'
                  : 'text-blue-300 hover:text-white'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
        <div className="ml-auto">
          <span className="text-xs text-blue-400 bg-blue-900 px-3 py-1 rounded-full">
            PRERNA 18.0 · SDG 6
          </span>
        </div>
      </div>
    </nav>
  );
}