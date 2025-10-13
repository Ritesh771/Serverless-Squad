// Notification Service for handling real-time notifications
// This service can be extended to work with WebSocket or other real-time technologies

export interface Notification {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  read: boolean;
  type: 'booking' | 'payment' | 'system' | 'reminder';
  relatedId?: string;
}

class NotificationService {
  private notifications: Notification[] = [];
  private listeners: Array<(notifications: Notification[]) => void> = [];

  // Add a new notification
  addNotification(notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) {
    const newNotification: Notification = {
      id: `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      read: false,
      ...notification
    };
    
    this.notifications.unshift(newNotification);
    this.notifyListeners();
    return newNotification;
  }

  // Get all notifications
  getNotifications(): Notification[] {
    return [...this.notifications];
  }

  // Get unread notifications count
  getUnreadCount(): number {
    return this.notifications.filter(n => !n.read).length;
  }

  // Mark a notification as read
  markAsRead(id: string): void {
    const notification = this.notifications.find(n => n.id === id);
    if (notification) {
      notification.read = true;
      this.notifyListeners();
    }
  }

  // Mark all notifications as read
  markAllAsRead(): void {
    this.notifications.forEach(n => n.read = true);
    this.notifyListeners();
  }

  // Delete a notification
  deleteNotification(id: string): void {
    this.notifications = this.notifications.filter(n => n.id !== id);
    this.notifyListeners();
  }

  // Clear all notifications
  clearAll(): void {
    this.notifications = [];
    this.notifyListeners();
  }

  // Add listener for notification updates
  addListener(listener: (notifications: Notification[]) => void): void {
    this.listeners.push(listener);
  }

  // Remove listener
  removeListener(listener: (notifications: Notification[]) => void): void {
    this.listeners = this.listeners.filter(l => l !== listener);
  }

  // Notify all listeners of changes
  private notifyListeners(): void {
    this.listeners.forEach(listener => listener([...this.notifications]));
  }

  // Simulate receiving a notification from server
  simulateServerNotification(notification: Omit<Notification, 'id' | 'timestamp' | 'read'>): void {
    this.addNotification(notification);
  }
}

export const notificationService = new NotificationService();