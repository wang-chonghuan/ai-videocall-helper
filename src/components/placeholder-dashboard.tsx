import React from 'react';

const PlaceholderDashboardContent: React.FC = () => {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Dashboard Home</h1>
      <p>This is the main dashboard area.</p>
      <div className="mt-8 grid auto-rows-min gap-4 md:grid-cols-3">
        <div className="aspect-video rounded-xl bg-muted/50 border animate-pulse" />
        <div className="aspect-video rounded-xl bg-muted/50 border animate-pulse" />
        <div className="aspect-video rounded-xl bg-muted/50 border animate-pulse" />
      </div>
    </div>
  );
};

export default PlaceholderDashboardContent; 