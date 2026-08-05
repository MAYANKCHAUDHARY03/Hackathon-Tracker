import type { Notification } from "@/api/notifications";
import { formatDistanceToNow } from "date-fns";
import { Link } from "react-router-dom";
import { Check, Info, AlertTriangle, AlertCircle, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface NotificationItemProps {
  notification: Notification;
  onMarkRead: (id: string) => void;
}

const typeConfig: Record<string, { icon: any, color: string, bg: string }> = {
  announcement: { icon: Info, color: "text-blue-500", bg: "bg-blue-500/10" },
  assignment: { icon: Check, color: "text-green-500", bg: "bg-green-500/10" },
  reminder: { icon: Calendar, color: "text-amber-500", bg: "bg-amber-500/10" },
  alert: { icon: AlertTriangle, color: "text-red-500", bg: "bg-red-500/10" },
  default: { icon: AlertCircle, color: "text-muted-foreground", bg: "bg-muted" },
};

export function NotificationItem({ notification, onMarkRead }: NotificationItemProps) {
  const config = typeConfig[notification.type] || typeConfig.default;
  const Icon = config.icon;

  const content = (
    <div className={cn(
      "flex items-start gap-4 p-4 rounded-lg border transition-colors",
      notification.is_read ? "bg-background border-border/50 opacity-70" : "bg-card border-primary/20 shadow-sm"
    )}>
      <div className={cn("mt-1 flex h-8 w-8 items-center justify-center rounded-full shrink-0", config.bg, config.color)}>
        <Icon className="h-4 w-4" />
      </div>
      
      <div className="flex-1 space-y-1 overflow-hidden">
        <div className="flex items-center justify-between gap-2">
          <p className={cn("text-sm font-medium leading-none truncate", notification.is_read ? "text-muted-foreground" : "text-foreground")}>
            {notification.title}
          </p>
          <span className="text-xs text-muted-foreground shrink-0">
            {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
          </span>
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2">
          {notification.message}
        </p>
      </div>

      {!notification.is_read && (
        <Button 
          variant="ghost" 
          size="icon" 
          className="h-8 w-8 shrink-0 rounded-full hover:bg-primary hover:text-primary-foreground text-muted-foreground"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onMarkRead(notification.id);
          }}
          title="Mark as read"
        >
          <Check className="h-4 w-4" />
        </Button>
      )}
    </div>
  );

  if (notification.link) {
    return (
      <Link to={notification.link} className="block group">
        {content}
      </Link>
    );
  }

  return content;
}
