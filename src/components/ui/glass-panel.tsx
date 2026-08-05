import type { HTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface GlassPanelProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

export function GlassPanel({ children, className, ...props }: GlassPanelProps) {
  return (
    <div className={cn("glass-panel rounded-2xl p-6", className)} {...props}>
      {children}
    </div>
  )
}
