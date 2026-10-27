// Owner: Person 3
// Purpose: Privacy warning banner displayed when Nebius cloud provider is active

import React from 'react';

interface BannerProps {
  provider: string;
}

export const Banner: React.FC<BannerProps> = ({ provider }) => {
  if (provider.toLowerCase() !== 'nebius') {
    return null;
  }

  return (
    <aside className="privacy-banner" id="nebius-privacy-banner" role="alert">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <span className="privacy-banner-badge">Privacy Notice</span>
        <span>Prompts leave this machine — Connected to Nebius Token Factory (NVIDIA Nemotron).</span>
      </div>
      <span style={{ opacity: 0.85, fontSize: '0.8rem' }}>Cloud Inference Active</span>
    </aside>
  );
};
