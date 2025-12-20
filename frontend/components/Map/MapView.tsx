/**
 * MapView Component
 * Interactive map using Leaflet
 * 
 * NOTE: Temporarily disabled until Leaflet packages install successfully
 */

'use client';

// import { useEffect } from 'react';
// import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
// import L from 'leaflet';
// import 'leaflet/dist/leaflet.css';

export interface MapMarker {
  position: [number, number];
  label?: string;
  icon?: 'default' | 'pickup' | 'dropoff' | 'driver';
}

interface MapViewProps {
  center: [number, number];
  zoom?: number;
  markers?: MapMarker[];
  onMapClick?: (lat: number, lng: number) => void;
  className?: string;
  height?: string;
}

// Temporary placeholder until Leaflet installs
export function MapView({
  center,
  zoom = 13,
  markers = [],
  onMapClick,
  className = '',
  height = '400px',
}: MapViewProps) {
  return (
    <div 
      className={`relative bg-bg-secondary rounded-xl border border-white/10 flex items-center justify-center ${className}`} 
      style={{ height }}
    >
      <div className="text-center p-8">
        <div className="text-6xl mb-4">🗺️</div>
        <div className="text-text-primary font-semibold mb-2">Map Loading...</div>
        <div className="text-text-secondary text-sm">
          Interactive map will appear here once Leaflet installs
        </div>
        {center && (
          <div className="mt-4 text-xs text-text-muted">
            Center: {center[0].toFixed(4)}, {center[1].toFixed(4)}
          </div>
        )}
        {markers.length > 0 && (
          <div className="mt-2 text-xs text-text-muted">
            {markers.length} marker(s) ready
          </div>
        )}
      </div>
    </div>
  );
}

export default MapView;
