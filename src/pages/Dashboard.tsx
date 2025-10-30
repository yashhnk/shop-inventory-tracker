import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Package, Warehouse, TrendingUp, Calendar, Brain } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import Card from '../components/Card';

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState({
    totalProducts: 0,
    lowStock: 0,
    monthlySales: 0
  });

  const [demandForecast, setDemandForecast] = useState<any[]>([]);
  const [spoilageRisk, setSpoilageRisk] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch all backend data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsRes, demandRes, spoilageRes] = await Promise.all([
          axios.get('http://localhost:5000/api/dashboard_metrics'),
          axios.get('http://localhost:5000/api/demand_forecast'),
          axios.get('http://localhost:5000/api/spoilage_prediction')
        ]);
        setMetrics(metricsRes.data);
        setDemandForecast(demandRes.data);
        setSpoilageRisk(spoilageRes.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="text-center text-gray-600 mt-10">Loading data...</div>;
  }

  const metricCards = [
    {
      title: 'Total Products',
      value: metrics.totalProducts.toLocaleString(),
      icon: Package,
      color: 'bg-blue-500'
    },
    {
      title: 'Low Stock Items',
      value: metrics.lowStock.toString(),
      icon: Warehouse,
      color: 'bg-amber-500'
    },
    {
      title: 'Total Sales Volume',
      value: metrics.monthlySales.toLocaleString(),
      icon: TrendingUp,
      color: 'bg-green-500'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Welcome back! Here's what's happening with your inventory.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-white px-4 py-2 rounded-lg border border-gray-200">
            <Calendar className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">
              Today:{' '}
              {new Date().toLocaleDateString('en-IN', {
                day: 'numeric',
                month: 'short',
                year: 'numeric'
              })}
            </span>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {metricCards.map((metric, index) => (
          <MetricCard
            key={index}
            title={metric.title}
            value={metric.value}
            icon={metric.icon}
            color={metric.color}
          />
        ))}
      </div>

      {/* ML Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sales Forecast (Product Names Only) */}
        <Card
          title="Sales Forecast (Top 10)"
          action={
            <div className="flex items-center space-x-2 text-purple-600">
              <Brain className="w-4 h-4" />
              <span className="text-sm font-medium">AI Powered</span>
            </div>
          }
        >
          <div className="space-y-3">
            {demandForecast.map((item, i) => (
              <div
                key={i}
                className="bg-green-50 p-3 rounded-lg border border-green-200 text-gray-800 font-medium"
              >
                {item.productName || item.product}
              </div>
            ))}
          </div>
        </Card>

        {/* Spoilage Risk (Product Names Only) */}
        <Card title="Spoilage Risk (Top 10)">
          <div className="space-y-3">
            {spoilageRisk.map((item, i) => (
              <div
                key={i}
                className="bg-amber-50 p-3 rounded-lg border border-amber-200 text-gray-800 font-medium"
              >
                {item.product}
              </div>
            ))}
          </div>
        </Card>

        <Card title="Discount Suggestions" subtitle="Based on spoilage risk">
          <div className="bg-gradient-to-r from-blue-100 to-blue-200 p-4 rounded-lg">
            <h4 className="font-medium text-blue-800">Suggested Discount Range</h4>
            <p className="text-2xl font-bold text-blue-900 mt-1">5–15%</p>
            <p className="text-sm text-blue-700">For high-risk expiring products</p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
