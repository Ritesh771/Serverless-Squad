import api from './api';
import { ENDPOINTS } from './endpoints';

export interface Photo {
  id: number;
  booking: string;
  image: string;
  image_type: 'before' | 'after' | 'additional';
  description?: string;
  uploaded_by: number;
  uploaded_at: string;
}

export const photoService = {
  // Upload photo
  async uploadPhoto(
    bookingId: string,
    imageType: 'before' | 'after' | 'additional',
    file: File,
    description?: string
  ): Promise<Photo> {
    const formData = new FormData();
    formData.append('booking', bookingId);
    formData.append('image_type', imageType);
    formData.append('image', file);
    if (description) {
      formData.append('description', description);
    }

    const { data } = await api.post(ENDPOINTS.PHOTOS.UPLOAD, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  // Get photos for a booking
  async getPhotos(bookingId: string): Promise<Photo[]> {
    const { data } = await api.get(ENDPOINTS.PHOTOS.LIST, {
      params: { booking: bookingId },
    });
    return data.results || data;
  },

  // Delete photo
  async deletePhoto(photoId: number): Promise<void> {
    await api.delete(ENDPOINTS.PHOTOS.DELETE(photoId));
  },
};
