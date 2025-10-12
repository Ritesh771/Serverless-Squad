import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarIcon, Loader2, MapPin, Star, Clock, Users, TrendingUp, AlertTriangle } from 'lucide-react';
import { format } from 'date-fns';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { vendorService, Vendor, pricingService, PricingSuggestions } from '@/services/vendorService';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';

interface Service {
  id: string;
  name: string;
  base_price: number;
  duration_minutes: number;
}

export default function BookService() {
  const [services, setServices] = useState<Service[]>([]);
  const [serviceType, setServiceType] = useState('');
  const [date, setDate] = useState<Date>();
  const [address, setAddress] = useState('');
  const [pincode, setPincode] = useState('');
  const [description, setDescription] = useState('');
  const [estimatedPrice, setEstimatedPrice] = useState<number | null>(null);
  const [timeSlot, setTimeSlot] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchingVendors, setSearchingVendors] = useState(false);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [demandIndex, setDemandIndex] = useState<number | null>(null);
  const [selectedVendor, setSelectedVendor] = useState<string>('');
  const [pricingSuggestions, setPricingSuggestions] = useState<PricingSuggestions | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const navigate = useNavigate();

  // Load services on component mount
  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      const response = await api.get(ENDPOINTS.SERVICE.LIST);
      setServices(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load services');
    }
  };

  const timeSlots = [
    '09:00 AM - 11:00 AM',
    '11:00 AM - 01:00 PM',
    '01:00 PM - 03:00 PM',
    '03:00 PM - 05:00 PM',
    '05:00 PM - 07:00 PM',
  ];

  const searchVendors = async () => {
    if (!pincode) {
      toast.error('Please enter a pincode');
      return;
    }

    setSearchingVendors(true);
    try {
      const serviceId = serviceType ? parseInt(serviceType) : undefined;
      const result = await vendorService.searchVendors(pincode, serviceId);
      setVendors(result.vendors);
      setDemandIndex(result.demand_index);
      
      // Show demand alert if high demand
      if (result.demand_index > 7) {
        toast.warning(`High demand zone detected! (${result.demand_index}/10) - Prices may be higher`);
      } else if (result.demand_index > 5) {
        toast.info(`Moderate demand zone (${result.demand_index}/10)`);
      }
    } catch (error) {
      toast.error('Failed to search vendors in this area');
    } finally {
      setSearchingVendors(false);
    }
  };

  const calculatePrice = async () => {
    if (!serviceType || !pincode) {
      toast.error('Please select a service and enter a pincode');
      return;
    }

    try {
      const service = services.find((s) => s.id === serviceType);
      if (!service) return;

      const response = await pricingService.calculatePrice(
        parseInt(serviceType),
        pincode,
        date ? date.toISOString() : undefined
      );

      setEstimatedPrice(response.final_price);
      
      // Show price change information
      if (response.price_change_percent !== 0) {
        const change = response.price_change_percent;
        const surgeInfo = response.surge_info;
        
        toast.info(
          `Price ${change > 0 ? 'increased' : 'decreased'} by ${Math.abs(change)}% due to demand`,
          {
            description: `Base: $${response.base_price.toFixed(2)} → Final: $${response.final_price.toFixed(2)}`,
            duration: 5000
          }
        );
        
        // Show surge information if applicable
        if (surgeInfo.level > 0) {
          toast.info(
            `${surgeInfo.label} Pricing`,
            {
              description: surgeInfo.reasons.join(', '),
              icon: surgeInfo.level > 1 ? <AlertTriangle className="h-4 w-4" /> : <TrendingUp className="h-4 w-4" />,
              duration: 5000
            }
          );
        }
      }
      
      // Get pricing suggestions
      const suggestions = await pricingService.getPriceSuggestions(parseInt(serviceType), pincode);
      setPricingSuggestions(suggestions);
    } catch (error) {
      toast.error('Failed to calculate dynamic price');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!serviceType || !date || !address || !pincode || !timeSlot) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);

    try {
      const service = services.find((s) => s.id === serviceType);
      if (!service) {
        throw new Error('Service not found');
      }

      const bookingData = {
        service: parseInt(serviceType),
        pincode,
        scheduled_date: date.toISOString(),
        customer_notes: description,
        total_price: estimatedPrice || service.base_price,
      };

      const response = await api.post(ENDPOINTS.CUSTOMER.BOOKINGS, bookingData);
      toast.success('Service booked successfully!');
      navigate('/customer/my-bookings');
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to book service';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-6">
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
                        {service.name} - ${service.base_price}/hr
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
                <div className="flex gap-2">
                  <Input
                    id="pincode"
                    placeholder="123456"
                    value={pincode}
                    onChange={(e) => setPincode(e.target.value)}
                    required
                  />
                  <Button 
                    type="button" 
                    onClick={searchVendors}
                    disabled={searchingVendors || !pincode}
                  >
                    {searchingVendors ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      'Search'
                    )}
                  </Button>
                </div>
                
                {demandIndex !== null && (
                  <div className="flex items-center gap-2 text-sm mt-1">
                    <Users className="h-4 w-4" />
                    <span>Demand Index: {demandIndex}/10</span>
                    {demandIndex > 7 && (
                      <span className="px-2 py-1 bg-destructive/10 text-destructive text-xs rounded">
                        High Demand
                      </span>
                    )}
                  </div>
                )}
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

            {vendors.length > 0 && (
              <Card className="border-primary">
                <CardHeader>
                  <CardTitle className="text-lg">Available Vendors ({vendors.length})</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {vendors.map((vendor) => (
                    <div 
                      key={vendor.id} 
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        selectedVendor === vendor.id.toString() 
                          ? 'border-primary bg-primary/5' 
                          : 'hover:bg-muted'
                      }`}
                      onClick={() => setSelectedVendor(vendor.id.toString())}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium">{vendor.name}</div>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                              <span>{vendor.rating}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <MapPin className="h-4 w-4" />
                              <span>{vendor.distance_km} km</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="h-4 w-4" />
                              <span>{vendor.travel_time} min</span>
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-muted-foreground">
                            {vendor.total_jobs} jobs completed
                          </div>
                          {selectedVendor === vendor.id.toString() && (
                            <div className="text-xs text-primary font-medium">Selected</div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

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
                <div className="flex justify-between items-center mb-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={calculatePrice}
                    className="mb-2"
                    disabled={!pincode}
                  >
                    Calculate Estimated Price
                  </Button>
                  {pricingSuggestions && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowSuggestions(!showSuggestions)}
                    >
                      {showSuggestions ? 'Hide' : 'Show'} Suggestions
                    </Button>
                  )}
                </div>
                
                {estimatedPrice !== null && (
                  <p className="text-2xl font-bold text-primary">
                    Estimated: ${estimatedPrice.toFixed(2)}
                  </p>
                )}
                
                {showSuggestions && pricingSuggestions && (
                  <div className="mt-3 p-3 bg-background border rounded-md">
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <TrendingUp className="h-4 w-4" />
                      Pricing Suggestions
                    </h4>
                    
                    {pricingSuggestions.recommendations.length > 0 ? (
                      <div className="space-y-2">
                        {pricingSuggestions.recommendations.map((rec, index) => (
                          <div key={index} className="text-sm p-2 bg-muted rounded">
                            {rec.message}
                            {rec.savings > 0 && (
                              <span className="ml-2 font-medium text-green-600">
                                Save ₹{rec.savings.toFixed(2)}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">No specific recommendations at this time.</p>
                    )}
                    
                    <div className="mt-2 text-sm">
                      <p>
                        Cheapest date: {new Date(pricingSuggestions.cheapest_date).toLocaleDateString()} 
                        <span className="ml-2 font-medium text-green-600">
                          Save ₹{pricingSuggestions.savings.toFixed(2)}
                        </span>
                      </p>
                    </div>
                  </div>
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