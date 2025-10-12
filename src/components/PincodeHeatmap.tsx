import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { MapPin, TrendingUp, Users, DollarSign } from 'lucide-react';

interface PincodeData {
  pincode: string;
  lat: number;
  lng: number;
  jobCount: number;
  vendorCount: number;
  revenue: number;
  density: number; // 0-100 scale for heatmap intensity
}

interface HeatmapLegendItem {
  color: string;
  label: string;
  range: string;
}

export const PincodeHeatmap = () => {
  const [pincodeData, setPincodeData] = useState<PincodeData[]>([
    { pincode: '10001', lat: 40.7505, lng: -73.9934, jobCount: 45, vendorCount: 12, revenue: 3600, density: 90 },
    { pincode: '10002', lat: 40.7128, lng: -73.9852, jobCount: 38, vendorCount: 8, revenue: 3040, density: 75 },
    { pincode: '10003', lat: 40.7295, lng: -73.9857, jobCount: 32, vendorCount: 7, revenue: 2560, density: 60 },
    { pincode: '10004', lat: 40.7074, lng: -74.0113, jobCount: 28, vendorCount: 6, revenue: 2240, density: 50 },
    { pincode: '10005', lat: 40.7064, lng: -74.0081, jobCount: 25, vendorCount: 5, revenue: 2000, density: 45 },
    { pincode: '10006', lat: 40.7081, lng: -74.0138, jobCount: 22, vendorCount: 4, revenue: 1760, density: 40 },
    { pincode: '10007', lat: 40.7147, lng: -74.0121, jobCount: 18, vendorCount: 3, revenue: 1440, density: 30 },
    { pincode: '10009', lat: 40.7253, lng: -73.9831, jobCount: 35, vendorCount: 9, revenue: 2800, density: 70 },
    { pincode: '10010', lat: 40.7380, lng: -73.9804, jobCount: 42, vendorCount: 11, revenue: 3360, density: 85 },
    { pincode: '10011', lat: 40.7390, lng: -74.0022, jobCount: 30, vendorCount: 7, revenue: 2400, density: 55 },
  ]);

  const [viewMode, setViewMode] = useState<'jobs' | 'vendors' | 'revenue'>('jobs');
  const [densityThreshold, setDensityThreshold] = useState([50]);
  const [filteredData, setFilteredData] = useState<PincodeData[]>([]);

  // Filter data based on density threshold
  useEffect(() => {
    const filtered = pincodeData.filter(item => item.density >= densityThreshold[0]);
    setFilteredData(filtered);
  }, [pincodeData, densityThreshold]);

  // Calculate circle size based on view mode
  const getCircleRadius = (item: PincodeData) => {
    switch (viewMode) {
      case 'jobs':
        return Math.max(10, item.jobCount * 2);
      case 'vendors':
        return Math.max(10, item.vendorCount * 5);
      case 'revenue':
        return Math.max(10, item.revenue / 100);
      default:
        return 20;
    }
  };

  // Calculate circle color based on density
  const getCircleColor = (density: number) => {
    if (density >= 80) return '#ef4444'; // red
    if (density >= 60) return '#f97316'; // orange
    if (density >= 40) return '#eab308'; // yellow
    if (density >= 20) return '#22c55e'; // green
    return '#3b82f6'; // blue
  };

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(amount);
  };

  // Heatmap legend
  const heatmapLegend: HeatmapLegendItem[] = [
    { color: '#3b82f6', label: 'Low Density', range: '0-19%' },
    { color: '#22c55e', label: 'Medium-Low', range: '20-39%' },
    { color: '#eab308', label: 'Medium', range: '40-59%' },
    { color: '#f97316', label: 'Medium-High', range: '60-79%' },
    { color: '#ef4444', label: 'High Density', range: '80-100%' }
  ];

  return (
    <Card className="card-elevated">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MapPin className="h-5 w-5 text-primary" />
          Service Activity Heatmap
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <div className="flex-1">
            <label className="text-sm font-medium mb-2 block">View Mode</label>
            <Select value={viewMode} onValueChange={(value: 'jobs' | 'vendors' | 'revenue') => setViewMode(value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="jobs">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Job Density
                  </div>
                </SelectItem>
                <SelectItem value="vendors">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    Vendor Coverage
                  </div>
                </SelectItem>
                <SelectItem value="revenue">
                  <div className="flex items-center gap-2">
                    <DollarSign className="h-4 w-4" />
                    Revenue
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex-1">
            <label className="text-sm font-medium mb-2 block">
              Density Threshold: {densityThreshold[0]}%
            </label>
            <Slider
              value={densityThreshold}
              onValueChange={setDensityThreshold}
              max={100}
              step={5}
              className="w-full"
            />
          </div>
        </div>

        <div className="h-64 sm:h-80 rounded-lg overflow-hidden relative bg-muted flex items-center justify-center">
          <div className="text-center p-4">
            <MapPin className="h-12 w-12 text-primary mx-auto mb-2" />
            <p className="text-muted-foreground">Map visualization would appear here</p>
            <p className="text-xs text-muted-foreground mt-1">
              Interactive pincode heatmap showing service activity
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mt-4">
          {heatmapLegend.map((item, index) => (
            <div key={index} className="flex items-center gap-1">
              <div 
                className="w-4 h-4 rounded-full" 
                style={{ backgroundColor: item.color }}
              />
              <span className="text-xs">{item.label} ({item.range})</span>
            </div>
          ))}
        </div>

        <div className="mt-4 text-sm text-muted-foreground">
          <p>
            Click on circles to view detailed pincode information. 
            Adjust view mode and density threshold to focus on specific metrics.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};