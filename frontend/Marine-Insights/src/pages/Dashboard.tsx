import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-white mb-4 bg-gradient-to-r from-white via-[#00C9D9] to-white bg-clip-text text-transparent">
          Unified Marine Dashboard Prototype
        </h1>
        <p className="text-white/80 text-lg max-w-2xl mx-auto leading-relaxed">
          Comprehensive marine data insights for environmental monitoring, fisheries management, and biodiversity conservation
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8 mb-16">
        {/* Ocean Data Module */}
        <Link to="/ocean" className="group">
          <div className="backdrop-blur-md bg-white/10 rounded-2xl p-8 border border-white/20 hover:bg-white/15 hover:border-[#00C9D9]/30 hover:shadow-2xl hover:shadow-[#00C9D9]/20 transition-all duration-300 transform hover:-translate-y-2">
            <div className="text-center">
              <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">🌊</div>
              <h3 className="text-2xl font-bold text-white mb-3">Ocean Data</h3>
              <p className="text-white/70 mb-6 leading-relaxed">
                Sea surface temperature forecasts, depth profiles, and environmental monitoring
              </p>
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="flex justify-between items-center text-sm text-white/60">
                  <span>Ocean Forecast</span>
                  <span className="text-[#2ECC71]">Active</span>
                </div>
                <div className="h-16 mt-2 bg-gradient-to-r from-[#007B82]/30 to-[#00C9D9]/30 rounded flex items-end space-x-1 p-2">
                  {[...Array(8)].map((_, i) => (
                    <div
                      key={i}
                      className="bg-[#00C9D9]/60 rounded-sm flex-1"
                      style={{ height: `${Math.random() * 100}%` }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </Link>

        {/* Fisheries Module */}
        <Link to="/fisheries" className="group">
          <div className="backdrop-blur-md bg-white/10 rounded-2xl p-8 border border-white/20 hover:bg-white/15 hover:border-[#F1C40F]/30 hover:shadow-2xl hover:shadow-[#F1C40F]/20 transition-all duration-300 transform hover:-translate-y-2">
            <div className="text-center">
              <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">🐟</div>
              <h3 className="text-2xl font-bold text-white mb-3">Fisheries</h3>
              <p className="text-white/70 mb-6 leading-relaxed">
                Stock forecasting, overfishing monitoring, and species classification
              </p>
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="flex justify-between items-center text-sm text-white/60">
                  <span>Fish Stocks</span>
                  <span className="text-[#F1C40F]">Moderate</span>
                </div>
                <div className="h-16 mt-2 bg-gradient-to-r from-[#F1C40F]/20 to-[#FF6B6B]/20 rounded flex items-center justify-center">
                  <div className="w-12 h-12 bg-[#F1C40F]/40 rounded-full flex items-center justify-center">
                    <div className="w-6 h-6 bg-[#F1C40F] rounded-full"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Link>

        {/* Biodiversity Module */}
        <Link to="/biodiversity" className="group">
          <div className="backdrop-blur-md bg-white/10 rounded-2xl p-8 border border-white/20 hover:bg-white/15 hover:border-[#2ECC71]/30 hover:shadow-2xl hover:shadow-[#2ECC71]/20 transition-all duration-300 transform hover:-translate-y-2">
            <div className="text-center">
              <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">🧬</div>
              <h3 className="text-2xl font-bold text-white mb-3">Biodiversity</h3>
              <p className="text-white/70 mb-6 leading-relaxed">
                eDNA analysis, species identification, and invasive species monitoring
              </p>
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="flex justify-between items-center text-sm text-white/60 mb-3">
                  <span>eDNA Analysis</span>
                  <span className="text-[#2ECC71]">Clean</span>
                </div>
                <div className="space-y-2">
                  {['Atlantic Cod', 'Harbor Seal', 'Blue Mussel'].map((species, i) => (
                    <div key={i} className="flex justify-between text-xs text-white/50">
                      <span>{species}</span>
                      <span>{Math.floor(Math.random() * 30 + 70)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </Link>
      </div>

      {/* Footer */}
      <div className="text-center">
        <div className="backdrop-blur-md bg-white/5 rounded-xl p-6 border border-white/10">
          <p className="text-white/60 text-sm">
            <span className="font-medium text-[#00C9D9]">Prototype for Hackathon</span> – Marine Data Insights
          </p>
          <p className="text-white/40 text-xs mt-2">
            Empowering marine research and conservation through advanced data analytics
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;