import { useState, useEffect } from "react";
import { notificationsApi } from "@/api/notifications";
import type { Notification } from "@/api/notifications";
import { useWorkspaceStore } from "@/store/workspaceStore";

export function useNotifications() {
  const workspaceId = useWorkspaceStore(s => s.activeWorkspaceId);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (workspaceId) {
      loadNotifications();
      loadUnreadCount();
      
      const interval = setInterval(() => {
        loadUnreadCount();
      }, 60000); // Check every minute
      
      return () => clearInterval(interval);
    }
  }, [workspaceId]);

  const loadNotifications = async () => {
    if (!workspaceId) return;
    try {
      const result = await notificationsApi.getNotifications(workspaceId);
      setNotifications(result);
    } catch (error) {
      console.error("Failed to load notifications", error);
    }
  };

  const loadUnreadCount = async () => {
    if (!workspaceId) return;
    try {
      const res = await notificationsApi.getUnreadCount(workspaceId);
      setUnreadCount(res.count);
    } catch (error) {
      console.error("Failed to load unread count", error);
    }
  };

  const markAsRead = async (notificationId: string) => {
    if (!workspaceId) return;
    try {
      await notificationsApi.markAsRead(workspaceId, notificationId);
      setNotifications(prev => prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error("Failed to mark as read", error);
    }
  };

  const markAllAsRead = async () => {
    if (!workspaceId) return;
    try {
      await notificationsApi.markAllAsRead(workspaceId);
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error("Failed to mark all as read", error);
    }
  };

  return { notifications, unreadCount, loadNotifications, markAsRead, markAllAsRead };
}
