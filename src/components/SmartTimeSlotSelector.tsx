import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Clock, MapPin, Car, TrendingUp, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface SmartTimeSlot {
  id: string;
  start_time: string;
  end_time: string;
  vendor_id: string;
  vendor_name: string;
  service_duration_minutes: number;
  travel_time_minutes: number;
  buffer_before_minutes: number;
  buffer_after_minutes: number;
  total_duration_minutes: number;
  optimization_score: number;
  travel_data: {
    distance_km: number;
    source: string;
    confidence_score: number;
  };
  pricing: {
    base_price: number;
    travel_surcharge: number;
    total_price: number;
  };
  availability_reason: string;
}

interface SmartTimeSlotSelectorProps {
  serviceId: string;
  pincode: string;
  selectedDate: string;
  onSlotSelect: (slot: SmartTimeSlot) => void;
  selectedSlotId?: string;
}

export function SmartTimeSlotSelector({ 
  serviceId, 
  pincode, 
  selectedDate, 
  onSlotSelect, 
  selectedSlotId 
}: SmartTimeSlotSelectorProps) {
  const [slots, setSlots] = useState<SmartTimeSlot[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Mock smart time slots with buffer information
  const mockSlots: SmartTimeSlot[] = [
    {
      id: '1',
      start_time: '2025-01-15T09:00:00Z',
      end_time: '2025-01-15T11:30:00Z',
      vendor_id: '1',
      vendor_name: 'John Smith',
      service_duration_minutes: 90,
      travel_time_minutes: 20,
      buffer_before_minutes: 15,
      buffer_after_minutes: 15,
      total_duration_minutes: 140,
      optimization_score: 92,
      travel_data: {
        distance_km: 12.5,
        source: 'api',
        confidence_score: 1.0
      },
      pricing: {
        base_price: 80,
        travel_surcharge: 10,
        total_price: 90
      },
      availability_reason: 'Optimal morning slot with minimal travel time'
    },
    {
      id: '2',
      start_time: '2025-01-15T14:00:00Z',
      end_time: '2025-01-15T16:45:00Z',
      vendor_id: '2',
      vendor_name: 'Sarah Johnson',
      service_duration_minutes: 90,
      travel_time_minutes: 35,
      buffer_before_minutes: 15,
      buffer_after_minutes: 15,
      total_duration_minutes: 155,
      optimization_score: 78,
      travel_data: {
        distance_km: 18.2,
        source: 'estimated',
        confidence_score: 0.7
      },
      pricing: {
        base_price: 80,
        travel_surcharge: 20,
        total_price: 100
      },
      availability_reason: 'Available afternoon slot with moderate travel'
    }
  ];

  const generateSmartSlots = async () => {
    if (!serviceId || !pincode || !selectedDate) {
      setError('Please provide service, pincode, and date');
      return;
    }

    setLoading(true);
    setError(null);

    // Simulate API call
    setTimeout(() => {
      setSlots(mockSlots);
      setLoading(false);
      toast.success('Smart time slots generated!');
    }, 1500);
  };

  const formatTime = (isoString: string) => {
    return new Date(isoString).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  return (
    <div className=\"space-y-4\">
      <div className=\"text-center\">
        <Button onClick={generateSmartSlots} disabled={!serviceId || !pincode || !selectedDate || loading}>
          {loading ? (
            <Loader2 className=\"h-4 w-4 mr-2 animate-spin\" />
          ) : (
            <TrendingUp className=\"h-4 w-4 mr-2\" />
          )}
          {loading ? 'Generating...' : 'Generate Smart Slots'}
        </Button>
        <p className=\"text-sm text-muted-foreground mt-2\">
          AI-optimized scheduling with travel time and buffer management
        </p>
      </div>

      {error && (
        <Alert>
          <AlertCircle className=\"h-4 w-4\" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className=\"space-y-3\">
        {slots.map((slot) => (
          <Card
            key={slot.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              selectedSlotId === slot.id 
                ? 'border-primary bg-primary/5 ring-2 ring-primary/20' 
                : 'border-gray-200'
            }`}
            onClick={() => onSlotSelect(slot)}
          >
            <CardContent className=\"p-4\">
              <div className=\"flex items-center justify-between mb-3\">
                <div>
                  <h4 className=\"font-semibold\">
                    {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                  </h4>
                  <p className=\"text-sm text-muted-foreground\">{slot.vendor_name}</p>
                </div>
                <div className=\"text-right\">
                  <Badge className={slot.optimization_score >= 85 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                    {slot.optimization_score}% optimized
                  </Badge>
                  <p className=\"text-lg font-bold mt-1\">${slot.pricing.total_price}</p>
                </div>
              </div>

              <Separator className=\"my-3\" />

              <div className=\"grid grid-cols-2 gap-4 text-xs\">
                <div className=\"space-y-2\">
                  <div className=\"flex items-center gap-2\">
                    <Car className=\"h-3 w-3 text-blue-600\" />
                    <span>Travel: {formatDuration(slot.travel_time_minutes)}</span>
                  </div>
                  <div className=\"flex items-center gap-2\">
                    <Clock className=\"h-3 w-3 text-green-600\" />
                    <span>Service: {formatDuration(slot.service_duration_minutes)}</span>
                  </div>
                </div>
                <div className=\"space-y-2\">
                  <div className=\"flex items-center gap-2\">
                    <MapPin className=\"h-3 w-3 text-gray-600\" />
                    <span>{slot.travel_data.distance_km}km distance</span>
                  </div>
                  <div className=\"flex items-center gap-2\">
                    <CheckCircle2 className=\"h-3 w-3 text-orange-600\" />
                    <span>Buffer: {formatDuration(slot.buffer_before_minutes + slot.buffer_after_minutes)}</span>
                  </div>
                </div>
              </div>

              <div className=\"mt-3 pt-3 border-t border-gray-100\">
                <p className=\"text-xs text-muted-foreground\">
                  💡 {slot.availability_reason}
                </p>
                {slot.travel_data.source !== 'api' && (
                  <p className=\"text-xs text-yellow-600 mt-1\">
                    ⚠️ Travel time estimated - actual may vary
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {slots.length > 0 && (
        <Alert>
          <TrendingUp className=\"h-4 w-4\" />
          <AlertDescription>
            <strong>Smart scheduling benefits:</strong> Reduced waiting times, 
            optimized vendor routes, and transparent pricing with travel costs included.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}