import { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  color?: string;
  variant?: 'primary' | 'secondary' | 'neutral';
  className?: string;
}

const variantStyles: Record<'primary' | 'secondary' | 'neutral', string> = {
  primary: 'bg-primary-500/10 text-primary-300 border-primary-500/30',
  secondary: 'bg-secondary-500/10 text-secondary-300 border-secondary-500/30',
  neutral: 'bg-neutral-500/10 text-neutral-300 border-neutral-500/30',
};

export function Badge({ children, color, variant = 'neutral', className = '' }: BadgeProps) {
  if (color) {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${className}`}
        style={{ backgroundColor: `${color}1a`, borderColor: `${color}66`, color }}
      >
        {children}
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
