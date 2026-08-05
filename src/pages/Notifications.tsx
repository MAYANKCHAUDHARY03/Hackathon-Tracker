import { NotificationList } from "@/components/notifications/NotificationList";

export default function NotificationsPage() {
  return (
    <div className="p-6 md:p-8 space-y-6 max-w-4xl mx-auto w-full">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Notifications</h1>
        <p className="text-muted-foreground">
          Stay updated with your hackathons, team activities, and evaluations.
        </p>
      </div>
      
      <div className="bg-card border border-border/50 rounded-xl p-6 shadow-sm">
        <NotificationList />
      </div>
    </div>
  );
}
