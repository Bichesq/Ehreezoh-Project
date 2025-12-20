/**
 * RideTimeline Component
 * Visual progress tracker for ride status
 */

'use client';

interface RideTimelineProps {
  currentStatus: 'requested' | 'accepted' | 'started' | 'completed' | 'cancelled';
  className?: string;
}

const steps = [
  { key: 'requested', label: 'Requested', icon: '🔍' },
  { key: 'accepted', label: 'Accepted', icon: '✅' },
  { key: 'started', label: 'Started', icon: '🚗' },
  { key: 'completed', label: 'Completed', icon: '🎉' },
];

export function RideTimeline({ currentStatus, className = '' }: RideTimelineProps) {
  const currentIndex = steps.findIndex(step => step.key === currentStatus);

  return (
    <div className={`${className}`}>
      <div className="flex items-center justify-between relative">
        {/* Progress Line */}
        <div className="absolute top-6 left-0 right-0 h-1 bg-white/10">
          <div 
            className="h-full bg-primary transition-all duration-500"
            style={{ width: `${(currentIndex / (steps.length - 1)) * 100}%` }}
          />
        </div>

        {/* Steps */}
        {steps.map((step, index) => {
          const isCompleted = index <= currentIndex;
          const isCurrent = index === currentIndex;

          return (
            <div key={step.key} className="flex flex-col items-center relative z-10">
              {/* Circle */}
              <div 
                className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-300 ${
                  isCompleted
                    ? 'bg-primary border-primary text-white'
                    : 'bg-bg-secondary border-white/20 text-text-muted'
                } ${isCurrent ? 'ring-4 ring-primary/30' : ''}`}
              >
                <span className="text-xl">{step.icon}</span>
              </div>

              {/* Label */}
              <div 
                className={`mt-2 text-xs font-medium ${
                  isCompleted ? 'text-text-primary' : 'text-text-muted'
                }`}
              >
                {step.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default RideTimeline;
