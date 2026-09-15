import { useState, useEffect } from "react";
import { notificationsApi } from "@/api/notifications";
import type { NotificationPreference } from "@/api/notifications";
import { useWorkspaceStore } from "@/store/workspaceStore";
// Mock Switch if not available
const Switch = ({ checked, onCheckedChange }: { checked: boolean, onCheckedChange: () => void }) => (
  <input type="checkbox" checked={checked} onChange={onCheckedChange} className="w-4 h-4 accent-primary" />
);
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export function NotificationSettings() {
  const activeWorkspaceId = useWorkspaceStore(s => s.activeWorkspaceId);
  const currentWorkspace = activeWorkspaceId ? { id: activeWorkspaceId as string } : null;
  const [preferences, setPreferences] = useState<NotificationPreference[]>([]);
  const [isLoading, setIsLoading] = useState(false);

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

  const handleToggle = async (category: string, key: "in_app_enabled" | "email_enabled") => {
    if (!currentWorkspace) return;
    
    // Optimistic update
    const prev = [...preferences];
    const categoryPref = preferences.find(p => p.category === category);
    if (!categoryPref) return;
    
    const newValue = !categoryPref[key];
    setPreferences(preferences.map(p => 
      p.category === category ? { ...p, [key]: newValue } : p
    ));

    try {
      await notificationsApi.updatePreference(currentWorkspace.id, category, { [key]: newValue });
      toast.success("Preference updated");
    } catch (error) {
      console.error("Failed to update preference", error);
      toast.error("Failed to update preference");
      // Revert on failure
      setPreferences(prev);
    }
  };

  if (isLoading) {
    return <div className="animate-pulse space-y-4">
      <div className="h-12 bg-muted rounded-md" />
      <div className="h-12 bg-muted rounded-md" />
      <div className="h-12 bg-muted rounded-md" />
    </div>;
  }

  if (!preferences || preferences.length === 0) return null;

  return (
    <div className="space-y-6">
      <div className="rounded-md border">
        <table className="w-full text-sm text-left">
          <thead className="bg-muted text-muted-foreground">
            <tr>
              <th className="p-4 font-medium">Category</th>
              <th className="p-4 font-medium text-center">In-App</th>
              <th className="p-4 font-medium text-center">Email</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {preferences.map((pref) => (
              <tr key={pref.category}>
                <td className="p-4 capitalize font-medium">{pref.category}</td>
                <td className="p-4 text-center">
                  <Switch 
                    checked={pref.in_app_enabled} 
                    onCheckedChange={() => handleToggle(pref.category, 'in_app_enabled')} 
                  />
                </td>
                <td className="p-4 text-center">
                  <Switch 
                    checked={pref.email_enabled} 
                    onCheckedChange={() => handleToggle(pref.category, 'email_enabled')} 
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
