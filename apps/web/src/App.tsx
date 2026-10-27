// Owner: Person 3
// Purpose: Root React component managing navigation, banner state, and data reset

import React, { useEffect, useState } from 'react';
import { api } from './api/client';
import { Banner } from './components/Banner';
import { Navbar } from './components/Navbar';
import { ActivityLog } from './pages/ActivityLog';
import { Approvals } from './pages/Approvals';
import { Briefing } from './pages/Briefing';
import { Dashboard } from './pages/Dashboard';
import { Documents } from './pages/Documents';
import { Permissions } from './pages/Permissions';
import { Settings } from './pages/Settings';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [provider, setProvider] = useState('mock');
  const [isResetting, setIsResetting] = useState(false);

  useEffect(() => {
    // Load current provider from backend settings or health
    api.getHealth()
      .then((res) => setProvider(res.provider))
      .catch(() => setProvider('mock'));
  }, []);

  const handleResetData = async () => {
    try {
      setIsResetting(true);
      await api.resetSeedData();
      alert('Sample demonstration data successfully reset!');
      // Force refresh current tab state if needed
      window.location.reload();
    } catch (err: any) {
      alert(`Reset failed: ${err.message}`);
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="app-layout" id="miko-app-root">
      {/* Top Banner when provider=nebius: 'Prompts leave this machine' */}
      <Banner provider={provider} />

      <Navbar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        provider={provider}
        onResetData={handleResetData}
        isResetting={isResetting}
      />

      <main className="main-viewport">
        {currentTab === 'dashboard' && (
          <Dashboard provider={provider} onNavigate={setCurrentTab} />
        )}
        {currentTab === 'activity' && <ActivityLog />}
        {currentTab === 'approvals' && <Approvals />}
        {currentTab === 'documents' && <Documents />}
        {currentTab === 'briefing' && <Briefing />}
        {currentTab === 'permissions' && <Permissions />}
        {currentTab === 'settings' && <Settings onProviderChange={setProvider} />}
      </main>
    </div>
  );
};

export default App;
