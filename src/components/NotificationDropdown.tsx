import { useState, useEffect } from 'react';
import { Bell, X, Check, AlertCircle, User, Calendar, CreditCard } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useAuth } from '@/context/AuthContext';
import { notificationService, Notification } from '@/services/notificationService';
import './NotificationDropdown.css';

export function NotificationDropdown() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // Load initial notifications and set up listener
  useEffect(() => {
    if (!user) return;
    
    // Load initial notifications
    loadInitialNotifications();
    
    // Set up listener for real-time updates
    notificationService.addListener(handleNotificationUpdate);
    
    // Cleanup listener on unmount
    return () => {
      notificationService.removeListener(handleNotificationUpdate);
    };
  }, [user]);

  const loadInitialNotifications = () => {
    if (!user) return;
    
    const mockNotifications: Record<string, Notification[]> = {
      customer: [
        {
          id: '1',
          title: 'Booking Confirmed',
          description: 'Your plumbing service booking has been confirmed for tomorrow at 10:00 AM',
          timestamp: '2025-01-15T09:30:00Z',
          read: false,
          type: 'booking',
          relatedId: 'booking-123'
        },
        {
          id: '2',
          title: 'Payment Successful',
          description: 'Your payment of ₹180.00 has been processed successfully',
          timestamp: '2025-01-14T14:22:00Z',
          read: true,
          type: 'payment',
          relatedId: 'payment-456'
        },
        {
          id: '3',
          title: 'Service Reminder',
          description: 'Your scheduled service is tomorrow. Please be available',
          timestamp: '2025-01-14T08:15:00Z',
          read: false,
          type: 'reminder',
          relatedId: 'booking-123'
        }
      ],
      vendor: [
        {
          id: '4',
          title: 'New Booking Assigned',
          description: 'You have a new plumbing service booking for today at 2:00 PM',
          timestamp: '2025-01-15T08:45:00Z',
          read: false,
          type: 'booking',
          relatedId: 'booking-789'
        },
        {
          id: '5',
          title: 'Payment Received',
          description: 'Payment of ₹250.00 has been credited to your account',
          timestamp: '2025-01-14T16:30:00Z',
          read: true,
          type: 'payment',
          relatedId: 'payment-987'
        }
      ],
      ops_manager: [
        {
          id: '6',
          title: 'Urgent Support Ticket',
          description: 'Customer John Smith needs immediate assistance with booking #1234',
          timestamp: '2025-01-15T10:15:00Z',
          read: false,
          type: 'system',
          relatedId: 'ticket-555'
        },
        {
          id: '7',
          title: 'Daily Report Ready',
          description: 'Your daily operations report is now available for review',
          timestamp: '2025-01-15T06:00:00Z',
          read: true,
          type: 'system',
          relatedId: 'report-abc'
        }
      ],
      super_admin: [
        {
          id: '8',
          title: 'System Alert',
          description: 'Server maintenance scheduled for tonight at 2:00 AM',
          timestamp: '2025-01-15T07:30:00Z',
          read: false,
          type: 'system',
          relatedId: 'alert-xyz'
        },
        {
          id: '9',
          title: 'New User Registration',
          description: 'New vendor application received for review',
          timestamp: '2025-01-14T18:45:00Z',
          read: true,
          type: 'system',
          relatedId: 'application-111'
        }
      ]
    };

    const userNotifications = mockNotifications[user.role] || [];
    setNotifications(userNotifications);
    setUnreadCount(userNotifications.filter(n => !n.read).length);
    
    // Initialize the notification service with these notifications
    userNotifications.forEach(notification => {
      notificationService.addNotification({
        title: notification.title,
        description: notification.description,
        type: notification.type,
        relatedId: notification.relatedId
      });
    });
  };

  const handleNotificationUpdate = (updatedNotifications: Notification[]) => {
    setNotifications(updatedNotifications);
    setUnreadCount(updatedNotifications.filter(n => !n.read).length);
  };

  const markAsRead = (id: string) => {
    notificationService.markAsRead(id);
  };

  const markAllAsRead = () => {
    notificationService.markAllAsRead();
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'booking':
        return <Calendar className="h-4 w-4 text-blue-500" />;
      case 'payment':
        return <CreditCard className="h-4 w-4 text-green-500" />;
      case 'reminder':
        return <Bell className="h-4 w-4 text-yellow-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute top-0 right-0 flex h-4 w-4">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500 text-xs text-white items-center justify-center notification-badge">
                {unreadCount}
              </span>
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-80 notification-dropdown-content" align="end">
        <DropdownMenuLabel className="flex justify-between items-center">
          <span>Notifications</span>
          {unreadCount > 0 && (
            <Button variant="ghost" size="sm" onClick={markAllAsRead}>
              Mark all as read
            </Button>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <ScrollArea className="h-80">
          <DropdownMenuGroup>
            {notifications.length === 0 ? (
              <DropdownMenuItem>
                <div className="flex flex-col items-center justify-center w-full py-8">
                  <Bell className="h-8 w-8 text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">No notifications</p>
                </div>
              </DropdownMenuItem>
            ) : (
              notifications.map((notification) => (
                <DropdownMenuItem 
                  key={notification.id} 
                  className={`flex flex-col items-start p-3 notification-item ${!notification.read ? 'notification-unread' : ''}`}
                  onClick={() => markAsRead(notification.id)}
                >
                  <div className="flex w-full">
                    <div className="mr-2 mt-0.5">
                      {getNotificationIcon(notification.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between">
                        <p className="text-sm font-medium">{notification.title}</p>
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="h-5 w-5 p-0 ml-2"
                          onClick={(e) => {
                            e.stopPropagation();
                            markAsRead(notification.id);
                          }}
                        >
                          <Check className="h-3 w-3" />
                        </Button>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">{notification.description}</p>
                      <p className="text-xs text-muted-foreground mt-2">{formatTime(notification.timestamp)}</p>
                    </div>
                  </div>
                </DropdownMenuItem>
              ))
            )}
          </DropdownMenuGroup>
        </ScrollArea>
        <DropdownMenuSeparator />
        <DropdownMenuItem className="justify-center text-center">
          <Button variant="ghost" className="w-full">
            View all notifications
          </Button>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}