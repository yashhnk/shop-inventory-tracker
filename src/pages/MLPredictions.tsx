import React, { useEffect, useState } from "react";
import axios from "axios";

export default function MLPredictions() {
  const [demandForecasts, setDemandForecasts] = useState<any[]>([]);
  const [spoilagePredictions, setSpoilagePredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get("http://127.0.0.1:5000/api/demand_forecast"),
      axios.get("http://127.0.0.1:5000/api/spoilage_prediction"),
    ])
      .then(([demandRes, spoilageRes]) => {
        const demandData = demandRes.data.map((item: any) => ({
          product: item.product || item.Category || item.item || "Unknown",
          predictedDemand:
            item.predictedDemand || item.Predicted_Demand || item.prediction || 0,
        }));

        const spoilageData = spoilageRes.data.map((item: any) => ({
          product: item.product || item.Category || item.item || "Unknown",
          spoilageRisk:
            item.spoilageRisk ||
            item.Spoilage_Risk ||
            item.risk ||
            0,
        }));

        // ✅ Remove duplicates by product name
        const uniqueDemand = demandData.filter(
          (v, i, a) => a.findIndex(t => t.product === v.product) === i
        );
        const uniqueSpoilage = spoilageData.filter(
          (v, i, a) => a.findIndex(t => t.product === v.product) === i
        );

        setDemandForecasts(uniqueDemand);
        setSpoilagePredictions(uniqueSpoilage);
      })
      .catch((err) => console.error("Error fetching data:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-center mt-6">Loading predictions...</p>;

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-2xl font-bold text-center text-blue-600">
        Smart Inventory ML Predictions
      </h1>

      {/* Demand Forecast Section */}
      <div className="bg-white shadow-lg rounded-2xl p-6">
        <h2 className="text-xl font-semibold mb-4">📈 Demand Forecast</h2>
        <table className="w-full text-left border border-gray-200">
          <thead className="bg-blue-100">
            <tr>
              <th className="p-3">Product</th>
              <th className="p-3">Predicted Demand</th>
            </tr>
          </thead>
          <tbody>
            {demandForecasts.length > 0 ? (
              demandForecasts.map((item, i) => (
                <tr key={i} className="border-b hover:bg-gray-50">
                  <td className="p-3 font-medium text-gray-800">{item.product}</td>
                  <td className="p-3 text-gray-700">{item.predictedDemand.toFixed(2)}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="p-3 text-center text-gray-500" colSpan={2}>
                  No demand forecast data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Spoilage Prediction Section */}
      <div className="bg-white shadow-lg rounded-2xl p-6">
        <h2 className="text-xl font-semibold mb-4">🧪 Spoilage Risk Prediction</h2>
        <table className="w-full text-left border border-gray-200">
          <thead className="bg-blue-100">
            <tr>
              <th className="p-3">Product</th>
              <th className="p-3">Spoilage Risk</th>
            </tr>
          </thead>
          <tbody>
            {spoilagePredictions.length > 0 ? (
              spoilagePredictions.map((item, i) => (
                <tr key={i} className="border-b hover:bg-gray-50">
                  <td className="p-3 font-medium text-gray-800">{item.product}</td>
                  <td className="p-3 text-gray-700">
                    {(item.spoilageRisk * 100).toFixed(1)}%
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="p-3 text-center text-gray-500" colSpan={2}>
                  No spoilage data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
