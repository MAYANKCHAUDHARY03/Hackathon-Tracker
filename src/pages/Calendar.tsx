import { GlassPanel } from '@/components/ui/glass-panel';

export default function Calendar() {
  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Global Calendar</h1>
        <p className="text-muted-foreground">View upcoming rounds and deadlines across all hackathons.</p>
      </div>

      <GlassPanel className="p-6 h-[500px] flex items-center justify-center">
        <p className="text-muted-foreground">Calendar integration coming soon.</p>
      </GlassPanel>
    </div>
  );
}
