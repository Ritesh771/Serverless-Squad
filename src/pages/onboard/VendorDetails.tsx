import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, User, Phone, Mail, MapPin, Briefcase, FileText } from 'lucide-react';
import { toast } from 'sonner';

export default function VendorDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const vendor = {
    id,
    name: 'Mike Johnson',
    email: 'mike.johnson@example.com',
    phone: '+1 234 567 8900',
    service: 'Plumbing',
    experience: '5 years',
    location: 'New York',
    address: '123 Main St, New York, NY 10001',
    certifications: ['Licensed Plumber', 'EPA Certified', 'OSHA Safety'],
    status: 'pending',
    applicationDate: '2025-01-15',
    documents: [
      'License Certificate',
      'Insurance Proof',
      'Background Check',
    ],
  };

  const handleApprove = () => {
    // TODO: Connect to /api/onboard/vendors/:id/approve
    toast.success('Vendor approved successfully!');
    navigate('/onboard/approved-vendors');
  };

  const handleReject = () => {
    // TODO: Connect to /api/onboard/vendors/:id/reject
    toast.error('Vendor application rejected');
    navigate('/onboard/vendor-queue');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-6">
      <Button variant="ghost" onClick={() => navigate(-1)}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back
      </Button>

      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">{vendor.name}</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">Application ID: #{vendor.id}</p>
        </div>
        <Badge>{vendor.status}</Badge>
      </div>

      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Vendor Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <User className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Full Name</p>
                  <p className="text-sm text-muted-foreground">{vendor.name}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Mail className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Email</p>
                  <p className="text-sm text-muted-foreground">{vendor.email}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Phone className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Phone</p>
                  <p className="text-sm text-muted-foreground">{vendor.phone}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Location</p>
                  <p className="text-sm text-muted-foreground">{vendor.address}</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <Briefcase className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Service Type</p>
                  <p className="text-sm text-muted-foreground">{vendor.service}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Briefcase className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Experience</p>
                  <p className="text-sm text-muted-foreground">{vendor.experience}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Application Date</p>
                  <p className="text-sm text-muted-foreground">{vendor.applicationDate}</p>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-medium mb-3">Certifications</h4>
            <div className="flex flex-wrap gap-2">
              {vendor.certifications.map((cert, index) => (
                <Badge key={index} variant="secondary">
                  {cert}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-medium mb-3">Submitted Documents</h4>
            <div className="space-y-2">
              {vendor.documents.map((doc, index) => (
                <div key={index} className="flex items-center justify-between p-3 border border-border rounded-lg">
                  <span className="text-sm">{doc}</span>
                  <Button variant="ghost" size="sm">
                    View
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex flex-col sm:flex-row gap-3 sm:justify-end">
        <Button variant="outline" onClick={handleReject} className="w-full sm:w-auto">
          Reject Application
        </Button>
        <Button onClick={handleApprove} className="w-full sm:w-auto">
          Approve Vendor
        </Button>
      </div>
    </div>
  );
}
