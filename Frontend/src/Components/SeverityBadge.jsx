const styles = {
  CRITICAL: 'bg-red-100 text-red-700 ring-1 ring-red-300',
  HIGH:     'bg-orange-100 text-orange-700 ring-1 ring-orange-300',
  MEDIUM:   'bg-yellow-100 text-yellow-700 ring-1 ring-yellow-300',
  LOW:      'bg-green-100 text-green-700 ring-1 ring-green-300',
};

export default function SeverityBadge({ severity }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${styles[severity] || styles.LOW}`}>
      {severity}
    </span>
  );
}