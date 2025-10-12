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
  Car, Timer, Route
} from 'lucide-react';
import { format, addMinutes, isSameDay } from 'date-fns';

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
  const [optimization, setOptimization] = useState<ScheduleOptimization | null>(null);
  const [loading, setLoading] = useState(false);

  // Mock data with smart buffering information
  const bookingsWithBuffer: BookingWithBuffer[] = [
    {
      id: '1',
      time: '09:00 AM',
      customer: 'John Doe',
      service: 'Plumbing Repair',
      status: 'confirmed',
      pincode: '110001',
      travelTimeTo: 25,
      travelTimeFrom: 25,
      serviceDuration: 90,
      bufferBefore: 15,
      bufferAfter: 15,
      actualStartTime: '08:20 AM',
      actualEndTime: '11:10 AM',
      optimization: {
        score: 85,
        suggestions: []
      }
    },
    {
      id: '2',
      time: '02:00 PM',
      customer: 'Jane Smith',
      service: 'Electrical Inspection',
      status: 'pending',
      pincode: '110045',
      travelTimeTo: 35,
      travelTimeFrom: 35,
      serviceDuration: 60,
      bufferBefore: 15,
      bufferAfter: 15,
      actualStartTime: '01:10 PM',
      actualEndTime: '04:05 PM',
      optimization: {
        score: 65,
        suggestions: ['High travel time - consider route optimization']
      }
    },
    {
      id: '3',
      time: '04:30 PM',
      customer: 'Bob Wilson',
      service: 'HVAC Maintenance',
      status: 'confirmed',
      pincode: '110019',
      travelTimeTo: 15,
      travelTimeFrom: 15,
      serviceDuration: 120,
      bufferBefore: 15,
      bufferAfter: 15,
      actualStartTime: '04:00 PM',
      actualEndTime: '07:05 PM',
      optimization: {
        score: 92,
        suggestions: []
      }
    }
  ];

  const optimizationSummary: ScheduleOptimization = {
    total_bookings: 3,
    total_working_time_minutes: 645, // 10h 45m
    total_travel_time_minutes: 150,  // 2h 30m
    total_service_time_minutes: 270, // 4h 30m
    efficiency_score: 76,
    optimization_suggestions: [
      {
        type: 'excessive_travel',
        booking_id: '2',
        suggestion: 'Consider rearranging to reduce travel time',
        severity: 'medium'
      }
    ]
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
                <div className="space-y-4">
                  {bookingsWithBuffer.map((booking) => (
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
                  ))}
                </div>
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
