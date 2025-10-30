import React, { useEffect, useState } from 'react';
import { ShoppingCart, AlertCircle, CheckCircle, Clock, Package } from 'lucide-react';
import Card from '../components/Card';

const AutoReorder: React.FC = () => {
  const [pendingOrders, setPendingOrders] = useState<any[]>([]);
  const [recentOrders, setRecentOrders] = useState<any[]>([]);
  const [autoReorders, setAutoReorders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [autoRes, pendingRes, recentRes] = await Promise.all([
          fetch('http://localhost:5000/api/auto_reorder'),
          fetch('http://localhost:5000/api/pending_orders'),
          fetch('http://localhost:5000/api/recent_orders'),
        ]);

        const autoData = await autoRes.json();
        const pendingData = await pendingRes.json();
        const recentData = await recentRes.json();

        setAutoReorders(autoData);
        setPendingOrders(pendingData);
        setRecentOrders(recentData);
      } catch (error) {
        console.error('Error fetching reorder data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'delivered': return 'bg-green-100 text-green-800';
      case 'in-transit': return 'bg-blue-100 text-blue-800';
      case 'confirmed': return 'bg-amber-100 text-amber-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'delivered': return <CheckCircle className="w-4 h-4" />;
      case 'in-transit': return <Package className="w-4 h-4" />;
      case 'confirmed': return <Clock className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  const totalPendingAmount = pendingOrders.reduce((sum, o) => sum + (o.UnitPrice || 0) * (o.QuantityOrdered || 0), 0);

  if (loading) {
    return <div className="text-center py-20 text-gray-600">Loading reorder data...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Auto Reorder System</h1>
          <p className="text-gray-600 mt-2">
            Automated purchase orders based on stock levels and ML predictions
          </p>
        </div>
        <div className="flex space-x-3">
          <button className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors">
            <CheckCircle className="w-4 h-4" />
            <span>Approve All</span>
          </button>
          <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
            <ShoppingCart className="w-4 h-4" />
            <span>Create Manual Order</span>
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-red-600 mb-1">Pending Orders</p>
              <p className="text-2xl font-bold text-red-900">{pendingOrders.length}</p>
            </div>
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
        </div>

        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-amber-600 mb-1">Total Value</p>
              <p className="text-2xl font-bold text-amber-900">
                ₹{(totalPendingAmount / 1000).toFixed(1)}k
              </p>
            </div>
            <ShoppingCart className="w-8 h-8 text-amber-500" />
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-blue-600 mb-1">Critical Items</p>
              <p className="text-2xl font-bold text-blue-900">
                {autoReorders.filter(i => i.urgency === 'critical').length}
              </p>
            </div>
            <AlertCircle className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600 mb-1">Auto Generated</p>
              <p className="text-2xl font-bold text-green-900">100%</p>
            </div>
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">AI</span>
            </div>
          </div>
        </div>
      </div>

      {/* Auto Reorder List */}
      <Card title="Auto Generated Reorders" subtitle="Products automatically reordered">
        <div className="space-y-4">
          {autoReorders.map((item: any) => (
            <div key={item.ProductID} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Package className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{item.ProductName}</h3>
                    <p className="text-sm text-gray-600">{item.SupplierName}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 text-xs font-medium rounded-full border ${getUrgencyColor(item.urgency)}`}>
                  {item.urgency} urgency
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Current Stock</p>
                  <p className="text-lg font-bold text-red-600">{item.StockQuantity}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Reorder Level</p>
                  <p className="text-lg font-bold text-gray-900">{item.ReorderLevel}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Suggested Qty</p>
                  <p className="text-lg font-bold text-blue-600">{item.suggestedQuantity}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Total Amount</p>
                  <p className="text-lg font-bold text-green-600">₹{item.totalAmount}</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <span>Unit Price: ₹{item.UnitPrice}</span>
                  <span>•</span>
                  <span>Est. Delivery: {item.EstimatedDelivery}</span>
                </div>
                <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                  Approve Order
                </button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Recent Orders Table */}
      <Card title="Recent Orders" subtitle="Order history and tracking">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Supplier</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentOrders.map((order: any) => (
                <tr key={order.orderId} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">{order.orderId}</td>
                  <td className="px-6 py-4">{order.productName}</td>
                  <td className="px-6 py-4">{order.supplier}</td>
                  <td className="px-6 py-4">{order.quantity}</td>
                  <td className="px-6 py-4">₹{order.amount}</td>
                  <td className="px-6 py-4">
                    <span className={`flex items-center space-x-1 px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(order.status)}`}>
                      {getStatusIcon(order.status)}
                      <span>{order.status}</span>
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

export default AutoReorder;
