import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Search, Calendar, User, CheckCircle, Clock, AlertTriangle, Eye } from 'lucide-react';
import { toast } from 'sonner';
import { SignaturePad } from '@/components/SignaturePad';

interface SignatureRecord {
  id: string;
  bookingId: string;
  customer: string;
  vendor: string;
  service: string;
  status: 'pending' | 'completed' | 'expired';
  requestedAt: string;
  signedAt?: string;
  signatureData?: string;
}

export default function SignatureVault() {
  const [signatures, setSignatures] = useState<SignatureRecord[]>([
    {
      id: '1',
      bookingId: 'BK-12345',
      customer: 'Jane Doe',
      vendor: 'John Smith',
      service: 'Plumbing Repair',
      status: 'completed',
      requestedAt: '2025-01-15T10:30:00Z',
      signedAt: '2025-01-15T14:45:00Z',
      signatureData: ''
    },
    {
      id: '2',
      bookingId: 'BK-12346',
      customer: 'Bob Wilson',
      vendor: 'Sarah Johnson',
      service: 'AC Maintenance',
      status: 'pending',
      requestedAt: '2025-01-14T09:15:00Z'
    },
    {
      id: '3',
      bookingId: 'BK-12347',
      customer: 'Alice Brown',
      vendor: 'Mike Davis',
      service: 'Electrical Inspection',
      status: 'expired',
      requestedAt: '2025-01-10T11:20:00Z'
    }
  ]);

  const [search, setSearch] = useState('');
  const [selectedSignature, setSelectedSignature] = useState<SignatureRecord | null>(null);
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed' | 'expired'>('all');

  const filteredSignatures = signatures.filter(sig => {
    const matchesSearch = 
      sig.customer.toLowerCase().includes(search.toLowerCase()) ||
      sig.vendor.toLowerCase().includes(search.toLowerCase()) ||
      sig.bookingId.toLowerCase().includes(search.toLowerCase());
    
    const matchesFilter = filter === 'all' || sig.status === filter;
    
    return matchesSearch && matchesFilter;
  });

  const handleViewSignature = (signature: SignatureRecord) => {
    setSelectedSignature(signature);
  };

  const handleSignatureSave = (signatureData: string) => {
    if (selectedSignature) {
      setSignatures(prev => prev.map(sig => 
        sig.id === selectedSignature.id 
          ? { ...sig, signatureData, status: 'completed', signedAt: new Date().toISOString() } 
          : sig
      ));
      setSelectedSignature({ ...selectedSignature, signatureData, status: 'completed', signedAt: new Date().toISOString() });
      toast.success('Signature updated successfully');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-success/10 text-success hover:bg-success/10"><CheckCircle className="h-3 w-3 mr-1" />Completed</Badge>;
      case 'pending':
        return <Badge className="bg-warning/10 text-warning hover:bg-warning/10"><Clock className="h-3 w-3 mr-1" />Pending</Badge>;
      case 'expired':
        return <Badge className="bg-destructive/10 text-destructive hover:bg-destructive/10"><AlertTriangle className="h-3 w-3 mr-1" />Expired</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Signature Vault</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage and verify all customer signatures</p>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by customer, vendor, or booking ID..."
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          <Button 
            variant={filter === 'all' ? 'default' : 'outline'} 
            onClick={() => setFilter('all')}
            size="sm"
          >
            All
          </Button>
          <Button 
            variant={filter === 'pending' ? 'default' : 'outline'} 
            onClick={() => setFilter('pending')}
            size="sm"
          >
            Pending
          </Button>
          <Button 
            variant={filter === 'completed' ? 'default' : 'outline'} 
            onClick={() => setFilter('completed')}
            size="sm"
          >
            Completed
          </Button>
          <Button 
            variant={filter === 'expired' ? 'default' : 'outline'} 
            onClick={() => setFilter('expired')}
            size="sm"
          >
            Expired
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Signature List */}
        <Card className="lg:col-span-2 card-elevated">
          <CardHeader>
            <CardTitle>Signature Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Booking</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Vendor</TableHead>
                  <TableHead>Service</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredSignatures.map((signature) => (
                  <TableRow key={signature.id}>
                    <TableCell className="font-medium">{signature.bookingId}</TableCell>
                    <TableCell>{signature.customer}</TableCell>
                    <TableCell>{signature.vendor}</TableCell>
                    <TableCell>{signature.service}</TableCell>
                    <TableCell>{formatDate(signature.requestedAt)}</TableCell>
                    <TableCell>{getStatusBadge(signature.status)}</TableCell>
                    <TableCell>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleViewSignature(signature)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            
            {filteredSignatures.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No signatures found
              </div>
            )}
          </CardContent>
        </Card>

        {/* Signature Preview/Editor */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>
              {selectedSignature 
                ? `Signature: ${selectedSignature.bookingId}` 
                : 'Signature Preview'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedSignature ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <p className="text-muted-foreground">Customer</p>
                    <p className="font-medium">{selectedSignature.customer}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Vendor</p>
                    <p className="font-medium">{selectedSignature.vendor}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Service</p>
                    <p className="font-medium">{selectedSignature.service}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Requested</p>
                    <p className="font-medium">{formatDate(selectedSignature.requestedAt)}</p>
                  </div>
                  {selectedSignature.signedAt && (
                    <div>
                      <p className="text-muted-foreground">Signed</p>
                      <p className="font-medium">{formatDate(selectedSignature.signedAt)}</p>
                    </div>
                  )}
                </div>
                
                <div className="pt-2">
                  <SignaturePad 
                    onSave={handleSignatureSave}
                    bookingId={selectedSignature.bookingId}
                    isLocked={selectedSignature.status === 'completed'}
                    initialSignature={selectedSignature.signatureData}
                  />
                </div>
                
                <div className="flex gap-2 pt-2">
                  <Button variant="outline" className="flex-1" size="sm">
                    Download
                  </Button>
                  <Button variant="outline" className="flex-1" size="sm">
                    Verify
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 text-muted-foreground">
                <div className="text-center">
                  <Eye className="h-12 w-12 mx-auto mb-2" />
                  <p>Select a signature to view details</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}