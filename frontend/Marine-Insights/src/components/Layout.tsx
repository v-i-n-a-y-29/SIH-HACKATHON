import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#001F3F] via-[#003366] to-[#007B82]">
      {/* Navbar */}
      <nav className="backdrop-blur-md bg-white/10 border-b border-white/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/dashboard" className="flex items-center space-x-2 text-white hover:text-[#00C9D9] transition-colors duration-300">
                <span className="text-2xl">🌊</span>
                <span className="text-xl font-bold bg-gradient-to-r from-white to-[#00C9D9] bg-clip-text text-transparent">
                  Marine Insights
                </span>
              </Link>
            </div>
            
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-2 text-white/60 text-sm">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span>API Ready</span>
              </div>
              <Link
                to="/dashboard"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  isActive('/dashboard')
                    ? 'bg-white/20 text-white shadow-lg'
                    : 'text-white/80 hover:text-white hover:bg-white/10'
                }`}
              >
                Dashboard
              </Link>
              <Link
                to="/ocean"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  isActive('/ocean')
                    ? 'bg-white/20 text-white shadow-lg'
                    : 'text-white/80 hover:text-white hover:bg-white/10'
                }`}
              >
                Ocean Data
              </Link>
              <Link
                to="/fisheries"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  isActive('/fisheries')
                    ? 'bg-white/20 text-white shadow-lg'
                    : 'text-white/80 hover:text-white hover:bg-white/10'
                }`}
              >
                Fisheries
              </Link>
              <Link
                to="/biodiversity"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  isActive('/biodiversity')
                    ? 'bg-white/20 text-white shadow-lg'
                    : 'text-white/80 hover:text-white hover:bg-white/10'
                }`}
              >
                Biodiversity
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
};

export default Layout;