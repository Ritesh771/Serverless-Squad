import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

export default function AdminSettings() {
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [allowRegistration, setAllowRegistration] = useState(true);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [photoQualityThreshold, setPhotoQualityThreshold] = useState('80');
  const [signatureDelayThreshold, setSignatureDelayThreshold] = useState('48');
  const [priceAnomalyThreshold, setPriceAnomalyThreshold] = useState('25');

  const handleSave = () => {
    toast.success('Settings saved successfully');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">System Settings</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Configure platform-wide settings</p>
      </div>

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
              checked={maintenanceMode}
              onCheckedChange={setMaintenanceMode}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="registration">Allow New Registrations</Label>
              <p className="text-sm text-muted-foreground">
                Enable or disable new user sign-ups
              </p>
            </div>
            <Switch
              id="registration"
              checked={allowRegistration}
              onCheckedChange={setAllowRegistration}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="emails">Email Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Send system email notifications
              </p>
            </div>
            <Switch
              id="emails"
              checked={emailNotifications}
              onCheckedChange={setEmailNotifications}
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
            <Label htmlFor="apiUrl">API Base URL</Label>
            <Input
              id="apiUrl"
              placeholder="https://api.homeservepro.com"
              defaultValue="http://localhost:3000"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="rateLimit">API Rate Limit (requests/minute)</Label>
            <Input
              id="rateLimit"
              type="number"
              defaultValue="60"
            />
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
              value={photoQualityThreshold}
              onChange={(e) => setPhotoQualityThreshold(e.target.value)}
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
              value={signatureDelayThreshold}
              onChange={(e) => setSignatureDelayThreshold(e.target.value)}
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
              value={priceAnomalyThreshold}
              onChange={(e) => setPriceAnomalyThreshold(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Maximum percentage above area average before flagging
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-3">
        <Button variant="outline">Reset to Defaults</Button>
        <Button onClick={handleSave}>Save Settings</Button>
      </div>
    </div>
  );
}
