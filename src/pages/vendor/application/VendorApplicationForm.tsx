import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'sonner';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';

interface VendorApplicationData {
  name: string;
  email: string;
  phone: string;
  pincode: string;
  service_category: string;
  experience: number;
  id_proof: File | null;
  address_proof: File | null;
  profile_photo: File | null;
  terms_accepted: boolean;
}

export default function VendorApplicationForm() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<VendorApplicationData>({
    name: '',
    email: '',
    phone: '',
    pincode: '',
    service_category: '',
    experience: 0,
    id_proof: null,
    address_proof: null,
    profile_photo: null,
    terms_accepted: false,
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const serviceCategories = [
    'Plumbing',
    'Electrical',
    'HVAC',
    'Carpentry',
    'Painting',
    'Cleaning',
    'Pest Control',
    'Appliance Repair',
    'Home Security',
    'Landscaping'
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, fieldName: string) => {
    if (e.target.files && e.target.files.length > 0) {
      setFormData(prev => ({ ...prev, [fieldName]: e.target.files![0] }));
    }
  };

  const handleCheckboxChange = (checked: boolean) => {
    setFormData(prev => ({ ...prev, terms_accepted: checked }));
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    if (!formData.phone.trim()) newErrors.phone = 'Phone is required';
    if (!formData.pincode.trim()) newErrors.pincode = 'Pincode is required';
    if (!formData.service_category) newErrors.service_category = 'Service category is required';
    if (formData.experience <= 0) newErrors.experience = 'Experience must be greater than 0';
    if (!formData.id_proof) newErrors.id_proof = 'ID proof is required';
    if (!formData.address_proof) newErrors.address_proof = 'Address proof is required';
    if (!formData.profile_photo) newErrors.profile_photo = 'Profile photo is required';
    if (!formData.terms_accepted) newErrors.terms_accepted = 'You must accept the terms and conditions';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Please fix the errors in the form');
      return;
    }
    
    setLoading(true);
    
    try {
      // Create FormData object for file uploads
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('email', formData.email);
      formDataToSend.append('phone', formData.phone);
      formDataToSend.append('pincode', formData.pincode);
      formDataToSend.append('service_category', formData.service_category);
      formDataToSend.append('experience', formData.experience.toString());
      if (formData.id_proof) formDataToSend.append('id_proof', formData.id_proof);
      if (formData.address_proof) formDataToSend.append('address_proof', formData.address_proof);
      if (formData.profile_photo) formDataToSend.append('profile_photo', formData.profile_photo);
      
      const response = await api.post(ENDPOINTS.VENDOR.APPLICATIONS, formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      toast.success('Vendor application submitted successfully! Our team will review it shortly.');
      navigate('/vendor/application-success');
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to submit application');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Vendor Application</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">
          Join our network of trusted service providers
        </p>
      </div>

      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name *</Label>
                <Input
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="John Doe"
                  required
                />
                {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="john@example.com"
                  required
                />
                {errors.email && <p className="text-sm text-destructive">{errors.email}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Mobile Number *</Label>
                <Input
                  id="phone"
                  name="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="+1 234 567 8900"
                  required
                />
                {errors.phone && <p className="text-sm text-destructive">{errors.phone}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="pincode">Pincode *</Label>
                <Input
                  id="pincode"
                  name="pincode"
                  value={formData.pincode}
                  onChange={handleInputChange}
                  placeholder="123456"
                  required
                />
                {errors.pincode && <p className="text-sm text-destructive">{errors.pincode}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="service_category">Service Category *</Label>
                <Select 
                  value={formData.service_category} 
                  onValueChange={(value) => handleSelectChange('service_category', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a service category" />
                  </SelectTrigger>
                  <SelectContent>
                    {serviceCategories.map((category) => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.service_category && <p className="text-sm text-destructive">{errors.service_category}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="experience">Years of Experience *</Label>
                <Input
                  id="experience"
                  name="experience"
                  type="number"
                  min="1"
                  value={formData.experience || ''}
                  onChange={handleInputChange}
                  placeholder="5"
                  required
                />
                {errors.experience && <p className="text-sm text-destructive">{errors.experience}</p>}
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-medium">Documents</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="id_proof">ID Proof *</Label>
                  <Input
                    id="id_proof"
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(e) => handleFileChange(e, 'id_proof')}
                  />
                  {errors.id_proof && <p className="text-sm text-destructive">{errors.id_proof}</p>}
                  <p className="text-xs text-muted-foreground">Upload Aadhar, Passport, or Driver's License</p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="address_proof">Address Proof *</Label>
                  <Input
                    id="address_proof"
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(e) => handleFileChange(e, 'address_proof')}
                  />
                  {errors.address_proof && <p className="text-sm text-destructive">{errors.address_proof}</p>}
                  <p className="text-xs text-muted-foreground">Utility bill, bank statement, or rental agreement</p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="profile_photo">Profile Photo *</Label>
                  <Input
                    id="profile_photo"
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleFileChange(e, 'profile_photo')}
                  />
                  {errors.profile_photo && <p className="text-sm text-destructive">{errors.profile_photo}</p>}
                  <p className="text-xs text-muted-foreground">Clear passport-sized photo</p>
                </div>
              </div>
            </div>

            <div className="flex items-start space-x-2">
              <Checkbox
                id="terms"
                checked={formData.terms_accepted}
                onCheckedChange={handleCheckboxChange}
              />
              <Label htmlFor="terms" className="text-sm">
                I agree to the <a href="#" className="text-primary hover:underline">Terms & Conditions</a> and <a href="#" className="text-primary hover:underline">Privacy Policy</a> *
              </Label>
            </div>
            {errors.terms_accepted && <p className="text-sm text-destructive">{errors.terms_accepted}</p>}

            <div className="flex gap-3">
              <Button type="submit" className="flex-1" disabled={loading}>
                {loading ? 'Submitting...' : 'Submit Application'}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate(-1)}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}