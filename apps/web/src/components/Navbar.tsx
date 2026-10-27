// Owner: Person 3
// Purpose: Header navigation bar with provider badge and reset sample data trigger

import React from 'react';

interface NavbarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
  provider: string;
  onResetData: () => void;
  isResetting: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onTabChange,
  provider,
  onResetData,
  isResetting,
}) => {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'activity', label: 'Activity Log' },
    { id: 'approvals', label: 'Approvals' },
    { id: 'documents', label: 'Documents' },
    { id: 'briefing', label: 'Briefing' },
    { id: 'permissions', label: 'Permissions' },
    { id: 'settings', label: 'Settings' },
  ];

  const getBadgeClass = (p: string) => {
    switch (p.toLowerCase()) {
      case 'nebius':
        return 'badge badge-nebius';
      case 'local':
        return 'badge badge-local';
      default:
        return 'badge badge-mock';
    }
  };

  return (
    <header className="header-nav">
      <div className="brand">
        <h1 className="brand-title" style={{ margin: 0 }}>
          Miko
        </h1>
        <span className="brand-badge">Local-First Agent</span>
        <span className={getBadgeClass(provider)} id="active-provider-badge">
          {provider} mode
        </span>
      </div>

      <nav className="nav-links" id="main-navigation">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            id={`nav-${tab.id}`}
            className={`nav-btn ${currentTab === tab.id ? 'active' : ''}`}
            onClick={() => onTabChange(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <div className="nav-actions">
        <button
          id="btn-reset-sample-data"
          className="btn btn-secondary"
          onClick={onResetData}
          disabled={isResetting}
        >
          {isResetting ? 'Resetting...' : 'Reset sample data'}
        </button>
      </div>
    </header>
  );
};
