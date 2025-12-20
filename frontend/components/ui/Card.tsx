import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  glass?: boolean;
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  className = '',
  glass = true 
}) => {
  const baseStyles = 'rounded-card p-6';
  const glassStyles = glass 
    ? 'bg-bg-secondary/70 backdrop-blur-glass border border-white/10 shadow-glass'
    : 'bg-bg-secondary border border-white/10';
  
  return (
    <div className={`${baseStyles} ${glassStyles} ${className}`}>
      {children}
    </div>
  );
};
