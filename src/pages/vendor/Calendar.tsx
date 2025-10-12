import { useState } from 'react';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function VendorCalendar() {
  const [date, setDate] = useState<Date | undefined>(new Date());

  const jobsForDate = [
    { time: '09:00 AM', customer: 'John Doe', service: 'Plumbing', status: 'confirmed' },
    { time: '02:00 PM', customer: 'Jane Smith', service: 'Electrical', status: 'pending' },
    { time: '04:30 PM', customer: 'Bob Wilson', service: 'HVAC', status: 'confirmed' },
  ];

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">My Calendar</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">View and manage your job schedule</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar */}
        <Card className="lg:col-span-2 card-elevated">
          <CardHeader>
            <CardTitle>Schedule</CardTitle>
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

        {/* Jobs for selected date */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>
              Jobs for {date?.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {jobsForDate.map((job, index) => (
                <div key={index} className="p-3 border border-border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-primary">{job.time}</span>
                    <Badge variant={job.status === 'confirmed' ? 'default' : 'secondary'}>
                      {job.status}
                    </Badge>
                  </div>
                  <p className="font-medium text-sm">{job.service}</p>
                  <p className="text-xs text-muted-foreground">{job.customer}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
