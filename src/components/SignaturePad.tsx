import { useRef, useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';
import { Check, Loader2 } from 'lucide-react';

interface SignaturePadProps {
  onSave: (signature: string) => void;
  onClear?: () => void;
  bookingId?: string;
  isLocked?: boolean;
  initialSignature?: string;
}

export const SignaturePad = ({ onSave, onClear, bookingId, isLocked = false, initialSignature }: SignaturePadProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [signatureVerified, setSignatureVerified] = useState(false);
  const [signatureTimestamp, setSignatureTimestamp] = useState<string | null>(null);

  // Initialize canvas or load existing signature
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas dimensions
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Set drawing styles
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#000000';

    // If there's an initial signature, load it
    if (initialSignature && !isLocked) {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      };
      img.src = initialSignature;
    } else if (isLocked && initialSignature) {
      // Display locked signature
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        // Add lock overlay
        ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      };
      img.src = initialSignature;
    }
  }, [initialSignature, isLocked]);

  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    if (isLocked) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    setIsDrawing(true);
    
    const rect = canvas.getBoundingClientRect();
    let clientX, clientY;
    
    if ('touches' in e) {
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      clientX = e.clientX;
      clientY = e.clientY;
    }

    ctx.beginPath();
    ctx.moveTo(clientX - rect.left, clientY - rect.top);
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    if (!isDrawing || isLocked) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    let clientX, clientY;
    
    if ('touches' in e) {
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      clientX = e.clientX;
      clientY = e.clientY;
    }

    ctx.lineTo(clientX - rect.left, clientY - rect.top);
    ctx.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const clearSignature = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    onClear?.();
  };

  const saveSignature = async () => {
    const canvas = canvasRef.current;
    if (!canvas || isLocked) return;

    const dataUrl = canvas.toDataURL();
    
    // Hash the signature using SHA-256
    try {
      setIsSaving(true);
      
      // Send to backend for verification and storage
      const response = await api.post(ENDPOINTS.SIGNATURE.CREATE, {
        booking_id: bookingId,
        signature_data: dataUrl,
        // The backend will handle the hashing per security specifications
      });
      
      if (response.data.verified) {
        setSignatureVerified(true);
        setSignatureTimestamp(new Date().toISOString());
        toast.success('Signature verified and saved successfully!');
      }
      
      onSave(dataUrl);
    } catch (error) {
      toast.error('Failed to save signature');
      console.error('Signature save error:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // Verify an existing signature
  const verifySignature = async () => {
    if (!initialSignature || !bookingId) return;
    
    try {
      const response = await api.post(ENDPOINTS.SIGNATURE.VERIFY, {
        booking_id: bookingId,
        signature_data: initialSignature
      });
      
      if (response.data.verified) {
        setSignatureVerified(true);
        setSignatureTimestamp(response.data.timestamp);
        toast.success('Signature verified successfully!');
      } else {
        toast.error('Signature verification failed');
      }
    } catch (error) {
      toast.error('Failed to verify signature');
      console.error('Signature verification error:', error);
    }
  };

  // Format timestamp for display
  const formatTimestamp = (timestamp: string | null) => {
    if (!timestamp) return '';
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Card className="p-4 sm:p-6 space-y-4">
      <div>
        <h3 className="font-semibold mb-2">Sign Below</h3>
        <p className="text-sm text-muted-foreground">
          Please sign in the box below to confirm job completion
        </p>
      </div>

      <div className="relative">
        <canvas
          ref={canvasRef}
          className={`border-2 border-dashed border-border rounded-lg cursor-crosshair bg-white w-full ${
            isLocked ? 'cursor-not-allowed' : ''
          }`}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
        />
        
        {isLocked && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/80 rounded-lg">
            <div className="text-center p-4">
              <Check className="h-8 w-8 text-success mx-auto mb-2" />
              <p className="font-medium text-success">Signature Locked</p>
              <p className="text-xs text-muted-foreground mt-1">
                Submitted on {formatTimestamp(signatureTimestamp)}
              </p>
            </div>
          </div>
        )}
      </div>

      {!isLocked && (
        <div className="flex flex-col sm:flex-row gap-2 justify-end">
          <Button variant="outline" onClick={clearSignature} disabled={isSaving} className="w-full sm:w-auto">
            Clear
          </Button>
          <Button onClick={saveSignature} disabled={isSaving} className="w-full sm:w-auto">
            {isSaving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Signature'
            )}
          </Button>
        </div>
      )}

      {signatureVerified && (
        <div className="flex items-center gap-2 p-3 bg-success/10 rounded-lg border border-success/20">
          <Check className="h-5 w-5 text-success" />
          <div>
            <p className="text-sm font-medium text-success">Signature Verified</p>
            <p className="text-xs text-muted-foreground">
              Verified on {formatTimestamp(signatureTimestamp)}
            </p>
          </div>
        </div>
      )}
    </Card>
  );
};