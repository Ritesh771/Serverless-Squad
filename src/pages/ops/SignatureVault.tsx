import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, CheckCircle, Hash, Calendar } from 'lucide-react';
import { useState } from 'react';

const mockSignatures = [
  { id: '1', bookingId: 'BK-12345', customer: 'Jane Doe', vendor: 'John Smith', date: '2025-01-15', hash: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb', verified: true },
  { id: '2', bookingId: 'BK-12346', customer: 'Bob Wilson', vendor: 'Sarah Johnson', date: '2025-01-14', hash: '0x8f3a2b1c9d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8', verified: true },
  { id: '3', bookingId: 'BK-12347', customer: 'Alice Brown', vendor: 'Mike Davis', date: '2025-01-13', hash: '0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0', verified: true },
];

export default function SignatureVault() {
  const [search, setSearch] = useState('');

  const filteredSignatures = mockSignatures.filter((sig) =>
    sig.bookingId.toLowerCase().includes(search.toLowerCase()) ||
    sig.customer.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Signature Vault</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">View and verify all digital signatures</p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search by booking ID or customer..."
          className="pl-10"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Signatures */}
      <div className="grid grid-cols-1 gap-4">
        {filteredSignatures.map((sig) => (
          <Card key={sig.id} className="card-elevated">
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold">Booking {sig.bookingId}</h3>
                      <Badge className="bg-success text-success-foreground">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Verified
                      </Badge>
                    </div>
                    <div className="space-y-1 text-sm text-muted-foreground">
                      <p>
                        <span className="font-medium">Customer:</span> {sig.customer}
                      </p>
                      <p>
                        <span className="font-medium">Vendor:</span> {sig.vendor}
                      </p>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {sig.date}
                      </div>
                    </div>
                  </div>

                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                </div>

                <div className="p-3 bg-muted rounded-lg">
                  <div className="flex items-start gap-2">
                    <Hash className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-xs text-muted-foreground mb-1">
                        Blockchain Hash:
                      </p>
                      <code className="text-xs font-mono break-all">{sig.hash}</code>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
