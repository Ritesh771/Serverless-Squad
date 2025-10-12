import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarIcon, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const services = [
  { id: '1', name: 'Plumbing', basePrice: 80 },
  { id: '2', name: 'Electrical', basePrice: 100 },
  { id: '3', name: 'HVAC', basePrice: 120 },
  { id: '4', name: 'Carpentry', basePrice: 90 },
  { id: '5', name: 'Painting', basePrice: 70 },
];

export default function BookService() {
  const [serviceType, setServiceType] = useState('');
  const [date, setDate] = useState<Date>();
  const [address, setAddress] = useState('');
  const [pincode, setPincode] = useState('');
  const [description, setDescription] = useState('');
  const [estimatedPrice, setEstimatedPrice] = useState<number | null>(null);
  const [timeSlot, setTimeSlot] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const timeSlots = [
    '09:00 AM - 11:00 AM',
    '11:00 AM - 01:00 PM',
    '01:00 PM - 03:00 PM',
    '03:00 PM - 05:00 PM',
    '05:00 PM - 07:00 PM',
  ];

  const calculatePrice = () => {
    const service = services.find((s) => s.id === serviceType);
    if (service && pincode) {
      // Mock dynamic pricing based on pincode
      const basePrice = service.basePrice;
      const pincodeMultiplier = pincode.startsWith('1') ? 1.2 : pincode.startsWith('9') ? 1.15 : 1.0;
      setEstimatedPrice(Math.round(basePrice * pincodeMultiplier));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // TODO: Connect to /api/customer/bookings
    setTimeout(() => {
      toast.success('Service booked successfully!');
      navigate('/customer/my-bookings');
    }, 1500);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Book a Service</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Schedule a home service with our verified vendors</p>
      </div>

      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Service Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="service">Service Type</Label>
                <Select value={serviceType} onValueChange={setServiceType} required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select service" />
                  </SelectTrigger>
                  <SelectContent>
                    {services.map((service) => (
                      <SelectItem key={service.id} value={service.id}>
                        {service.name} - ${service.basePrice}/hr
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Preferred Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className="w-full justify-start">
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {date ? format(date, 'PPP') : 'Pick a date'}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar mode="single" selected={date} onSelect={setDate} />
                  </PopoverContent>
                </Popover>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Service Address</Label>
              <Input
                id="address"
                placeholder="123 Main St, Apartment 4B"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="pincode">Pincode</Label>
                <Input
                  id="pincode"
                  placeholder="12345"
                  value={pincode}
                  onChange={(e) => setPincode(e.target.value)}
                  onBlur={calculatePrice}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label>Time Slot</Label>
                <Select value={timeSlot} onValueChange={setTimeSlot} required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select time slot" />
                  </SelectTrigger>
                  <SelectContent>
                    {timeSlots.map((slot) => (
                      <SelectItem key={slot} value={slot}>
                        {slot}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Service Description</Label>
              <Textarea
                id="description"
                placeholder="Describe the issue or service needed..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                required
              />
            </div>

            {serviceType && (
              <div className="p-4 bg-muted rounded-lg">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={calculatePrice}
                  className="mb-2"
                >
                  Calculate Estimated Price
                </Button>
                {estimatedPrice !== null && (
                  <p className="text-2xl font-bold text-primary">
                    Estimated: ${estimatedPrice}/hour
                  </p>
                )}
              </div>
            )}

            <div className="flex gap-3">
              <Button type="submit" className="flex-1" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Booking...
                  </>
                ) : (
                  'Confirm Booking'
                )}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate(-1)}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
