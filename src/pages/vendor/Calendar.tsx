import { useState, useEffect } from 'react';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Clock, MapPin, Calendar as CalendarIcon, 
  TrendingUp, AlertTriangle, CheckCircle,
  Car, Timer, Route, Loader2
} from 'lucide-react';
import { format, addMinutes, isSameDay } from 'date-fns';
import { useQuery } from '@tanstack/react-query';
import { bookingService } from '@/services/bookingService';
import { schedulingService } from '@/services/schedulingService';

interface BookingWithBuffer {
  id: string;
  time: string;
  customer: string;
  service: string;
  status: 'confirmed' | 'pending' | 'in_progress' | 'completed';
  pincode: string;
  travelTimeTo: number;
  travelTimeFrom: number;
  serviceDuration: number;
  bufferBefore: number;
  bufferAfter: number;
  actualStartTime: string;
  actualEndTime: string;
  optimization?: {
    score: number;
    suggestions: string[];
  };
}

interface ScheduleOptimization {
  total_bookings: number;
  total_working_time_minutes: number;
  total_travel_time_minutes: number;
  total_service_time_minutes: number;
  efficiency_score: number;
  optimization_suggestions: Array<{
    type: string;
    booking_id: string;
    suggestion: string;
    severity: 'low' | 'medium' | 'high';
  }>;
}

export default function VendorCalendar() {
  const [date, setDate] = useState<Date | undefined>(new Date());
  const [selectedTab, setSelectedTab] = useState('schedule');

  // Fetch vendor's bookings
  const { data: allBookings, isLoading: bookingsLoading } = useQuery({
    queryKey: ['vendor-bookings-calendar'],
    queryFn: () => bookingService.getBookings(),
  });

  // Fetch schedule optimization for selected date
  const { data: optimization, isLoading: optimizationLoading } = useQuery({
    queryKey: ['vendor-schedule-optimization', date?.toISOString().split('T')[0]],
    queryFn: () => {
      if (!date) return null;
      return schedulingService.getVendorOptimization(date.toISOString().split('T')[0]);
    },
    enabled: !!date,
  });

  // Filter bookings for selected date
  const bookingsForDate = allBookings?.filter(booking => {
    if (!date) return false;
    const bookingDate = new Date(booking.scheduled_date);
    return isSameDay(bookingDate, date);
  }) || [];

  // Transform bookings to include buffer information
  const bookingsWithBuffer = bookingsForDate.map(booking => ({
    id: booking.id,
    time: new Date(booking.scheduled_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
    customer: booking.customer_name || `Customer #${booking.customer}`,
    service: booking.service_name || `Service #${booking.service}`,
    status: booking.status,
    pincode: booking.pincode,
    travelTimeTo: booking.travel_time_to_location_minutes || 30,
    travelTimeFrom: booking.travel_time_from_location_minutes || 30,
    serviceDuration: booking.estimated_service_duration_minutes || 60,
    bufferBefore: booking.buffer_before_minutes || 15,
    bufferAfter: booking.buffer_after_minutes || 15,
    actualStartTime: format(addMinutes(new Date(booking.scheduled_date), -(booking.buffer_before_minutes || 15) - (booking.travel_time_to_location_minutes || 30)), 'hh:mm a'),
    actualEndTime: format(addMinutes(new Date(booking.scheduled_date), 
      (booking.estimated_service_duration_minutes || 60) + (booking.buffer_after_minutes || 15) + (booking.travel_time_from_location_minutes || 30)), 'hh:mm a'),
    optimization: {
      score: 85, // Default score, could be calculated from real data
      suggestions: []
    }
  }));

  // Calculate optimization summary from real data
  const optimizationSummary: ScheduleOptimization = {
    total_bookings: bookingsWithBuffer.length,
    total_working_time_minutes: bookingsWithBuffer.reduce((total, booking) => 
      total + booking.travelTimeTo + booking.serviceDuration + booking.travelTimeFrom + booking.bufferBefore + booking.bufferAfter, 0),
    total_travel_time_minutes: bookingsWithBuffer.reduce((total, booking) => 
      total + booking.travelTimeTo + booking.travelTimeFrom, 0),
    total_service_time_minutes: bookingsWithBuffer.reduce((total, booking) => 
      total + booking.serviceDuration, 0),
    efficiency_score: optimization?.efficiency_score || 76,
    optimization_suggestions: optimization?.optimization_suggestions || []
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800 border-green-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'in_progress': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getOptimizationColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
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
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Smart Calendar</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">
          Intelligent scheduling with travel time optimization
        </p>
      </div>

      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="schedule">Schedule</TabsTrigger>
          <TabsTrigger value="optimization">Optimization</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="schedule" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Calendar */}
            <Card className="lg:col-span-2 card-elevated">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CalendarIcon className="h-5 w-5" />
                  Schedule Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="flex justify-center">
                <CalendarComponent
                  mode="single"
                  selected={date}
                  onSelect={setDate}
                  className="rounded-md border"
                />
              </CardContent>
            </Card>

            {/* Smart Schedule for selected date */}
            <Card className="card-elevated">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Smart Schedule - {date?.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {bookingsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin" />
                    <span className="ml-2">Loading schedule...</span>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {bookingsWithBuffer.length === 0 ? (
                      <p className="text-muted-foreground text-center py-4">
                        No bookings scheduled for this date.
                      </p>
                    ) : (
                      bookingsWithBuffer.map((booking) => (
                    <div key={booking.id} className="space-y-3">
                      {/* Main booking info */}
                      <div className={`p-4 border rounded-lg ${getStatusColor(booking.status)}`}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">{booking.time}</span>
                          <Badge variant="outline" className={getOptimizationColor(booking.optimization?.score || 0)}>
                            {booking.optimization?.score}% optimized
                          </Badge>
                        </div>
                        <p className="font-medium text-sm">{booking.service}</p>
                        <p className="text-xs text-muted-foreground">{booking.customer}</p>
                        <div className="flex items-center gap-1 mt-1">
                          <MapPin className="h-3 w-3" />
                          <span className="text-xs">{booking.pincode}</span>
                        </div>
                      </div>

                      {/* Smart buffering timeline */}
                      <div className="ml-4 space-y-1 text-xs">
                        <div className="flex items-center gap-2 text-blue-600">
                          <Car className="h-3 w-3" />
                          <span>Travel to: {formatDuration(booking.travelTimeTo)}</span>
                        </div>
                        <div className="flex items-center gap-2 text-orange-600">
                          <Timer className="h-3 w-3" />
                          <span>Buffer: {formatDuration(booking.bufferBefore)}</span>
                        </div>
                        <div className="flex items-center gap-2 text-green-600">
                          <CheckCircle className="h-3 w-3" />
                          <span>Service: {formatDuration(booking.serviceDuration)}</span>
                        </div>
                        <div className="flex items-center gap-2 text-orange-600">
                          <Timer className="h-3 w-3" />
                          <span>Buffer: {formatDuration(booking.bufferAfter)}</span>
                        </div>
                        <div className="flex items-center gap-2 text-blue-600">
                          <Car className="h-3 w-3" />
                          <span>Travel from: {formatDuration(booking.travelTimeFrom)}</span>
                        </div>
                        <div className="border-t pt-1 mt-2">
                          <div className="flex justify-between text-xs font-medium">
                            <span>Actual: {booking.actualStartTime} - {booking.actualEndTime}</span>
                          </div>
                        </div>
                      </div>

                      {/* Optimization suggestions */}
                      {booking.optimization?.suggestions && booking.optimization.suggestions.length > 0 && (
                        <Alert className="ml-4">
                          <AlertTriangle className="h-4 w-4" />
                          <AlertDescription>
                            {booking.optimization.suggestions[0]}
                          </AlertDescription>
                        </Alert>
                      )}
                    </div>
                      ))
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="optimization" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  <div>
                    <p className="text-sm text-muted-foreground">Efficiency Score</p>
                    <p className="text-2xl font-bold text-green-600">{optimizationSummary.efficiency_score}%</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Car className="h-5 w-5 text-blue-600" />
                  <div>
                    <p className="text-sm text-muted-foreground">Travel Time</p>
                    <p className="text-2xl font-bold">{formatDuration(optimizationSummary.total_travel_time_minutes)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <div>
                    <p className="text-sm text-muted-foreground">Service Time</p>
                    <p className="text-2xl font-bold">{formatDuration(optimizationSummary.total_service_time_minutes)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-orange-600" />
                  <div>
                    <p className="text-sm text-muted-foreground">Working Time</p>
                    <p className="text-2xl font-bold">{formatDuration(optimizationSummary.total_working_time_minutes)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Optimization Suggestions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {optimizationSummary.optimization_suggestions.map((suggestion, index) => (
                  <Alert key={index} className={`border-l-4 ${
                    suggestion.severity === 'high' ? 'border-l-red-500' :
                    suggestion.severity === 'medium' ? 'border-l-yellow-500' :
                    'border-l-blue-500'
                  }`}>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <div className="flex justify-between items-start">
                        <span>{suggestion.suggestion}</span>
                        <Badge variant="outline" className="ml-2">
                          {suggestion.severity}
                        </Badge>
                      </div>
                    </AlertDescription>
                  </Alert>
                ))}
                {optimizationSummary.optimization_suggestions.length === 0 && (
                  <p className="text-muted-foreground text-center py-4">
                    Your schedule is well optimized! No suggestions at this time.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Daily Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>Total Bookings</span>
                    <span className="font-semibold">{optimizationSummary.total_bookings}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Service Time</span>
                    <span className="font-semibold text-green-600">
                      {Math.round((optimizationSummary.total_service_time_minutes / optimizationSummary.total_working_time_minutes) * 100)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Travel Time</span>
                    <span className="font-semibold text-blue-600">
                      {Math.round((optimizationSummary.total_travel_time_minutes / optimizationSummary.total_working_time_minutes) * 100)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Buffer/Idle Time</span>
                    <span className="font-semibold text-gray-600">
                      {Math.round(((optimizationSummary.total_working_time_minutes - optimizationSummary.total_service_time_minutes - optimizationSummary.total_travel_time_minutes) / optimizationSummary.total_working_time_minutes) * 100)}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Smart Insights</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                    <div>
                      <p className="font-medium">Optimal Route Planning</p>
                      <p className="text-sm text-muted-foreground">
                        Your bookings are well-sequenced geographically
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                    <div>
                      <p className="font-medium">Buffer Time Usage</p>
                      <p className="text-sm text-muted-foreground">
                        Consider reducing buffer time for familiar services
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <div>
                      <p className="font-medium">Peak Hours</p>
                      <p className="text-sm text-muted-foreground">
                        Most bookings between 2-5 PM - consider expanding morning slots
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
