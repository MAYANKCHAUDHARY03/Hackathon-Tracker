import { GlassPanel } from '@/components/ui/glass-panel'

export default function Placeholder({ title }: { title: string }) {
  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-8rem)]">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
        <p className="text-muted-foreground mt-1">This page is under construction.</p>
      </div>
      
      <GlassPanel className="flex-1 flex flex-col items-center justify-center text-muted-foreground gap-4">
        <div className="animate-pulse rounded-full bg-primary/20 p-6">
          <svg className="w-12 h-12 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
        </div>
        <p>Feature coming soon</p>
      </GlassPanel>
    </div>
  )
}
