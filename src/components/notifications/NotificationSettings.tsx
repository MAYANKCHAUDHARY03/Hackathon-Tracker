import { useState, useEffect } from "react";
import { notificationsApi } from "@/api/notifications";
import type { NotificationPreference } from "@/api/notifications";
import { useWorkspaceStore } from "@/store/workspaceStore";
// Mock Switch if not available
const Switch = ({ checked, onCheckedChange }: { checked: boolean, onCheckedChange: () => void }) => (
  <input type="checkbox" checked={checked} onChange={onCheckedChange} className="w-4 h-4 accent-primary" />
);
import { Button } from "@/components/ui/button";
import { Mail, Smartphone, AtSign, CheckSquare, Clock } from "lucide-react";
import { toast } from "sonner";

export function NotificationSettings() {
  const activeWorkspaceId = useWorkspaceStore(s => s.activeWorkspaceId);
  const currentWorkspace = activeWorkspaceId ? { id: activeWorkspaceId as string } : null;
  const [preferences, setPreferences] = useState<NotificationPreference | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (currentWorkspace) {
      loadPreferences();
    }
  }, [currentWorkspace?.id]);

  const loadPreferences = async () => {
    if (!currentWorkspace) return;
    setIsLoading(true);
    try {
      const res = await notificationsApi.getPreferences(currentWorkspace.id);
      setPreferences(res);
    } catch (error) {
      console.error("Failed to load preferences", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = (key: keyof NotificationPreference) => {
    if (!preferences) return;
    setPreferences({ ...preferences, [key]: !preferences[key] });
  };

  const handleSave = async () => {
    if (!currentWorkspace || !preferences) return;
    setIsSaving(true);
    try {
      await notificationsApi.updatePreferences(currentWorkspace.id, preferences);
      toast.success("Preferences updated successfully");
    } catch (error) {
      console.error("Failed to update preferences", error);
      toast.error("Failed to update preferences");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <div className="animate-pulse space-y-4">
      <div className="h-12 bg-muted rounded-md" />
      <div className="h-12 bg-muted rounded-md" />
      <div className="h-12 bg-muted rounded-md" />
    </div>;
  }

  if (!preferences) return null;

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 rounded-lg border bg-card">
          <div className="flex items-center gap-4">
            <div className="p-2 bg-primary/10 rounded-full text-primary">
              <Mail className="h-5 w-5" />
            </div>
            <div>
              <p className="font-medium">Email Notifications</p>
              <p className="text-sm text-muted-foreground">Receive notifications via email</p>
            </div>
          </div>
          <Switch 
            checked={preferences.email_notifications} 
            onCheckedChange={() => handleToggle('email_notifications')} 
          />
        </div>

        <div className="flex items-center justify-between p-4 rounded-lg border bg-card">
          <div className="flex items-center gap-4">
            <div className="p-2 bg-primary/10 rounded-full text-primary">
              <Smartphone className="h-5 w-5" />
            </div>
            <div>
              <p className="font-medium">In-App Notifications</p>
              <p className="text-sm text-muted-foreground">Show notifications in the app</p>
            </div>
          </div>
          <Switch 
            checked={preferences.in_app_notifications} 
            onCheckedChange={() => handleToggle('in_app_notifications')} 
          />
        </div>

        <div className="flex items-center justify-between p-4 rounded-lg border bg-card">
          <div className="flex items-center gap-4">
            <div className="p-2 bg-primary/10 rounded-full text-primary">
              <AtSign className="h-5 w-5" />
            </div>
            <div>
              <p className="font-medium">Mentions</p>
              <p className="text-sm text-muted-foreground">Notify when someone mentions you</p>
            </div>
          </div>
          <Switch 
            checked={preferences.notify_on_mentions} 
            onCheckedChange={() => handleToggle('notify_on_mentions')} 
          />
        </div>

        <div className="flex items-center justify-between p-4 rounded-lg border bg-card">
          <div className="flex items-center gap-4">
            <div className="p-2 bg-primary/10 rounded-full text-primary">
              <CheckSquare className="h-5 w-5" />
            </div>
            <div>
              <p className="font-medium">Assignments</p>
              <p className="text-sm text-muted-foreground">Notify when you are assigned a task</p>
            </div>
          </div>
          <Switch 
            checked={preferences.notify_on_assignments} 
            onCheckedChange={() => handleToggle('notify_on_assignments')} 
          />
        </div>

        <div className="flex items-center justify-between p-4 rounded-lg border bg-card">
          <div className="flex items-center gap-4">
            <div className="p-2 bg-primary/10 rounded-full text-primary">
              <Clock className="h-5 w-5" />
            </div>
            <div>
              <p className="font-medium">Deadlines</p>
              <p className="text-sm text-muted-foreground">Notify about upcoming deadlines</p>
            </div>
          </div>
          <Switch 
            checked={preferences.notify_on_deadlines} 
            onCheckedChange={() => handleToggle('notify_on_deadlines')} 
          />
        </div>
      </div>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={isSaving}>
          {isSaving ? "Saving..." : "Save Preferences"}
        </Button>
      </div>
    </div>
  );
}
