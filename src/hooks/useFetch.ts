import { useState, useEffect } from 'react';
import axios, { AxiosRequestConfig } from 'axios';

interface UseFetchOptions<T> {
  url: string;
  config?: AxiosRequestConfig;
  skip?: boolean;
  mockData?: T; // For development with mock data
}

interface UseFetchResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useFetch<T = any>({ url, config, skip = false, mockData }: UseFetchOptions<T>): UseFetchResult<T> {
  const [data, setData] = useState<T | null>(mockData || null);
  const [loading, setLoading] = useState(!mockData);
  const [error, setError] = useState<Error | null>(null);
  const [refetchTrigger, setRefetchTrigger] = useState(0);

  useEffect(() => {
    if (skip) return;

    // If mock data is provided, use it instead of making API call
    if (mockData) {
      setData(mockData);
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await axios.get<T>(url, config);
        setData(response.data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url, skip, refetchTrigger]);

  const refetch = () => setRefetchTrigger(prev => prev + 1);

  return { data, loading, error, refetch };
}

export async function apiPost<T = any>(url: string, data: any, config?: AxiosRequestConfig): Promise<T> {
  const response = await axios.post<T>(url, data, config);
  return response.data;
}

export async function apiPut<T = any>(url: string, data: any, config?: AxiosRequestConfig): Promise<T> {
  const response = await axios.put<T>(url, data, config);
  return response.data;
}

export async function apiDelete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await axios.delete<T>(url, config);
  return response.data;
}
