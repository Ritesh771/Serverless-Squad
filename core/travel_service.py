"""
Google Maps Travel Time Service with intelligent caching
"""
import requests
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from typing import Dict, Optional, Tuple
from .models import TravelTimeCache

logger = logging.getLogger(__name__)


class GoogleMapsService:
    """Service for calculating travel times using Google Maps API with caching"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
        self.base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        
    def get_travel_time(self, from_pincode: str, to_pincode: str, departure_time: Optional[timezone.datetime] = None) -> Dict:
        """
        Get travel time between two pincodes with intelligent caching
        
        Returns:
            {
                'distance_km': float,
                'duration_minutes': int,
                'duration_in_traffic_minutes': int,
                'source': 'cache|api|estimated'
            }
        """
        # First check cache
        cached_result = self._get_from_cache(from_pincode, to_pincode)
        if cached_result:
            logger.info(f"Using cached travel time: {from_pincode} → {to_pincode}")
            return {
                'distance_km': cached_result.distance_km,
                'duration_minutes': cached_result.duration_minutes,
                'duration_in_traffic_minutes': cached_result.duration_in_traffic_minutes or cached_result.duration_minutes,
                'source': 'cache'
            }
        
        # Try Google Maps API if API key is available
        if self.api_key:
            try:
                api_result = self._call_google_maps_api(from_pincode, to_pincode, departure_time)
                if api_result:
                    # Cache the result
                    self._save_to_cache(from_pincode, to_pincode, api_result)
                    logger.info(f"Used Google Maps API: {from_pincode} → {to_pincode}")
                    return {**api_result, 'source': 'api'}
            except Exception as e:
                logger.error(f"Google Maps API failed: {e}")
        
        # Fallback to estimated travel time
        estimated_result = self._estimate_travel_time(from_pincode, to_pincode)
        logger.info(f"Using estimated travel time: {from_pincode} → {to_pincode}")
        
        # Cache the estimated result with lower confidence
        estimated_result['confidence_score'] = 0.5
        self._save_to_cache(from_pincode, to_pincode, estimated_result, api_used=False)
        
        return {**estimated_result, 'source': 'estimated'}
    
    def _get_from_cache(self, from_pincode: str, to_pincode: str) -> Optional[TravelTimeCache]:
        """Get travel time from cache if available and not expired"""
        try:
            cached = TravelTimeCache.objects.get(
                from_pincode=from_pincode,
                to_pincode=to_pincode,
                is_expired=False
            )
            
            # Check if cache is older than 24 hours
            if (timezone.now() - cached.calculated_at).days >= 1:
                cached.is_expired = True
                cached.save()
                return None
                
            return cached
        except TravelTimeCache.DoesNotExist:
            return None
    
    def _call_google_maps_api(self, from_pincode: str, to_pincode: str, departure_time: Optional[timezone.datetime] = None) -> Optional[Dict]:
        """Call Google Maps Distance Matrix API"""
        params = {
            'origins': from_pincode,
            'destinations': to_pincode,
            'units': 'metric',
            'key': self.api_key,
            'mode': 'driving',
            'traffic_model': 'best_guess'
        }
        
        # Add departure time for traffic-aware routing
        if departure_time:
            params['departure_time'] = int(departure_time.timestamp())
        else:
            params['departure_time'] = 'now'
        
        response = requests.get(self.base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] != 'OK':
            raise Exception(f"Google Maps API error: {data['status']}")
        
        row = data['rows'][0]
        if row['elements'][0]['status'] != 'OK':
            raise Exception(f"Route not found: {row['elements'][0]['status']}")
        
        element = row['elements'][0]
        
        # Extract distance and duration
        distance_m = element['distance']['value']
        distance_km = distance_m / 1000
        
        duration_s = element['duration']['value']
        duration_minutes = max(1, int(duration_s / 60))  # Minimum 1 minute
        
        # Duration in traffic (if available)
        duration_in_traffic_minutes = duration_minutes
        if 'duration_in_traffic' in element:
            duration_in_traffic_s = element['duration_in_traffic']['value']
            duration_in_traffic_minutes = max(1, int(duration_in_traffic_s / 60))
        
        return {
            'distance_km': round(distance_km, 2),
            'duration_minutes': duration_minutes,
            'duration_in_traffic_minutes': duration_in_traffic_minutes,
            'confidence_score': 1.0
        }
    
    def _estimate_travel_time(self, from_pincode: str, to_pincode: str) -> Dict:
        """
        Estimate travel time based on pincode distance and average speeds
        This is a fallback when Google Maps API is not available
        """
        # Simple estimation based on pincode numerical difference
        # This is a rough approximation - in production, you'd want a more sophisticated model
        
        try:
            from_num = int(from_pincode[:3])  # First 3 digits
            to_num = int(to_pincode[:3])
            
            # Rough distance estimation (very basic)
            pincode_diff = abs(from_num - to_num)
            
            if pincode_diff == 0:
                # Same area
                distance_km = 5.0
                duration_minutes = 15
            elif pincode_diff <= 10:
                # Nearby areas
                distance_km = 15.0
                duration_minutes = 30
            elif pincode_diff <= 50:
                # Medium distance
                distance_km = 35.0
                duration_minutes = 60
            else:
                # Far distance
                distance_km = 75.0
                duration_minutes = 120
            
        except (ValueError, IndexError):
            # Default fallback if pincode format is unexpected
            distance_km = 25.0
            duration_minutes = 45
        
        return {
            'distance_km': distance_km,
            'duration_minutes': duration_minutes,
            'duration_in_traffic_minutes': int(duration_minutes * 1.3),  # Add 30% for traffic
            'confidence_score': 0.5
        }
    
    def _save_to_cache(self, from_pincode: str, to_pincode: str, result: Dict, api_used: bool = True):
        """Save travel time result to cache"""
        try:
            TravelTimeCache.objects.update_or_create(
                from_pincode=from_pincode,
                to_pincode=to_pincode,
                defaults={
                    'distance_km': result['distance_km'],
                    'duration_minutes': result['duration_minutes'],
                    'duration_in_traffic_minutes': result.get('duration_in_traffic_minutes'),
                    'google_maps_api_used': api_used,
                    'confidence_score': result.get('confidence_score', 1.0),
                    'is_expired': False,
                    'calculated_at': timezone.now()
                }
            )
        except Exception as e:
            logger.error(f"Failed to save travel time to cache: {e}")
    
    def clear_expired_cache(self):
        """Clean up expired cache entries"""
        expired_count = TravelTimeCache.objects.filter(
            calculated_at__lt=timezone.now() - timedelta(days=7)
        ).delete()[0]
        
        logger.info(f"Cleared {expired_count} expired travel time cache entries")
        return expired_count
    
    def warm_up_cache(self, pincodes: list):
        """Pre-populate cache for common pincode combinations"""
        if not self.api_key:
            logger.warning("Cannot warm up cache without Google Maps API key")
            return
        
        total_combinations = len(pincodes) * (len(pincodes) - 1)
        processed = 0
        
        logger.info(f"Warming up travel time cache for {total_combinations} combinations")
        
        for from_pincode in pincodes:
            for to_pincode in pincodes:
                if from_pincode != to_pincode:
                    # Check if already cached
                    if not self._get_from_cache(from_pincode, to_pincode):
                        self.get_travel_time(from_pincode, to_pincode)
                        processed += 1
                        
                        # Add small delay to avoid rate limiting
                        if processed % 10 == 0:
                            import time
                            time.sleep(1)
        
        logger.info(f"Cache warm-up completed. Processed {processed} new combinations")


# Singleton instance
travel_service = GoogleMapsService()