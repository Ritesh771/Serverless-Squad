import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DollarSign, TrendingUp, Calendar, ArrowUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function VendorEarnings() {
  const recentTransactions = [
    { id: '1', date: '2025-01-15', customer: 'John Doe', service: 'Plumbing', amount: '$80', status: 'Completed' },
    { id: '2', date: '2025-01-14', customer: 'Jane Smith', service: 'Electrical', amount: '$100', status: 'Pending' },
    { id: '3', date: '2025-01-13', customer: 'Bob Wilson', service: 'HVAC', amount: '$120', status: 'Completed' },
    { id: '4', date: '2025-01-12', customer: 'Sarah Davis', service: 'Plumbing', amount: '$90', status: 'Completed' },
  ];

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Earnings</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Track your payments and transactions</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Earnings"
          value="$12,450"
          icon={DollarSign}
          description="All time"
        />
        <DashboardCard
          title="This Month"
          value="$1,240"
          icon={TrendingUp}
          trend={{ value: 12, isPositive: true }}
        />
        <DashboardCard
          title="Pending Payouts"
          value="$200"
          icon={Calendar}
          description="2 transactions"
        />
        <DashboardCard
          title="This Week"
          value="$380"
          icon={ArrowUpRight}
          trend={{ value: 8, isPositive: true }}
        />
      </div>

      {/* Transactions */}
      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentTransactions.map((transaction) => (
              <Link
                key={transaction.id}
                to={`/vendor/earnings/${transaction.id}`}
                className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted transition-colors"
              >
                <div>
                  <p className="font-medium">{transaction.service}</p>
                  <p className="text-sm text-muted-foreground">
                    {transaction.customer} • {transaction.date}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-primary">{transaction.amount}</p>
                  <span
                    className={`text-xs ${
                      transaction.status === 'Completed'
                        ? 'text-success'
                        : 'text-warning'
                    }`}
                  >
                    {transaction.status}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
