import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { PhotoUpload } from '@/components/PhotoUpload';
import { toast } from 'sonner';

export default function VendorProfile() {
  const { user } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [phone, setPhone] = useState('');
  const [skills, setSkills] = useState('Plumbing, Leak Repair, Installation');
  const [experience, setExperience] = useState('5 years');
  const [bio, setBio] = useState('');
  const [documents, setDocuments] = useState<File[]>([]);

  const handleSave = () => {
    // TODO: Connect to backend API
    toast.success('Profile updated successfully!');
  };

  const handleDocumentUpload = (files: File[]) => {
    setDocuments(files);
    toast.success('Documents uploaded successfully!');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">My Profile</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage your vendor information</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Avatar & Stats */}
        <Card className="card-elevated">
          <CardContent className="pt-6 flex flex-col items-center">
            <Avatar className="h-24 w-24 mb-4">
              <AvatarFallback className="text-2xl bg-primary text-primary-foreground">
                {user?.name.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <h3 className="font-semibold text-lg">{user?.name}</h3>
            <p className="text-sm text-muted-foreground capitalize">{user?.role}</p>
            
            <Separator className="my-4 w-full" />
            
            <div className="w-full space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Rating</span>
                <Badge variant="secondary">4.9/5.0</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Jobs Completed</span>
                <Badge variant="secondary">127</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Verified</span>
                <Badge className="bg-success text-success-foreground">Yes</Badge>
              </div>
            </div>

            <Button variant="outline" size="sm" className="mt-4 w-full">
              Change Photo
            </Button>
          </CardContent>
        </Card>

        {/* Profile Form */}
        <Card className="lg:col-span-2 card-elevated">
          <CardHeader>
            <CardTitle>Vendor Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="+1 234 567 8900"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="experience">Experience</Label>
                <Input
                  id="experience"
                  placeholder="5 years"
                  value={experience}
                  onChange={(e) => setExperience(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="skills">Skills & Services</Label>
              <Input
                id="skills"
                placeholder="Plumbing, Leak Repair, Installation"
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="bio">Professional Bio</Label>
              <Textarea
                id="bio"
                placeholder="Tell customers about your experience..."
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={4}
              />
            </div>

            <Separator />

            <div className="flex justify-end gap-3">
              <Button variant="outline">Cancel</Button>
              <Button onClick={handleSave}>Save Changes</Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Documents Section */}
      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Certifications & Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <PhotoUpload
            onUpload={handleDocumentUpload}
            title="Upload Documents"
            description="Upload licenses, certifications, and insurance documents"
          />
          
          {documents.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-medium mb-2">Uploaded Documents:</p>
              <div className="space-y-2">
                {documents.map((doc, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border border-border rounded-lg">
                    <span className="text-sm">{doc.name}</span>
                    <Badge variant="secondary">Pending Review</Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

