import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Inventory from './pages/Inventory';
import ExpiryAlerts from './pages/ExpiryAlerts';
import MLPredictions from './pages/MLPredictions';
import AutoReorder from './pages/AutoReorder';

export type Page = 'dashboard' | 'products' | 'inventory' | 'suppliers' | 'sales' | 'expiry-alerts' | 'ml-predictions' | 'auto-reorder';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'products':
        return <Products />;
      case 'inventory':
        return <Inventory />;
      case 'suppliers':
        return <Suppliers />;
      case 'sales':
        return <Sales />;
      case 'expiry-alerts':
        return <ExpiryAlerts />;
      case 'ml-predictions':
        return <MLPredictions />;
      case 'auto-reorder':
        return <AutoReorder />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar 
        currentPage={currentPage} 
        onPageChange={setCurrentPage}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      <main className={`flex-1 overflow-auto transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
        <div className="p-6">
          {renderPage()}
        </div>
      </main>
    </div>
  );
}

export default App;