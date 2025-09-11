import React, { useEffect, useState } from 'react';
// @ts-ignore
import Plot from 'plotly.js-dist';

const OceanData: React.FC = () => {
  const [sstData, setSstData] = useState<any>(null);
  const [depthData, setDepthData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Try to fetch SST data using forecast endpoint
        try {
          const sstResponse = await fetch('http://127.0.0.1:8000/api/v1/forecast', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              use_default_data: true,
              format: 'future_interactive',
              future_days: 365
            })
          });
          const sstJson = await sstResponse.json();
          setSstData(sstJson);
        } catch (error) {
          console.log('SST API not available, using mock data');
          setSstData(getMockSSTData());
        }

        // Try to fetch depth data using ocean depth-profile endpoint
        try {
          const depthResponse = await fetch('http://127.0.0.1:8000/api/v1/ocean/depth-profile', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              use_default_data: true,
              parameter: 'combined',
              format: 'interactive'
            })
          });
          const depthJson = await depthResponse.json();
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
          setDepthData(getMockDepthData());
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

  const getMockSSTData = () => ({
    data: [{
      x: ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06', '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12'],
      y: [12.5, 13.2, 15.8, 18.3, 21.7, 24.2, 26.8, 27.1, 24.5, 20.9, 17.3, 14.1],
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Historical SST',
      line: { color: '#00C9D9', width: 3 },
      marker: { size: 8, color: '#007B82' }
    }, {
      x: ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06'],
      y: [13.8, 14.5, 16.2, 19.1, 22.4, 25.1],
      type: 'scatter',
      mode: 'lines+markers',
      name: 'SST Forecast',
      line: { color: '#F1C40F', width: 3, dash: 'dash' },
      marker: { size: 8, color: '#F1C40F' }
    }],
    layout: {
      title: {
        text: 'Sea Surface Temperature - Historical & Forecast',
        font: { color: 'white', size: 18 }
      },
      xaxis: {
        title: 'Date',
        color: 'white',
        gridcolor: 'rgba(255,255,255,0.1)'
      },
      yaxis: {
        title: 'Temperature (°C)',
        color: 'white',
        gridcolor: 'rgba(255,255,255,0.1)'
      },
      plot_bgcolor: 'rgba(0,0,0,0)',
      paper_bgcolor: 'rgba(0,0,0,0)',
      font: { color: 'white' }
    }
  });

  const getMockDepthData = () => ({
    data: [
      {
        x: [0, 10, 20, 30, 40, 50, 75, 100],
        y: [2.8, 2.5, 2.2, 1.8, 1.4, 1.0, 0.6, 0.3],
        type: 'scatter',
        mode: 'lines',
        name: 'Chlorophyll (mg/m³)',
        line: { color: '#2ECC71', width: 3 }
      },
      {
        x: [0, 10, 20, 30, 40, 50, 75, 100],
        y: [8.2, 8.1, 7.9, 7.7, 7.5, 7.3, 7.1, 6.9],
        type: 'scatter',
        mode: 'lines',
        name: 'pH Level',
        line: { color: '#F1C40F', width: 3 },
        yaxis: 'y2'
      },
      {
        x: [0, 10, 20, 30, 40, 50, 75, 100],
        y: [34.5, 34.7, 34.9, 35.1, 35.3, 35.5, 35.7, 35.9],
        type: 'scatter',
        mode: 'lines',
        name: 'Salinity (PSU)',
        line: { color: '#FF6B6B', width: 3 },
        yaxis: 'y3'
      }
    ],
    layout: {
      title: {
        text: 'Ocean Depth Profiles',
        font: { color: 'white', size: 18 }
      },
      xaxis: {
        title: 'Depth (m)',
        color: 'white',
        gridcolor: 'rgba(255,255,255,0.1)'
      },
      yaxis: {
        title: 'Chlorophyll (mg/m³)',
        color: '#2ECC71',
        gridcolor: 'rgba(255,255,255,0.1)',
        side: 'left'
      },
      yaxis2: {
        title: 'pH Level',
        color: '#F1C40F',
        overlaying: 'y',
        side: 'right',
        showgrid: false
      },
      yaxis3: {
        title: 'Salinity (PSU)',
        color: '#FF6B6B',
        overlaying: 'y',
        side: 'right',
        position: 0.85,
        showgrid: false
      },
      plot_bgcolor: 'rgba(0,0,0,0)',
      paper_bgcolor: 'rgba(0,0,0,0)',
      font: { color: 'white' },
      legend: {
        bgcolor: 'rgba(255,255,255,0.1)',
        bordercolor: 'rgba(255,255,255,0.2)'
      }
    }
  });

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
