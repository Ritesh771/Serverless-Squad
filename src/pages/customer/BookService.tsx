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
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bookingService, Service } from '@/services/bookingService';
import { vendorService, VendorSearchResult } from '@/services/vendorService';
import { pricingService, DynamicPricing } from '@/services/pricingService';
import { schedulingService } from '@/services/schedulingService';

export default function BookService() {
  const [serviceType, setServiceType] = useState('');
  const [date, setDate] = useState<Date>();
  const [address, setAddress] = useState('');
  const [pincode, setPincode] = useState('');
  const [description, setDescription] = useState('');
  const [timeSlot, setTimeSlot] = useState('');
  const [selectedVendor, setSelectedVendor] = useState<string>('');
  const [searchingVendors, setSearchingVendors] = useState(false);
  const [vendors, setVendors] = useState<VendorSearchResult[]>([]);
  const [dynamicPricing, setDynamicPricing] = useState<DynamicPricing | null>(null);
  const [demandIndex, setDemandIndex] = useState<number | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch services from backend
  const { data: services, isLoading: servicesLoading } = useQuery({
    queryKey: ['services'],
    queryFn: () => bookingService.getServices(),
  });

  // Create booking mutation
  const createBookingMutation = useMutation({
    mutationFn: bookingService.createBooking,
    onSuccess: () => {
      toast.success('Service booked successfully!');
      queryClient.invalidateQueries({ queryKey: ['customer-bookings'] });
      navigate('/customer/my-bookings');
      setLoading(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to book service');
      setLoading(false);
    },
  });

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
      const scheduledDatetime = date ? date.toISOString() : undefined;
      const pricing = await pricingService.getDynamicPrice(
        parseInt(serviceType),
        pincode,
        scheduledDatetime
      );
      
      setDynamicPricing(pricing);
      
      // Show price change information
      const change = pricing.pricing.price_change_percent;
      if (Math.abs(change) > 0) {
        toast.info(
          `Price ${change > 0 ? 'increased' : 'decreased'} by ${Math.abs(change).toFixed(1)}% due to demand`,
          {
            description: `Base: ₹${pricing.pricing.base_price} → Final: ₹${pricing.pricing.final_price}`,
            duration: 5000
          }
        );
      }
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

    const service = services?.find((s) => s.id.toString() === serviceType);
    if (!service) {
      toast.error('Service not found');
      return;
    }

    const finalPrice = dynamicPricing?.pricing.final_price || parseFloat(service.base_price);

    setLoading(true);
    createBookingMutation.mutate({
      service: parseInt(serviceType),
      pincode,
      scheduled_date: date.toISOString(),
      customer_notes: description,
      total_price: finalPrice.toString(),
    });
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
                    {servicesLoading ? (
                      <SelectItem value="loading" disabled>
                        Loading services...
                      </SelectItem>
                    ) : services && services.length > 0 ? (
                      services.map((service) => (
                        <SelectItem key={service.id} value={service.id.toString()}>
                          {service.name} - ${service.base_price}/hr
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="no-services" disabled>
                        No services available
                      </SelectItem>
                    )}
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

            {serviceType && dynamicPricing && (
              <div className="p-4 bg-muted rounded-lg space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">Dynamic Pricing</h3>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={calculatePrice}
                    disabled={!pincode}
                  >
                    Recalculate
                  </Button>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-muted-foreground">Base Price</div>
                    <div className="font-medium">₹{dynamicPricing.pricing.base_price}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Final Price</div>
                    <div className="font-bold text-lg text-primary">₹{dynamicPricing.pricing.final_price}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Demand Multiplier</div>
                    <div className="font-medium">{dynamicPricing.pricing.demand_multiplier}x</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Price Change</div>
                    <div className={`font-medium ${dynamicPricing.pricing.price_change_percent > 0 ? 'text-destructive' : 'text-green-600'}`}>
                      {dynamicPricing.pricing.price_change_percent > 0 ? '+' : ''}{dynamicPricing.pricing.price_change_percent.toFixed(1)}%
                    </div>
                  </div>
                </div>

                {dynamicPricing.pricing.factors && dynamicPricing.pricing.factors.length > 0 && (
                  <div className="mt-3 pt-3 border-t">
                    <div className="text-sm font-medium mb-2">Pricing Factors:</div>
                    <div className="space-y-1">
                      {dynamicPricing.pricing.factors.map((factor: any, index: number) => (
                        <div key={index} className="text-sm text-muted-foreground flex items-center gap-2">
                          {factor.impact > 0 ? (
                            <TrendingUp className="h-3 w-3 text-destructive" />
                          ) : (
                            <AlertTriangle className="h-3 w-3 text-green-600" />
                          )}
                          <span>{factor.reason}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {serviceType && !dynamicPricing && (
              <div className="p-4 bg-muted rounded-lg">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={calculatePrice}
                  disabled={!pincode}
                  className="w-full"
                >
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Calculate Dynamic Price
                </Button>
                <p className="text-sm text-muted-foreground mt-2">
                  Get real-time pricing based on demand and availability
                </p>
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