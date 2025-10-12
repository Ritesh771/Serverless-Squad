import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ArrowLeft, User, Phone, Mail, MapPin, Briefcase, FileText, AlertTriangle, Check, History, Save, Eye } from 'lucide-react';
import { toast } from 'sonner';
import { onboardService, SignatureLog, AuditLog as ServiceAuditLog } from '@/services/vendorService';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';

interface Vendor {
  id: string;
  name: string;
  email: string;
  phone: string;
  service_category: string;
  experience: number;
  pincode: string;
  status: string;
  ai_flag?: boolean;
  flag_reason?: string;
  flagged_at?: string;
  created_at: string;
  id_proof?: string;
  address_proof?: string;
  profile_photo?: string;
}

interface LocalAuditLog {
  id: string;
  user: string;
  action: string;
  timestamp: string;
  old_values: Record<string, string | number | boolean | null>;
  new_values: Record<string, string | number | boolean | null>;
}

export default function VendorDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [flagReason, setFlagReason] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showSignatures, setShowSignatures] = useState(false);
  const [editData, setEditData] = useState({
    name: '',
    email: '',
    phone: '',
    service_category: '',
    experience: 0,
    pincode: '',
  });
  const [auditLogs, setAuditLogs] = useState<LocalAuditLog[]>([]);
  const [signatures, setSignatures] = useState<SignatureLog[]>([]);
  const [vendor, setVendor] = useState<Vendor | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch vendor details and related data
  useEffect(() => {
    if (id) {
      fetchVendorDetails();
    }
  }, [id]);

  const fetchVendorDetails = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/onboard/vendors/${id}/`);
      setVendor(response.data);
      setEditData({
        name: response.data.name,
        email: response.data.email,
        phone: response.data.phone,
        service_category: response.data.service_category,
        experience: response.data.experience,
        pincode: response.data.pincode,
      });
    } catch (error) {
      toast.error('Failed to fetch vendor details');
    } finally {
      setLoading(false);
    }
  };

  const fetchSignatureLogs = async () => {
    try {
      const data = await onboardService.getSignatureLogs(id!);
      setSignatures(data);
    } catch (error) {
      toast.error('Failed to fetch signature logs');
    }
  };

  const fetchEditHistory = async () => {
    try {
      const data = await onboardService.getEditHistory(id!);
      setAuditLogs(data);
    } catch (error) {
      toast.error('Failed to fetch edit history');
    }
  };

  const handleApprove = async () => {
    try {
      await api.post(ENDPOINTS.ONBOARD.APPROVE(id!), {});
      toast.success('Vendor approved successfully!');
      navigate('/onboard/approved-vendors');
    } catch (error) {
      toast.error('Failed to approve vendor');
    }
  };

  const handleReject = async () => {
    try {
      await api.post(ENDPOINTS.ONBOARD.REJECT(id!), {});
      toast.error('Vendor application rejected');
      navigate('/onboard/vendor-queue');
    } catch (error) {
      toast.error('Failed to reject vendor');
    }
  };

  const handleFlagApplication = async () => {
    if (!flagReason.trim()) {
      toast.error('Please provide a reason for flagging this application');
      return;
    }
    
    try {
      await api.post(`/api/onboard/vendors/${id}/flag_application/`, {
        flag_reason: flagReason
      });
      toast.success('Application flagged successfully');
      setFlagReason('');
      fetchVendorDetails(); // Refresh vendor data
    } catch (error) {
      toast.error('Failed to flag application');
    }
  };

  const handleUnflagApplication = async () => {
    try {
      await api.post(`/api/onboard/vendors/${id}/unflag_application/`, {});
      toast.success('Application unflagged successfully');
      fetchVendorDetails(); // Refresh vendor data
    } catch (error) {
      toast.error('Failed to unflag application');
    }
  };

  const handleSaveChanges = async () => {
    try {
      await api.put(`/api/onboard/vendors/${id}/`, editData);
      toast.success('Edit saved — changes logged to audit trail');
      setIsEditing(false);
      fetchVendorDetails(); // Refresh vendor data
    } catch (error) {
      toast.error('Failed to save changes');
    }
  };

  const handleViewHistory = async () => {
    await fetchEditHistory();
    setShowHistory(true);
  };

  const handleViewSignatures = async () => {
    await fetchSignatureLogs();
    setShowSignatures(true);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'signed':
        return <Badge variant="default">Signed</Badge>;
      case 'pending':
        return <Badge variant="secondary">Pending</Badge>;
      case 'expired':
        return <Badge variant="destructive">Expired</Badge>;
      case 'disputed':
        return <Badge variant="outline">Disputed</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  if (!vendor) {
    return <div className="flex justify-center items-center h-64">Vendor not found</div>;
  }

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
        <div className="flex flex-wrap gap-2">
          <Badge>{vendor.status}</Badge>
          {vendor.ai_flag && (
            <Badge variant="destructive" className="flex items-center gap-1">
              <AlertTriangle className="h-3 w-3" />
              Flagged
            </Badge>
          )}
        </div>
      </div>

      {vendor.ai_flag && vendor.flag_reason && vendor.flagged_at && (
        <Card className="border-warning bg-warning/10">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-warning mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-medium text-warning">AI Flagged Application</h4>
                <p className="text-sm text-warning/80 mt-1">{vendor.flag_reason}</p>
                <p className="text-xs text-warning/60 mt-1">
                  Flagged on {new Date(vendor.flagged_at).toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="card-elevated">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
            <CardTitle>Vendor Information</CardTitle>
            <div className="flex gap-2">
              {isEditing ? (
                <Button onClick={handleSaveChanges} className="flex items-center gap-2">
                  <Save className="h-4 w-4" />
                  Save Changes
                </Button>
              ) : (
                <Button onClick={() => setIsEditing(true)} variant="outline">
                  Edit Information
                </Button>
              )}
              <Button onClick={handleViewHistory} variant="outline" className="flex items-center gap-2">
                <History className="h-4 w-4" />
                View Edit History
              </Button>
              <Button onClick={handleViewSignatures} variant="outline" className="flex items-center gap-2">
                <Eye className="h-4 w-4" />
                Signature Logs
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <User className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Full Name</p>
                  {isEditing ? (
                    <Input
                      value={editData.name}
                      onChange={(e) => setEditData({...editData, name: e.target.value})}
                      className="mt-1"
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">{vendor.name}</p>
                  )}
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Mail className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Email</p>
                  {isEditing ? (
                    <Input
                      value={editData.email}
                      onChange={(e) => setEditData({...editData, email: e.target.value})}
                      className="mt-1"
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">{vendor.email}</p>
                  )}
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Phone className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Phone</p>
                  {isEditing ? (
                    <Input
                      value={editData.phone}
                      onChange={(e) => setEditData({...editData, phone: e.target.value})}
                      className="mt-1"
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">{vendor.phone}</p>
                  )}
                </div>
              </div>

              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Location</p>
                  {isEditing ? (
                    <Input
                      value={editData.pincode}
                      onChange={(e) => setEditData({...editData, pincode: e.target.value})}
                      className="mt-1"
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">{vendor.pincode}</p>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <Briefcase className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Service Type</p>
                  {isEditing ? (
                    <Input
                      value={editData.service_category}
                      onChange={(e) => setEditData({...editData, service_category: e.target.value})}
                      className="mt-1"
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">{vendor.service_category}</p>
                  )}
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Briefcase className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Experience</p>
                  {isEditing ? (
                    <Input
                      type="number"
                      value={editData.experience || ''}
                      onChange={(e) => setEditData({...editData, experience: parseInt(e.target.value) || 0})}
                      className="mt-1"
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">{vendor.experience} years</p>
                  )}
                </div>
              </div>

              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Application Date</p>
                  <p className="text-sm text-muted-foreground">{formatDate(vendor.created_at)}</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Edit History Modal */}
      {showHistory && (
        <Card className="card-elevated">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Edit History</CardTitle>
              <Button variant="ghost" onClick={() => setShowHistory(false)}>×</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {auditLogs.length > 0 ? (
                auditLogs.map((log) => (
                  <div key={log.id} className="border-b border-border pb-4 last:border-0 last:pb-0">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{log.user}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(log.timestamp).toLocaleString()}
                        </p>
                      </div>
                      <Badge variant="outline">{log.action}</Badge>
                    </div>
                    <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div>
                        <p className="font-medium text-muted-foreground">Before:</p>
                        <pre className="bg-muted p-2 rounded text-xs overflow-x-auto">
                          {JSON.stringify(log.old_values, null, 2)}
                        </pre>
                      </div>
                      <div>
                        <p className="font-medium text-muted-foreground">After:</p>
                        <pre className="bg-muted p-2 rounded text-xs overflow-x-auto">
                          {JSON.stringify(log.new_values, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground text-center py-4">No edit history found</p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Signature Logs Modal */}
      {showSignatures && (
        <Card className="card-elevated">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Signature Logs</CardTitle>
              <Button variant="ghost" onClick={() => setShowSignatures(false)}>×</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {signatures.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Job ID</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>Service</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Requested</TableHead>
                      <TableHead>Signed</TableHead>
                      <TableHead>Rating</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {signatures.map((signature) => (
                      <TableRow key={signature.id}>
                        <TableCell className="font-medium">{signature.booking.id}</TableCell>
                        <TableCell>{signature.customer.get_full_name}</TableCell>
                        <TableCell>{signature.booking.service.name}</TableCell>
                        <TableCell>{getStatusBadge(signature.status)}</TableCell>
                        <TableCell>{formatDate(signature.requested_at)}</TableCell>
                        <TableCell>
                          {signature.signed_at ? formatDate(signature.signed_at) : '-'}
                        </TableCell>
                        <TableCell>
                          {signature.satisfaction_rating ? `${signature.satisfaction_rating}/5` : '-'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-muted-foreground text-center py-4">No signature logs found</p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Manual Flagging Section */}
      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Flag Application</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {vendor.ai_flag ? (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                This application is currently flagged. You can remove the flag if you've reviewed and approved the concerns.
              </p>
              <Button variant="outline" onClick={handleUnflagApplication} className="flex items-center gap-2">
                <Check className="h-4 w-4" />
                Remove Flag
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                If you've identified issues with this application, you can manually flag it for further review.
              </p>
              <Textarea
                placeholder="Reason for flagging this application..."
                value={flagReason}
                onChange={(e) => setFlagReason(e.target.value)}
                rows={3}
              />
              <Button onClick={handleFlagApplication} variant="destructive" className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                Flag Application
              </Button>
            </div>
          )}
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