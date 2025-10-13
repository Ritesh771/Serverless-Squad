import api from './api';
import { ENDPOINTS } from './endpoints';

export interface DynamicPricing {
  service: {
    id: number;
    name: string;
    category: string;
  };
  pincode: string;
  pricing: {
    base_price: number;
    final_price: number;
    price_change_percent: number;
    factors: {
      demand: {
        level: string;
        multiplier: number;
        details: any;
      };
      supply: {
        level: string;
        multiplier: number;
        details: any;
      };
      time: {
        factors: string[];
        multiplier: number;
      };
      performance: {
        multiplier: number;
        details: any;
      };
    };
    total_multiplier: number;
  };
  timestamp: string;
}

export interface PricePrediction {
  service: {
    id: number;
    name: string;
    category: string;
    base_price: number;
  };
  pincode: string;
  predictions: Array<{
    date: string;
    day_of_week: string;
    prices: {
      morning: number;
      afternoon: number;
      evening: number;
    };
    avg_price: number;
    best_time: string;
  }>;
  timestamp: string;
}

export const pricingService = {
  // Get dynamic price for a service
  async getDynamicPrice(
    serviceId: number,
    pincode: string,
    scheduledDatetime?: string
  ): Promise<DynamicPricing> {
    const params: any = { service_id: serviceId, pincode };
    if (scheduledDatetime) {
      params.scheduled_datetime = scheduledDatetime;
    }

    const { data } = await api.get(ENDPOINTS.PRICING.GET, { params });
    return data;
  },

  // Get price predictions for multiple days
  async getPricePredictions(
    serviceId: number,
    pincode: string,
    days: number = 7
  ): Promise<PricePrediction> {
    const { data } = await api.post(ENDPOINTS.PRICING.PREDICT, {
      service_id: serviceId,
      pincode,
      days,
    });
    return data;
  },
};
