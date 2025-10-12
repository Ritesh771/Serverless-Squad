import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Image, ZoomIn, ZoomOut, RotateCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Photo {
  id: string;
  image: string;
  image_type: 'before' | 'after' | 'additional';
  description: string;
  uploaded_at: string;
  uploaded_by: {
    id: string;
    name: string;
  };
}

interface PhotoReviewProps {
  photos: Photo[];
  onPhotoSelect?: (photo: Photo) => void;
}

export const PhotoReview = ({ photos, onPhotoSelect }: PhotoReviewProps) => {
  const [selectedPhoto, setSelectedPhoto] = useState<Photo | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [rotation, setRotation] = useState(0);

  // Group photos by type
  const beforePhotos = photos.filter(photo => photo.image_type === 'before');
  const afterPhotos = photos.filter(photo => photo.image_type === 'after');
  const additionalPhotos = photos.filter(photo => photo.image_type === 'additional');

  // Set first photo as selected by default
  useEffect(() => {
    if (photos.length > 0 && !selectedPhoto) {
      setSelectedPhoto(photos[0]);
    }
  }, [photos, selectedPhoto]);

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev + 0.2, 3));
  };

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev - 0.2, 0.5));
  };

  const handleRotate = () => {
    setRotation(prev => (prev + 90) % 360);
  };

  const resetView = () => {
    setZoomLevel(1);
    setRotation(0);
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'before':
        return <Badge variant="destructive">Before</Badge>;
      case 'after':
        return <Badge variant="success">After</Badge>;
      default:
        return <Badge variant="secondary">Additional</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <Card className="card-elevated">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Image className="h-5 w-5" />
            Service Photos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Photo gallery */}
            <div className="lg:col-span-1 space-y-4">
              <div>
                <h3 className="font-medium mb-2">Before Photos ({beforePhotos.length})</h3>
                <div className="grid grid-cols-2 gap-2">
                  {beforePhotos.map((photo) => (
                    <div 
                      key={photo.id}
                      className={`relative cursor-pointer rounded-lg overflow-hidden border-2 ${
                        selectedPhoto?.id === photo.id 
                          ? 'border-primary' 
                          : 'border-border hover:border-primary/50'
                      }`}
                      onClick={() => {
                        setSelectedPhoto(photo);
                        if (onPhotoSelect) onPhotoSelect(photo);
                      }}
                    >
                      <img 
                        src={photo.image} 
                        alt={photo.description || 'Before photo'}
                        className="w-full h-24 object-cover"
                      />
                      <div className="absolute top-1 left-1">
                        {getTypeBadge(photo.image_type)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-medium mb-2">After Photos ({afterPhotos.length})</h3>
                <div className="grid grid-cols-2 gap-2">
                  {afterPhotos.map((photo) => (
                    <div 
                      key={photo.id}
                      className={`relative cursor-pointer rounded-lg overflow-hidden border-2 ${
                        selectedPhoto?.id === photo.id 
                          ? 'border-primary' 
                          : 'border-border hover:border-primary/50'
                      }`}
                      onClick={() => {
                        setSelectedPhoto(photo);
                        if (onPhotoSelect) onPhotoSelect(photo);
                      }}
                    >
                      <img 
                        src={photo.image} 
                        alt={photo.description || 'After photo'}
                        className="w-full h-24 object-cover"
                      />
                      <div className="absolute top-1 left-1">
                        {getTypeBadge(photo.image_type)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {additionalPhotos.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Additional Photos ({additionalPhotos.length})</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {additionalPhotos.map((photo) => (
                      <div 
                        key={photo.id}
                        className={`relative cursor-pointer rounded-lg overflow-hidden border-2 ${
                          selectedPhoto?.id === photo.id 
                            ? 'border-primary' 
                            : 'border-border hover:border-primary/50'
                        }`}
                        onClick={() => {
                          setSelectedPhoto(photo);
                          if (onPhotoSelect) onPhotoSelect(photo);
                        }}
                      >
                        <img 
                          src={photo.image} 
                          alt={photo.description || 'Additional photo'}
                          className="w-full h-24 object-cover"
                        />
                        <div className="absolute top-1 left-1">
                          {getTypeBadge(photo.image_type)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Photo viewer */}
            <div className="lg:col-span-2">
              {selectedPhoto ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getTypeBadge(selectedPhoto.image_type)}
                      <span className="text-sm text-muted-foreground">
                        Uploaded by {selectedPhoto.uploaded_by.name}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={handleZoomOut}
                        disabled={zoomLevel <= 0.5}
                      >
                        <ZoomOut className="h-4 w-4" />
                      </Button>
                      <span className="text-sm">{Math.round(zoomLevel * 100)}%</span>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={handleZoomIn}
                        disabled={zoomLevel >= 3}
                      >
                        <ZoomIn className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={handleRotate}>
                        <RotateCw className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={resetView}>
                        Reset
                      </Button>
                    </div>
                  </div>
                  
                  <div className="relative bg-muted rounded-lg overflow-hidden flex items-center justify-center h-96">
                    <img
                      src={selectedPhoto.image}
                      alt={selectedPhoto.description || 'Selected photo'}
                      className="max-h-full max-w-full object-contain transition-transform duration-200"
                      style={{
                        transform: `scale(${zoomLevel}) rotate(${rotation}deg)`,
                        transformOrigin: 'center center'
                      }}
                    />
                  </div>
                  
                  {selectedPhoto.description && (
                    <p className="text-sm text-muted-foreground">
                      {selectedPhoto.description}
                    </p>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center h-96 bg-muted rounded-lg">
                  <p className="text-muted-foreground">Select a photo to view</p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Photo comparison slider (if both before and after photos exist) */}
      {beforePhotos.length > 0 && afterPhotos.length > 0 && (
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Before/After Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium mb-2">Before</h4>
                <img 
                  src={beforePhotos[0].image} 
                  alt="Before service" 
                  className="w-full h-64 object-cover rounded-lg"
                />
              </div>
              <div>
                <h4 className="font-medium mb-2">After</h4>
                <img 
                  src={afterPhotos[0].image} 
                  alt="After service" 
                  className="w-full h-64 object-cover rounded-lg"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};