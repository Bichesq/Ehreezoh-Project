/**
 * DriverCard Component
 * Display driver information and vehicle details
 */

'use client';

interface DriverCardProps {
  driver: {
    full_name: string;
    phone_number?: string;
    profile_photo_url?: string;
    average_rating?: number;
    total_rides?: number;
    vehicle_type: 'moto' | 'car';
    vehicle_make?: string;
    vehicle_model?: string;
    vehicle_color?: string;
    vehicle_plate_number?: string;
  };
  eta?: number; // minutes to pickup
  className?: string;
}

export function DriverCard({ driver, eta, className = '' }: DriverCardProps) {
  const vehicleIcon = driver.vehicle_type === 'moto' ? '🏍️' : '🚗';
  const rating = driver.average_rating || 0;
  const totalRides = driver.total_rides || 0;

  return (
    <div className={`bg-bg-secondary rounded-xl p-6 border border-white/10 ${className}`}>
      {/* Driver Info */}
      <div className="flex items-start gap-4 mb-4">
        {/* Avatar */}
        <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center text-2xl flex-shrink-0">
          {driver.profile_photo_url ? (
            <img 
              src={driver.profile_photo_url} 
              alt={driver.full_name}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            '👤'
          )}
        </div>

        {/* Details */}
        <div className="flex-1">
          <h3 className="text-xl font-bold text-text-primary mb-1">
            {driver.full_name}
          </h3>
          
          {/* Rating */}
          <div className="flex items-center gap-2 mb-2">
            <div className="flex items-center gap-1">
              <span className="text-yellow-500">⭐</span>
              <span className="text-text-primary font-semibold">
                {rating.toFixed(1)}
              </span>
            </div>
            <span className="text-text-muted text-sm">
              ({totalRides} rides)
            </span>
          </div>

          {/* ETA */}
          {eta !== undefined && (
            <div className="flex items-center gap-2 text-primary">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium">
                Arriving in {eta} {eta === 1 ? 'minute' : 'minutes'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Vehicle Info */}
      <div className="bg-bg-primary rounded-lg p-4 border border-white/10">
        <div className="flex items-center gap-3">
          <div className="text-3xl">{vehicleIcon}</div>
          <div className="flex-1">
            <div className="text-text-primary font-semibold">
              {driver.vehicle_make} {driver.vehicle_model}
            </div>
            <div className="text-text-secondary text-sm">
              {driver.vehicle_color} • {driver.vehicle_plate_number}
            </div>
          </div>
        </div>
      </div>

      {/* Contact Button */}
      {driver.phone_number && (
        <button
          onClick={() => window.open(`tel:${driver.phone_number}`)}
          className="w-full mt-4 bg-primary hover:bg-primary-light text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
          </svg>
          Call Driver
        </button>
      )}
    </div>
  );
}

export default DriverCard;
