import React, { useEffect, useState } from 'react';
// @ts-ignore
import Plot from 'plotly.js-dist';
import { postJson } from '../utils/api';
import { mockSST, mockDepth } from '../utils/mock';

const OceanData: React.FC = () => {
  const [sstData, setSstData] = useState<any>(null);
  const [depthData, setDepthData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Try to fetch SST data using forecast endpoint
        try {
          const sstJson = await postJson<any>(
            '/api/v1/forecast',
            { use_default_data: true, format: 'future_interactive', future_days: 365 }
          );
          setSstData(sstJson);
        } catch (error) {
          console.log('SST API not available, using mock data');
          setSstData(mockSST());
        }

        // Try to fetch depth data using ocean depth-profile endpoint
        try {
          const depthJson = await postJson<any>(
            '/api/v1/ocean/depth-profile',
            { use_default_data: true, parameter: 'combined', format: 'interactive' }
          );
          // Handle the structured response format
          if (depthJson.plot_data) {
            setDepthData({
              data: depthJson.plot_data.data,
              layout: depthJson.plot_data.layout
            });
          } else {
            setDepthData(depthJson);
          }
        } catch (error) {
          console.log('Depth API not available, using mock data');
          setDepthData(mockDepth());
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (!loading && sstData) {
      Plot.newPlot('sst-chart', sstData.data, sstData.layout, {
        responsive: true,
        displayModeBar: false
      });
    }
  }, [sstData, loading]);

  useEffect(() => {
    if (!loading && depthData) {
      Plot.newPlot('depth-chart', depthData.data, depthData.layout, {
        responsive: true,
        displayModeBar: false
      });
    }
  }, [depthData, loading]);

  // Mock generators moved to utils/mock

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#00C9D9] mx-auto mb-4"></div>
          <p className="text-white/80">Loading ocean data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-white mb-4 bg-gradient-to-r from-white via-[#00C9D9] to-white bg-clip-text text-transparent">
          Ocean Environmental Monitoring
        </h1>
        <p className="text-white/80 text-lg max-w-2xl mx-auto leading-relaxed">
          Real-time and forecasted ocean conditions for marine ecosystem analysis
        </p>
      </div>

      <div className="space-y-12">
        {/* SST Forecast Section */}
        <div className="backdrop-blur-md bg-white/10 rounded-2xl p-8 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
            <span className="text-3xl mr-3">🌊</span>
            Sea Surface Temperature Forecast
          </h2>
          <div className="bg-white/5 rounded-xl p-6 border border-white/10">
            <div id="sst-chart" style={{ height: '400px' }}></div>
          </div>
        </div>

        {/* Depth Profiles Section */}
        <div className="backdrop-blur-md bg-white/10 rounded-2xl p-8 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
            <span className="text-3xl mr-3">📊</span>
            Ocean Depth Profiles
          </h2>
          <div className="bg-white/5 rounded-xl p-6 border border-white/10">
            <div id="depth-chart" style={{ height: '500px' }}></div>
          </div>
          <div className="mt-6 grid md:grid-cols-3 gap-4">
            <div className="backdrop-blur-md bg-white/10 rounded-lg p-4 border border-white/10">
              <h3 className="text-lg font-semibold text-[#2ECC71] mb-2">Chlorophyll</h3>
              <p className="text-white/70 text-sm">Indicates phytoplankton abundance and primary productivity</p>
            </div>
            <div className="backdrop-blur-md bg-white/10 rounded-lg p-4 border border-white/10">
              <h3 className="text-lg font-semibold text-[#F1C40F] mb-2">pH Level</h3>
              <p className="text-white/70 text-sm">Ocean acidity levels affecting marine life</p>
            </div>
            <div className="backdrop-blur-md bg-white/10 rounded-lg p-4 border border-white/10">
              <h3 className="text-lg font-semibold text-[#FF6B6B] mb-2">Salinity</h3>
              <p className="text-white/70 text-sm">Salt concentration affecting water density and circulation</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OceanData;
