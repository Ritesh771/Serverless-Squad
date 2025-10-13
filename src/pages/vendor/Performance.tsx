import { useQuery } from '@tanstack/react-query';
import { vendorService } from '@/services/vendorService';
import { toast } from 'sonner';
import { Loader2, Trophy, Star, CheckCircle, Clock, AlertTriangle, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface PerformanceMetrics {
  id: string;
  vendor: string;
  total_jobs: number;
  completed_jobs: number;
  cancelled_jobs: number;
  total_ratings: number;
  rating_sum: number;
  disputes_raised: number;
  disputes_against: number;
  on_time_completions: number;
  total_completions: number;
  bonus_points: number;
  tier: 'bronze' | 'silver' | 'gold';
  avg_rating: number;
  completion_rate: number;
  on_time_rate: number;
  dispute_rate: number;
  last_calculated: string;
}

export default function VendorPerformance() {
  // Fetch performance metrics using the new vendor service
  const { data: metrics, isLoading, error } = useQuery({
    queryKey: ['vendor-performance'],
    queryFn: () => vendorService.getPerformance(),
  });

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'gold': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'silver': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'bronze': return 'bg-amber-100 text-amber-800 border-amber-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'gold': return <Trophy className="h-5 w-5 text-yellow-500" />;
      case 'silver': return <Trophy className="h-5 w-5 text-gray-400" />;
      case 'bronze': return <Trophy className="h-5 w-5 text-amber-700" />;
      default: return <Trophy className="h-5 w-5 text-gray-400" />;
    }
  };

  // Data for charts
  const performanceData = metrics ? [
    { name: 'Completion', value: metrics.completion_rate },
    { name: 'On-Time', value: metrics.on_time_rate },
    { name: 'Rating', value: metrics.avg_rating * 20 }, // Convert 5-star to percentage
    { name: 'Dispute', value: 100 - metrics.dispute_rate },
  ] : [];

  const COLORS = ['#10B981', '#3B82F6', '#8B5CF6', '#EF4444'];

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-center">
          <p className="text-destructive mb-4">Failed to load performance data</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-primary text-primary-foreground rounded"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-muted-foreground">No performance data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Performance Dashboard</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">
          Track your performance metrics and bonus points
        </p>
      </div>

      {/* Tier Badge */}
      <Card className="card-elevated">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getTierIcon(metrics.tier)}
              <div>
                <h2 className="text-xl font-bold">Performance Tier</h2>
                <p className="text-muted-foreground">Your current standing</p>
              </div>
            </div>
            <Badge className={`px-4 py-2 text-lg font-bold ${getTierColor(metrics.tier)}`}>
              {metrics.tier.charAt(0).toUpperCase() + metrics.tier.slice(1)} Tier
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="card-elevated">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-full">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Completion Rate</p>
                <p className="text-2xl font-bold">{metrics.completion_rate}%</p>
              </div>
            </div>
            <Progress value={metrics.completion_rate} className="mt-3" />
          </CardContent>
        </Card>

        <Card className="card-elevated">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-full">
                <Star className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Average Rating</p>
                <p className="text-2xl font-bold">{metrics.avg_rating}/5</p>
              </div>
            </div>
            <Progress value={metrics.avg_rating * 20} className="mt-3" />
          </CardContent>
        </Card>

        <Card className="card-elevated">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-full">
                <Clock className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">On-Time Rate</p>
                <p className="text-2xl font-bold">{metrics.on_time_rate}%</p>
              </div>
            </div>
            <Progress value={metrics.on_time_rate} className="mt-3" />
          </CardContent>
        </Card>

        <Card className="card-elevated">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-100 rounded-full">
                <TrendingUp className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Bonus Points</p>
                <p className="text-2xl font-bold">{metrics.bonus_points}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Performance Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={performanceData}
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip 
                    formatter={(value) => [`${value}%`, 'Percentage']}
                    labelFormatter={(label) => `Metric: ${label}`}
                  />
                  <Bar dataKey="value">
                    {performanceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Job Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-muted-foreground">Total Jobs</span>
                  <span className="font-medium">{metrics.total_jobs}</span>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-muted-foreground">Completed Jobs</span>
                  <span className="font-medium">{metrics.completed_jobs}</span>
                </div>
                <Progress 
                  value={metrics.total_jobs > 0 ? (metrics.completed_jobs / metrics.total_jobs) * 100 : 0} 
                  className="h-2" 
                />
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-muted-foreground">On-Time Completions</span>
                  <span className="font-medium">{metrics.on_time_completions}/{metrics.total_completions}</span>
                </div>
                <Progress 
                  value={metrics.total_completions > 0 ? (metrics.on_time_completions / metrics.total_completions) * 100 : 0} 
                  className="h-2" 
                />
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-muted-foreground">Disputes Against</span>
                  <span className="font-medium">{metrics.disputes_against}</span>
                </div>
                <Progress 
                  value={metrics.completed_jobs > 0 ? (metrics.disputes_against / metrics.completed_jobs) * 100 : 0} 
                  className="h-2" 
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bonus Information */}
      <Card className="card-elevated">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Bonus Points System
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <h3 className="font-medium text-green-800">How You Earn Points</h3>
              <ul className="mt-2 text-sm text-green-700 space-y-1">
                <li>• 2 points per completed job</li>
                <li>• 10 points per average rating point</li>
                <li>• Bonus for on-time completions</li>
              </ul>
            </div>

            <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
              <h3 className="font-medium text-amber-800">Tier Requirements</h3>
              <ul className="mt-2 text-sm text-amber-700 space-y-1">
                <li>• Gold: 90+ points</li>
                <li>• Silver: 70-89 points</li>
                <li>• Bronze: Below 70 points</li>
              </ul>
            </div>

            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h3 className="font-medium text-blue-800">Monthly Bonuses</h3>
              <ul className="mt-2 text-sm text-blue-700 space-y-1">
                <li>• Gold tier: 15% bonus on earnings</li>
                <li>• Silver tier: 10% bonus on earnings</li>
                <li>• Bronze tier: 5% bonus on earnings</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}