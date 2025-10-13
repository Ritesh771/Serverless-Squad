import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Settings as SettingsIcon, Save, RotateCcw, AlertTriangle, Loader2, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';
import { Loader } from '@/components/Loader';

interface SystemSettings {
  maintenance_mode: boolean;
  allow_registration: boolean;
  email_notifications: boolean;
  photo_quality_threshold: number;
  signature_delay_threshold: number;
  price_anomaly_threshold: number;
  api_rate_limit: number;
  cache_ttl: number;
  notification_retry_attempts: number;
  backup_frequency: string;
  security_log_retention_days: number;
}

export default function AdminSettings() {
  const [settings, setSettings] = useState<SystemSettings>({
    maintenance_mode: false,
    allow_registration: true,
    email_notifications: true,
    photo_quality_threshold: 80,
    signature_delay_threshold: 48,
    price_anomaly_threshold: 25,
    api_rate_limit: 60,
    cache_ttl: 3600,
    notification_retry_attempts: 3,
    backup_frequency: 'daily',
    security_log_retention_days: 90,
  });
  
  const [isSaving, setIsSaving] = useState(false);
  const queryClient = useQueryClient();

  // Fetch current settings from backend
  const { data: currentSettings, isLoading, error } = useQuery({
    queryKey: ['admin-settings'],
    queryFn: async () => {
      // In a real implementation, this would fetch from backend
      // For now, we'll return the default settings
      return settings;
    },
  });

  // Save settings mutation
  const saveSettingsMutation = useMutation({
    mutationFn: async (newSettings: SystemSettings) => {
      // In a real implementation, this would save to backend
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      return newSettings;
    },
    onSuccess: () => {
      toast.success('Settings saved successfully');
      queryClient.invalidateQueries({ queryKey: ['admin-settings'] });
    },
    onError: () => {
      toast.error('Failed to save settings');
    },
  });

  // Reset cache mutation
  const resetCacheMutation = useMutation({
    mutationFn: async () => {
      // In a real implementation, this would call the cache management endpoint
      await new Promise(resolve => setTimeout(resolve, 500));
      return true;
    },
    onSuccess: () => {
      toast.success('Cache cleared successfully');
    },
    onError: () => {
      toast.error('Failed to clear cache');
    },
  });

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await saveSettingsMutation.mutateAsync(settings);
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    setSettings({
      maintenance_mode: false,
      allow_registration: true,
      email_notifications: true,
      photo_quality_threshold: 80,
      signature_delay_threshold: 48,
      price_anomaly_threshold: 25,
      api_rate_limit: 60,
      cache_ttl: 3600,
      notification_retry_attempts: 3,
      backup_frequency: 'daily',
      security_log_retention_days: 90,
    });
    toast.success('Settings reset to defaults');
  };

  const handleCacheClear = () => {
    resetCacheMutation.mutate();
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-center">
          <AlertTriangle className="mx-auto h-12 w-12 text-destructive" />
          <h3 className="mt-2 text-lg font-semibold">Error Loading Settings</h3>
          <p className="text-muted-foreground">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">System Settings</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">Configure platform-wide settings and system parameters</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleCacheClear} disabled={resetCacheMutation.isPending}>
            {resetCacheMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <SettingsIcon className="h-4 w-4" />
            )}
            Clear Cache
          </Button>
        </div>
      </div>

      {/* System Status Alert */}
      {settings.maintenance_mode && (
        <Alert className="border-orange-200 bg-orange-50">
          <AlertTriangle className="h-4 w-4 text-orange-600" />
          <AlertDescription className="text-orange-800">
            <strong>Maintenance Mode Active:</strong> Public access to the platform is currently disabled.
          </AlertDescription>
        </Alert>
      )}

      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Platform Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="maintenance">Maintenance Mode</Label>
              <p className="text-sm text-muted-foreground">
                Temporarily disable public access to the platform
              </p>
            </div>
            <Switch
              id="maintenance"
              checked={settings.maintenance_mode}
              onCheckedChange={(checked) => setSettings(prev => ({ ...prev, maintenance_mode: checked }))}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="registration">Allow New Registrations</Label>
              <p className="text-sm text-muted-foreground">
                Enable or disable new user sign-ups
              </p>
            </div>
            <Switch
              id="registration"
              checked={settings.allow_registration}
              onCheckedChange={(checked) => setSettings(prev => ({ ...prev, allow_registration: checked }))}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="emails">Email Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Send system email notifications
              </p>
            </div>
            <Switch
              id="emails"
              checked={settings.email_notifications}
              onCheckedChange={(checked) => setSettings(prev => ({ ...prev, email_notifications: checked }))}
            />
          </div>
        </CardContent>
      </Card>

      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>API Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="rateLimit">API Rate Limit (requests/minute)</Label>
            <Input
              id="rateLimit"
              type="number"
              min="1"
              max="1000"
              value={settings.api_rate_limit}
              onChange={(e) => setSettings(prev => ({ ...prev, api_rate_limit: parseInt(e.target.value) || 60 }))}
            />
            <p className="text-xs text-muted-foreground">
              Maximum API requests per minute per user
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="cacheTtl">Cache TTL (seconds)</Label>
            <Input
              id="cacheTtl"
              type="number"
              min="60"
              max="86400"
              value={settings.cache_ttl}
              onChange={(e) => setSettings(prev => ({ ...prev, cache_ttl: parseInt(e.target.value) || 3600 }))}
            />
            <p className="text-xs text-muted-foreground">
              Cache time-to-live in seconds (60-86400)
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>AI Thresholds & Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="photoQuality">Photo Quality Threshold (%)</Label>
            <Input
              id="photoQuality"
              type="number"
              min="0"
              max="100"
              value={settings.photo_quality_threshold}
              onChange={(e) => setSettings(prev => ({ ...prev, photo_quality_threshold: parseInt(e.target.value) || 80 }))}
            />
            <p className="text-xs text-muted-foreground">
              Minimum AI score for photo validation (0-100)
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="signatureDelay">Signature Delay Threshold (hours)</Label>
            <Input
              id="signatureDelay"
              type="number"
              min="0"
              max="168"
              value={settings.signature_delay_threshold}
              onChange={(e) => setSettings(prev => ({ ...prev, signature_delay_threshold: parseInt(e.target.value) || 48 }))}
            />
            <p className="text-xs text-muted-foreground">
              Maximum hours after job completion before flagging delay
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="priceAnomaly">Price Anomaly Threshold (%)</Label>
            <Input
              id="priceAnomaly"
              type="number"
              min="0"
              max="100"
              value={settings.price_anomaly_threshold}
              onChange={(e) => setSettings(prev => ({ ...prev, price_anomaly_threshold: parseInt(e.target.value) || 25 }))}
            />
            <p className="text-xs text-muted-foreground">
              Maximum percentage above area average before flagging
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="retryAttempts">Notification Retry Attempts</Label>
            <Input
              id="retryAttempts"
              type="number"
              min="1"
              max="10"
              value={settings.notification_retry_attempts}
              onChange={(e) => setSettings(prev => ({ ...prev, notification_retry_attempts: parseInt(e.target.value) || 3 }))}
            />
            <p className="text-xs text-muted-foreground">
              Number of retry attempts for failed notifications
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Security & Backup Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="backupFreq">Backup Frequency</Label>
            <Select value={settings.backup_frequency} onValueChange={(value) => setSettings(prev => ({ ...prev, backup_frequency: value }))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="hourly">Hourly</SelectItem>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              How often to create system backups
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="logRetention">Security Log Retention (days)</Label>
            <Input
              id="logRetention"
              type="number"
              min="30"
              max="365"
              value={settings.security_log_retention_days}
              onChange={(e) => setSettings(prev => ({ ...prev, security_log_retention_days: parseInt(e.target.value) || 90 }))}
            />
            <p className="text-xs text-muted-foreground">
              Number of days to retain security audit logs
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={handleReset} disabled={isSaving}>
          <RotateCcw className="h-4 w-4 mr-2" />
          Reset to Defaults
        </Button>
        <Button onClick={handleSave} disabled={isSaving}>
          {isSaving ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <Save className="h-4 w-4 mr-2" />
          )}
          Save Settings
        </Button>
      </div>
    </div>
  );
}
