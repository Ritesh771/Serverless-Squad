import api from './api';
import { ENDPOINTS } from './endpoints';

export interface Address {
  id: string;
  label: string;
  address_line: string;
  pincode: string;
  lat?: string;
  lng?: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export const addressService = {
  // Get all addresses for current user
  async getAddresses(isDefault?: boolean): Promise<Address[]> {
    const params = isDefault !== undefined ? { is_default: isDefault } : {};
    const { data } = await api.get(ENDPOINTS.ADDRESSES.LIST, { params });
    return data.results || data;
  },

  // Get address by ID
  async getAddress(id: string): Promise<Address> {
    const { data } = await api.get(ENDPOINTS.ADDRESSES.DETAIL(id));
    return data;
  },

  // Create new address
  async createAddress(address: Omit<Address, 'id' | 'created_at' | 'updated_at'>): Promise<Address> {
    const { data } = await api.post(ENDPOINTS.ADDRESSES.CREATE, address);
    return data;
  },

  // Update address
  async updateAddress(id: string, updates: Partial<Address>): Promise<Address> {
    const { data } = await api.patch(ENDPOINTS.ADDRESSES.UPDATE(id), updates);
    return data;
  },

  // Delete address
  async deleteAddress(id: string): Promise<void> {
    await api.delete(ENDPOINTS.ADDRESSES.DELETE(id));
  },

  // Set default address
  async setDefaultAddress(id: string): Promise<{ message: string }> {
    const { data } = await api.post(ENDPOINTS.ADDRESSES.SET_DEFAULT(id));
    return data;
  },
};
