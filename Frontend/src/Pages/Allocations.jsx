import { useEffect, useState } from "react";
import { getAllocations, runAllocation } from "../api/api";

export default function Allocations() {
  const [allocations, setAllocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  const fetchAllocations = async () => {
    try {
      const res = await getAllocations();
      setAllocations(res?.data?.data ?? []);
    } catch (err) {
      console.error("Allocation fetch error:", err);
      setError("❌ Failed to load allocations");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllocations();
  }, []);

  const handleRunAllocation = async () => {
    try {
      setRunning(true);
      setError("");

      await runAllocation();
      await fetchAllocations();
    } catch (err) {
      console.error("Run allocation error:", err);
      setError("❌ Failed to run allocation");
    } finally {
      setRunning(false);
    }
  };

  // Summary counts
  const totalTankers = allocations.length;
  const uniqueVillages = new Set(
    allocations.map(a => a?.village_id)
  ).size;

  const totalCapacity = allocations.reduce(
    (sum, a) => sum + (a?.tankers?.capacity_liters || 0),
    0
  );

  return (
    <div className="max-w-7xl mx-auto">

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-extrabold text-blue-950">
            🚛 Tanker Allocations
          </h2>
          <p className="text-gray-500 mt-1 text-sm">
            Priority-based dispatch — Today's deployment plan
          </p>
        </div>

        <button
          onClick={handleRunAllocation}
          disabled={running}
          className={`flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-white shadow-md transition-all duration-200 ${
            running
              ? "bg-green-300 cursor-not-allowed"
              : "bg-green-700 hover:bg-green-800 active:scale-95"
          }`}
        >
          {running ? "⏳ Running..." : "▶️ Run Allocation"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm font-medium">
          {error}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-5 mb-8">
        <div className="bg-white rounded-2xl shadow-sm p-6 border-l-4 border-blue-500">
          <p className="text-sm text-gray-500 mb-1">Total Dispatches</p>
          <p className="text-4xl font-extrabold text-blue-600">
            {totalTankers}
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-6 border-l-4 border-green-500">
          <p className="text-sm text-gray-500 mb-1">Villages Covered</p>
          <p className="text-4xl font-extrabold text-green-600">
            {uniqueVillages}
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-6 border-l-4 border-orange-500">
          <p className="text-sm text-gray-500 mb-1">Total Water Capacity</p>
          <p className="text-4xl font-extrabold text-orange-600">
            {totalCapacity.toLocaleString()} L
          </p>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 className="font-bold text-gray-800 text-lg">
            Deployment Details
          </h3>
          <span className="text-sm text-gray-400">
            {new Date().toLocaleDateString("en-IN", {
              dateStyle: "full",
            })}
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-gray-400">
            Loading allocations...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 uppercase text-xs tracking-wider">
                <tr>
                  {[
                    "#",
                    "Tanker Reg. No.",
                    "Capacity",
                    "Assigned Village",
                    "District",
                    "Status",
                  ].map(h => (
                    <th
                      key={h}
                      className="px-6 py-3 text-left font-semibold"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-100">
                {!allocations.length ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <p className="text-gray-400 text-lg mb-2">
                        No allocations for today
                      </p>
                      <p className="text-gray-400 text-sm">
                        Click "Run Allocation" to dispatch tankers based on village stress scores
                      </p>
                    </td>
                  </tr>
                ) : (
                  allocations.map((a, i) => (
                    <tr
                      key={i}
                      className="hover:bg-blue-50 transition-colors"
                    >
                      <td className="px-6 py-4 text-gray-400 font-mono text-xs">
                        {i + 1}
                      </td>

                      <td className="px-6 py-4 font-bold text-gray-800 font-mono">
                        {a?.tankers?.registration_no ?? "-"}
                      </td>

                      <td className="px-6 py-4 text-gray-600">
                        {(a?.tankers?.capacity_liters ?? 0).toLocaleString()} L
                      </td>

                      <td className="px-6 py-4 font-semibold text-gray-800">
                        {a?.villages?.name ?? "-"}
                      </td>

                      <td className="px-6 py-4 text-gray-500">
                        {a?.villages?.district ?? "-"}
                      </td>

                      <td className="px-6 py-4">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-green-100 text-green-700 ring-1 ring-green-300">
                          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                          {a?.status?.toUpperCase() ?? "ASSIGNED"}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}