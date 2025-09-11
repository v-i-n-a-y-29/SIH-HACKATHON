import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import OceanData from './pages/OceanData';
import Fisheries from './pages/Fisheries';
import Biodiversity from './pages/Biodiversity';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/ocean" element={<OceanData />} />
          <Route path="/fisheries" element={<Fisheries />} />
          <Route path="/biodiversity" element={<Biodiversity />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;