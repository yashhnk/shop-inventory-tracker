import React, { useEffect, useState } from 'react';
import { Package, AlertTriangle, Clock, TrendingDown } from 'lucide-react';
import Card from '../components/Card';
import MetricCard from '../components/MetricCard';

const Inventory: React.FC = () => {
  const [inventoryItems, setInventoryItems] = useState<any[]>([]);
  const [metrics, setMetrics] = useState({
    total: 0,
    lowStock: 0,
    expiringSoon: 0,
    outOfStock: 0,
  });

  // Fetch data from Flask
  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/spoilage_prediction")
      .then(res => res.json())
      .then(data => {
        setInventoryItems(data);

        // Basic metrics derived from data
        const total = data.length;
        const lowStock = data.filter((item: any) => item.stock < 20 && item.stock > 0).length;
        const expiringSoon = data.filter((item: any) => item.daysLeft <= 5).length;
        const outOfStock = data.filter((item: any) => item.stock === 0).length;

        setMetrics({ total, lowStock, expiringSoon, outOfStock });
      })
      .catch(err => console.error("Error fetching inventory:", err));
  }, []);

  const inventoryMetrics = [
    {
      title: 'Total Items',
      value: metrics.total,
      change: '+3%',
      isPositive: true,
      icon: Package,
      color: 'bg-blue-500'
    },
    {
      title: 'Low Stock',
      value: metrics.lowStock,
      change: '-12%',
      isPositive: true,
      icon: AlertTriangle,
      color: 'bg-amber-500'
    },
    {
      title: 'Expiring Soon',
      value: metrics.expiringSoon,
      change: '+8%',
      isPositive: false,
      icon: Clock,
      color: 'bg-red-500'
    },
    {
      title: 'Out of Stock',
      value: metrics.outOfStock,
      change: '-40%',
      isPositive: true,
      icon: TrendingDown,
      color: 'bg-gray-500'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good': return 'bg-green-100 text-green-800';
      case 'low-stock': return 'bg-amber-100 text-amber-800';
      case 'expiring': return 'bg-red-100 text-red-800';
      case 'out-of-stock': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDaysColor = (days: number) => {
    if (days <= 3) return 'text-red-600 font-semibold';
    if (days <= 7) return 'text-amber-600 font-medium';
    return 'text-green-600';
  };

  const getStatus = (item: any) => {
    if (item.stock === 0) return 'out-of-stock';
    if (item.stock < 20) return 'low-stock';
    if (item.daysLeft <= 5) return 'expiring';
    return 'good';
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Inventory Monitoring</h1>
        <p className="text-gray-600 mt-2">Track stock levels, expiry dates, and inventory health (Live Data)</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {inventoryMetrics.map((metric, index) => (
          <MetricCard key={index} {...metric} />
        ))}
      </div>

      <Card title="Current Inventory" subtitle="Live stock monitoring with expiry tracking">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stock</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Days Left</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Spoilage Risk</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {inventoryItems.map((item, index) => (
                <tr key={index} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{item.product}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{item.stock || 'N/A'}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={getDaysColor(item.daysLeft)}>
                      {item.daysLeft} days
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-900">
                    {(item.spoilageRisk * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(getStatus(item))}`}>
                      {getStatus(item).replace('-', ' ')}
                    </span>
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

export default Inventory;
