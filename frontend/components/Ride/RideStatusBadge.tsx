/**
 * RideStatusBadge Component
 * Visual indicator for ride status
 */

'use client';

interface RideStatusBadgeProps {
  status: 'requested' | 'accepted' | 'started' | 'completed' | 'cancelled';
  className?: string;
}

const statusConfig = {
  requested: {
    icon: '🔍',
    label: 'Finding Driver',
    color: 'bg-yellow-500/10 border-yellow-500/50 text-yellow-500',
  },
  accepted: {
    icon: '✅',
    label: 'Driver Assigned',
    color: 'bg-green-500/10 border-green-500/50 text-green-500',
  },
  started: {
    icon: '🚗',
    label: 'En Route',
    color: 'bg-blue-500/10 border-blue-500/50 text-blue-500',
  },
  completed: {
    icon: '🎉',
    label: 'Completed',
    color: 'bg-green-500/10 border-green-500/50 text-green-500',
  },
  cancelled: {
    icon: '❌',
    label: 'Cancelled',
    color: 'bg-red-500/10 border-red-500/50 text-red-500',
  },
};

export function RideStatusBadge({ status, className = '' }: RideStatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border-2 ${config.color} ${className}`}>
      <span className="text-2xl">{config.icon}</span>
      <span className="font-semibold">{config.label}</span>
    </div>
  );
}

export default RideStatusBadge;
