import React from 'react';
import { cn } from '../../lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}

export function Card({ title, icon, action, className, children, ...props }: CardProps) {
  return (
    <div 
      className={cn(
        "bg-[var(--color-bg-card)] border border-[var(--color-border-card)] rounded-lg overflow-hidden flex flex-col",
        className
      )}
      {...props}
    >
      <div className="px-4 py-3 border-b border-[var(--color-border-card)] flex items-center justify-between bg-black/20">
        <div className="flex items-center gap-2">
          {icon && <span className="text-[var(--color-neon-green)] opacity-80">{icon}</span>}
          <h3 className="text-sm font-semibold tracking-wider uppercase text-gray-300">{title}</h3>
        </div>
        {action && <div>{action}</div>}
      </div>
      <div className="p-4 flex-1 flex flex-col overflow-hidden">
        {children}
      </div>
    </div>
  );
}
