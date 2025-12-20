/**
 * FareEstimate Component
 * Display estimated fare and distance
 */

'use client';

interface FareEstimateProps {
  rideType: 'moto' | 'car';
  distance?: number; // in kilometers
  estimatedFare?: number; // in XAF
  className?: string;
}

export function FareEstimate({ rideType, distance, estimatedFare, className = '' }: FareEstimateProps) {
  // Calculate fare if not provided
  const baseFare = rideType === 'moto' ? 500 : 1000;
  const perKmRate = rideType === 'moto' ? 200 : 400;
  const calculatedFare = distance ? baseFare + (perKmRate * distance) : baseFare;
  const fare = estimatedFare || calculatedFare;

  return (
    <div className={`bg-bg-secondary rounded-xl p-4 border border-white/10 ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="text-text-secondary text-sm">Estimated Fare</div>
        <div className="text-2xl font-bold text-primary">
          {Math.round(fare).toLocaleString()} XAF
        </div>
      </div>

      {distance && (
        <div className="flex items-center justify-between text-sm">
          <div className="text-text-muted">Distance</div>
          <div className="text-text-secondary font-medium">
            {distance.toFixed(1)} km
          </div>
        </div>
      )}

      <div className="mt-3 pt-3 border-t border-white/10">
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Final fare may vary based on traffic and route</span>
        </div>
      </div>
    </div>
  );
}

export default FareEstimate;
