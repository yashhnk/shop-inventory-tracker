import React from 'react';
import { 
  LayoutDashboard, 
  Package, 
  Warehouse, 
  Users, 
  TrendingUp, 
  AlertTriangle, 
  Brain, 
  ShoppingCart,
  Menu,
  X
} from 'lucide-react';
import type { Page } from '../App';

interface SidebarProps {
  currentPage: Page;
  onPageChange: (page: Page) => void;
  isOpen: boolean;
  onToggle: () => void;
}

interface NavItem {
  id: Page;
  label: string;
  icon: React.ComponentType<any>;
  badge?: string;
}

const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'products', label: 'Products', icon: Package },
  { id: 'inventory', label: 'Inventory', icon: Warehouse },
  { id: 'expiry-alerts', label: 'Expiry Alerts', icon: AlertTriangle, badge: '3' },
  { id: 'ml-predictions', label: 'ML Predictions', icon: Brain },
  { id: 'auto-reorder', label: 'Auto Reorder', icon: ShoppingCart, badge: '5' },
];

const Sidebar: React.FC<SidebarProps> = ({ currentPage, onPageChange, isOpen, onToggle }) => {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden" onClick={onToggle} />
      )}
      
      <div className={`fixed left-0 top-0 h-full bg-white border-r border-gray-200 shadow-lg z-30 transition-all duration-300 ${
        isOpen ? 'w-64' : 'w-16'
      }`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          {isOpen && (
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Package className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-gray-900">SmartInventory</h1>
                <p className="text-xs text-gray-500">FMCG Tracker</p>
              </div>
            </div>
          )}
          <button
            onClick={onToggle}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => onPageChange(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200 group ${
                  isActive 
                    ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-blue-600' : 'text-gray-500 group-hover:text-gray-700'}`} />
                {isOpen && (
                  <>
                    <span className="font-medium">{item.label}</span>
                    {item.badge && (
                      <span className="ml-auto bg-red-500 text-white text-xs rounded-full px-2 py-1">
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </button>
            );
          })}
        </nav>

        {/* Bottom section */}
        {isOpen && (
          <div className="absolute bottom-4 left-4 right-4">
            <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">JD</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">John Doe</p>
                  <p className="text-xs text-gray-500">Admin</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Sidebar;