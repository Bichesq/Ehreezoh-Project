/**
 * RideTypeSelector Component
 * Select between Moto and Car rides
 */

'use client';

interface RideTypeSelectorProps {
  selected: 'moto' | 'car';
  onChange: (type: 'moto' | 'car') => void;
  className?: string;
}

export function RideTypeSelector({ selected, onChange, className = '' }: RideTypeSelectorProps) {
  return (
    <div className={`flex gap-3 ${className}`}>
      {/* Moto Option */}
      <button
        type="button"
        onClick={() => onChange('moto')}
        className={`flex-1 p-4 rounded-xl border-2 transition-all duration-200 ${
          selected === 'moto'
            ? 'border-primary bg-primary/10 shadow-lg shadow-primary/20'
            : 'border-white/10 bg-bg-secondary hover:border-primary/50'
        }`}
      >
        <div className="flex flex-col items-center gap-2">
          <div className="text-4xl">🏍️</div>
          <div className="font-semibold text-text-primary">Moto</div>
          <div className="text-xs text-text-secondary">Quick & Affordable</div>
          <div className="text-sm font-bold text-primary">~500 XAF</div>
        </div>
      </button>

      {/* Car Option */}
      <button
        type="button"
        onClick={() => onChange('car')}
        className={`flex-1 p-4 rounded-xl border-2 transition-all duration-200 ${
          selected === 'car'
            ? 'border-primary bg-primary/10 shadow-lg shadow-primary/20'
            : 'border-white/10 bg-bg-secondary hover:border-primary/50'
        }`}
      >
        <div className="flex-col items-center gap-2">
          <div className="text-4xl">🚗</div>
          <div className="font-semibold text-text-primary">Car</div>
          <div className="text-xs text-text-secondary">Comfortable</div>
          <div className="text-sm font-bold text-primary">~1,000 XAF</div>
        </div>
      </button>
    </div>
  );
}

export default RideTypeSelector;
