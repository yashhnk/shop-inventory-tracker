import React, { useEffect, useState } from 'react';
import { AlertTriangle, Clock, Package, Percent } from 'lucide-react';
import Card from '../components/Card';

interface DemandItem {
  product: string;
  predicted_demand: number;
}

interface SpoilageItem {
  product: string;
  spoilage_risk: number;
  days_left: number;
}

interface AlertItem {
  id: string;
  ProductName: string;
  Quantity: number;
  Priority: string;
  SuggestedDiscount: number;
}

const ExpiryAlerts: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const [demandRes, spoilageRes] = await Promise.all([
          fetch('http://localhost:5000/api/demand_forecast'),
          fetch('http://localhost:5000/api/spoilage_prediction')
        ]);

        const demandData: DemandItem[] = await demandRes.json();
        const spoilageData: SpoilageItem[] = await spoilageRes.json();

        const mergedAlerts = spoilageData.map((spoil) => {
          const demand = demandData.find(d => d.product === spoil.product);
          const lowDemand = demand && demand.predicted_demand < 50;

          const priority =
            spoil.spoilage_risk > 0.8 ? 'Critical' :
            spoil.spoilage_risk > 0.6 ? 'High' :
            spoil.spoilage_risk > 0.4 ? 'Medium' : 'Low';

          const discount =
            spoil.spoilage_risk > 0.8 ? 50 :
            spoil.spoilage_risk > 0.6 ? 30 :
            spoil.spoilage_risk > 0.4 ? 15 : 5;

          return {
            id: `ALERT-${spoil.product}`,
            ProductName: spoil.product,
            Quantity: Math.floor(Math.random() * 100) + 10,
            Priority: priority,
            SuggestedDiscount: discount
          };
        });

        setAlerts(mergedAlerts);
      } catch (error) {
        console.error('Error fetching alerts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return <div className="text-center py-10 text-gray-600">Loading expiry alerts...</div>;
  }

  const criticalAlerts = alerts.filter(alert => alert.Priority === 'Critical').length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Expiry Alerts</h1>
        <p className="text-gray-600 mt-2">Generated from spoilage and demand predictions</p>
      </div>

      {/* Summary Boxes */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-red-600 mb-1">Critical Alerts</p>
              <p className="text-2xl font-bold text-red-900">{criticalAlerts}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
        </div>

        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-amber-600 mb-1">Total Alerts</p>
              <p className="text-2xl font-bold text-amber-900">{alerts.length}</p>
            </div>
            <Clock className="w-8 h-8 text-amber-500" />
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-blue-600 mb-1">At Risk Items</p>
              <p className="text-2xl font-bold text-blue-900">
                {alerts.reduce((sum, a) => sum + a.Quantity, 0)}
              </p>
            </div>
            <Package className="w-8 h-8 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Active Alerts Table (no Days Left column) */}
      <Card title="Active Expiry Alerts" subtitle="Predicted using spoilage and demand forecasts">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Suggested Action
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {alerts.map(alert => (
                <tr key={alert.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(alert.Priority)}`}
                    >
                      {alert.Priority}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                    {alert.ProductName}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">{alert.Quantity}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button className="flex items-center space-x-1 px-3 py-1 bg-amber-100 text-amber-700 text-xs rounded-full hover:bg-amber-200 transition-colors">
                      <Percent className="w-3 h-3" />
                      <span>{alert.SuggestedDiscount}% off</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default ExpiryAlerts;
