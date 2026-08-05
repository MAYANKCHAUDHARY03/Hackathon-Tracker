import { useNotifications } from "@/hooks/useNotifications";
import { NotificationItem } from "./NotificationItem";
import { Button } from "@/components/ui/button";
import { BellOff, CheckCheck } from "lucide-react";

export function NotificationList() {
  const { notifications, markAsRead, markAllAsRead } = useNotifications();

  if (notifications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
        <div className="rounded-full bg-muted p-4 mb-4">
          <BellOff className="h-8 w-8 opacity-50" />
        </div>
        <h3 className="text-lg font-medium text-foreground">No notifications</h3>
        <p className="text-sm mt-1 max-w-sm">You're all caught up! When you receive notifications, they'll show up here.</p>
      </div>
    );
  }

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">
          Your Notifications {unreadCount > 0 && <span className="ml-2 text-sm text-muted-foreground">({unreadCount} unread)</span>}
        </h3>
        
        {unreadCount > 0 && (
          <Button variant="outline" size="sm" onClick={markAllAsRead} className="gap-2">
            <CheckCheck className="h-4 w-4" />
            Mark all as read
          </Button>
        )}
      </div>

      <div className="space-y-2">
        {notifications.map(notification => (
          <NotificationItem 
            key={notification.id} 
            notification={notification} 
            onMarkRead={markAsRead} 
          />
        ))}
      </div>
    </div>
  );
}
