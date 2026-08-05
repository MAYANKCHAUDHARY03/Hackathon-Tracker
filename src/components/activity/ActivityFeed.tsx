import { useState, useEffect } from 'react';
import { activityApi, type ActivityEvent } from '@/api/activityApi';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { formatDistanceToNow } from 'date-fns';
import { Activity, Clock } from 'lucide-react';

interface ActivityFeedProps {
  projectId: string;
}

export function ActivityFeed({ projectId }: ActivityFeedProps) {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [activities, setActivities] = useState<ActivityEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function loadActivities() {
      if (!activeWorkspaceId) return;
      setIsLoading(true);
      try {
        const data = await activityApi.getProjectActivities(activeWorkspaceId, projectId);
        setActivities(data);
      } catch (err: any) {
        setError(err instanceof Error ? err : new Error('Failed to load activity'));
      } finally {
        setIsLoading(false);
      }
    }
    
    loadActivities();
    
    // In a real app we might use websockets or polling here for live updates
    // For now we just poll every 5 seconds
    const interval = setInterval(loadActivities, 5000);
    return () => clearInterval(interval);
  }, [activeWorkspaceId, projectId]);

  if (isLoading && activities.length === 0) {
    return (
      <div className="p-4 border-l border-border h-full bg-muted/20 w-80 shrink-0">
        <h3 className="font-semibold text-sm mb-4 flex items-center gap-2">
          <Activity size={16} /> Activity
        </h3>
        <div className="text-sm text-muted-foreground animate-pulse">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-4 border-l border-border h-full bg-muted/20 w-80 shrink-0 overflow-y-auto">
      <h3 className="font-semibold text-sm mb-4 flex items-center gap-2">
        <Activity size={16} /> Activity
      </h3>
      {error && <div className="text-xs text-destructive mb-4">Failed to load activity</div>}
      
      <div className="flex flex-col gap-4">
        {activities.map(activity => {
          const actionText = activity.action.replace('_', ' ');
          const entity = activity.entity_type;
          
          return (
            <div key={activity.id} className="flex gap-3 text-sm">
              <div className="mt-0.5 shrink-0">
                <div className="w-2 h-2 rounded-full bg-primary" />
              </div>
              <div className="flex flex-col gap-1">
                <div className="text-foreground">
                  <span className="font-medium">{activity.user_id}</span> {actionText} {entity}
                </div>
                <div className="text-xs text-muted-foreground flex items-center gap-1">
                  <Clock size={12} />
                  {formatDistanceToNow(new Date(activity.created_at), { addSuffix: true })}
                </div>
              </div>
            </div>
          );
        })}
        {activities.length === 0 && (
          <div className="text-sm text-muted-foreground text-center py-8">
            No activity yet.
          </div>
        )}
      </div>
    </div>
  );
}
