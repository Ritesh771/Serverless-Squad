"""
Advanced Dynamic Pricing Service
Calculates real-time prices based on demand, supply density, and market conditions
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class DynamicPricingService:
    """
    Real-time dynamic pricing based on:
    1. Demand intensity (bookings vs vendors)
    2. Supply density (vendor availability)
    3. Time-based factors (peak hours, weekends)
    4. Historical performance (completion rates, satisfaction)
    """
    
    # Base multipliers
    BASE_MULTIPLIER = Decimal('1.0')
    
    # Demand-based multipliers
    DEMAND_MULTIPLIERS = {
        'very_low': Decimal('0.85'),    # < 1 booking per vendor - discount
        'low': Decimal('0.95'),          # 1-2 bookings per vendor
        'normal': Decimal('1.0'),        # 2-3 bookings per vendor
        'high': Decimal('1.15'),         # 3-5 bookings per vendor
        'very_high': Decimal('1.30'),    # 5-8 bookings per vendor
        'extreme': Decimal('1.50'),      # > 8 bookings per vendor
    }
    
    # Supply density multipliers
    SUPPLY_MULTIPLIERS = {
        'no_vendors': Decimal('2.0'),    # 0 vendors available - emergency pricing
        'very_low': Decimal('1.40'),     # 1 vendor available
        'low': Decimal('1.20'),          # 2-3 vendors available
        'normal': Decimal('1.0'),        # 4-6 vendors available
        'good': Decimal('0.90'),         # 7-10 vendors available
        'excellent': Decimal('0.85'),    # > 10 vendors available
    }
    
    # Time-based multipliers
    PEAK_HOUR_MULTIPLIER = Decimal('1.10')     # Peak hours (5 PM - 9 PM)
    WEEKEND_MULTIPLIER = Decimal('1.15')       # Saturday, Sunday
    LATE_NIGHT_MULTIPLIER = Decimal('1.25')    # 10 PM - 6 AM
    EARLY_MORNING_MULTIPLIER = Decimal('1.10') # 6 AM - 8 AM
    
    # Performance-based adjustments
    HIGH_SATISFACTION_DISCOUNT = Decimal('0.98')  # Area with >4.5 avg rating
    LOW_COMPLETION_SURCHARGE = Decimal('1.05')    # Area with <70% completion
    
    # Seasonal/promotional adjustments
    PROMOTIONAL_DISCOUNT = Decimal('0.90')  # Can be toggled for marketing campaigns
    
    @classmethod
    def calculate_dynamic_price(cls, service, pincode, scheduled_datetime=None):
        """
        Calculate dynamic price for a service in a specific pincode
        
        Args:
            service: Service object
            pincode: Customer pincode
            scheduled_datetime: When the service is scheduled (optional)
            
        Returns:
            dict with price breakdown and final price
        """
        try:
            # Start with base price
            base_price = Decimal(str(service.base_price))
            
            # Use current time if no scheduled time provided
            if not scheduled_datetime:
                scheduled_datetime = timezone.now()
            
            # Get real-time analytics
            demand_data = cls._get_demand_data(pincode)
            supply_data = cls._get_supply_data(pincode)
            time_factors = cls._get_time_factors(scheduled_datetime)
            performance_data = cls._get_performance_data(pincode)
            
            # Calculate multipliers
            demand_multiplier = cls._calculate_demand_multiplier(demand_data)
            supply_multiplier = cls._calculate_supply_multiplier(supply_data)
            time_multiplier = cls._calculate_time_multiplier(time_factors)
            performance_multiplier = cls._calculate_performance_multiplier(performance_data)
            
            # Apply multipliers
            final_price = base_price * demand_multiplier * supply_multiplier * time_multiplier * performance_multiplier
            
            # Round to 2 decimal places
            final_price = final_price.quantize(Decimal('0.01'))
            
            # Calculate percentage change
            price_change_percent = ((final_price - base_price) / base_price * 100).quantize(Decimal('0.1'))
            
            # Build breakdown
            breakdown = {
                'base_price': float(base_price),
                'final_price': float(final_price),
                'price_change_percent': float(price_change_percent),
                'factors': {
                    'demand': {
                        'level': demand_data['level'],
                        'multiplier': float(demand_multiplier),
                        'details': demand_data
                    },
                    'supply': {
                        'level': supply_data['level'],
                        'multiplier': float(supply_multiplier),
                        'details': supply_data
                    },
                    'time': {
                        'factors': time_factors,
                        'multiplier': float(time_multiplier)
                    },
                    'performance': {
                        'multiplier': float(performance_multiplier),
                        'details': performance_data
                    }
                },
                'total_multiplier': float(demand_multiplier * supply_multiplier * time_multiplier * performance_multiplier)
            }
            
            logger.info(f"Dynamic price calculated for {service.name} in {pincode}: ₹{base_price} -> ₹{final_price}")
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error calculating dynamic price: {str(e)}")
            # Return base price on error
            return {
                'base_price': float(service.base_price),
                'final_price': float(service.base_price),
                'price_change_percent': 0.0,
                'error': str(e)
            }
    
    @classmethod
    def _get_demand_data(cls, pincode):
        """Get real-time demand data for pincode"""
        from .models import PincodeAnalytics, Booking
        
        # Try to get from cache first
        cache_key = f"demand_data_{pincode}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Get today's analytics
        today = timezone.now().date()
        analytics = PincodeAnalytics.objects.filter(
            pincode=pincode,
            date=today
        ).first()
        
        if analytics:
            demand_ratio = analytics.demand_ratio
            total_bookings = analytics.total_bookings
            pending_bookings = analytics.pending_bookings
        else:
            # Calculate on the fly
            total_bookings = Booking.objects.filter(
                pincode=pincode,
                created_at__date=today
            ).count()
            
            pending_bookings = Booking.objects.filter(
                pincode=pincode,
                status='pending',
                created_at__date=today
            ).count()
            
            from .models import User
            available_vendors = User.objects.filter(
                role='vendor',
                pincode=pincode,
                is_available=True,
                is_active=True
            ).count()
            
            demand_ratio = total_bookings / available_vendors if available_vendors > 0 else float('inf')
        
        # Determine demand level
        if demand_ratio < 1:
            level = 'very_low'
        elif demand_ratio < 2:
            level = 'low'
        elif demand_ratio < 3:
            level = 'normal'
        elif demand_ratio < 5:
            level = 'high'
        elif demand_ratio < 8:
            level = 'very_high'
        else:
            level = 'extreme'
        
        data = {
            'level': level,
            'demand_ratio': round(demand_ratio, 2) if demand_ratio != float('inf') else 999,
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings
        }
        
        # Cache for 10 minutes
        cache.set(cache_key, data, 600)
        return data
    
    @classmethod
    def _get_supply_data(cls, pincode):
        """Get real-time supply/vendor availability data"""
        from .models import User, Booking
        
        # Try cache first
        cache_key = f"supply_data_{pincode}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Get available vendors in pincode
        available_vendors = User.objects.filter(
            role='vendor',
            pincode=pincode,
            is_available=True,
            is_active=True
        ).count()
        
        # Get vendors currently busy today
        today = timezone.now().date()
        busy_vendors = Booking.objects.filter(
            pincode=pincode,
            scheduled_date__date=today,
            status__in=['confirmed', 'in_progress'],
            vendor__isnull=False
        ).values('vendor').distinct().count()
        
        # Effective available vendors
        effective_vendors = max(0, available_vendors - busy_vendors)
        
        # Determine supply level
        if effective_vendors == 0:
            level = 'no_vendors'
        elif effective_vendors == 1:
            level = 'very_low'
        elif effective_vendors <= 3:
            level = 'low'
        elif effective_vendors <= 6:
            level = 'normal'
        elif effective_vendors <= 10:
            level = 'good'
        else:
            level = 'excellent'
        
        data = {
            'level': level,
            'available_vendors': available_vendors,
            'busy_vendors': busy_vendors,
            'effective_vendors': effective_vendors
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, data, 300)
        return data
    
    @classmethod
    def _get_time_factors(cls, scheduled_datetime):
        """Analyze time-based pricing factors"""
        hour = scheduled_datetime.hour
        is_weekend = scheduled_datetime.weekday() >= 5
        
        factors = []
        
        # Check peak hours (5 PM - 9 PM)
        if 17 <= hour <= 21:
            factors.append('peak_hour')
        
        # Check late night (10 PM - 6 AM)
        if hour >= 22 or hour < 6:
            factors.append('late_night')
        
        # Check early morning rush (6 AM - 8 AM)
        if 6 <= hour < 8:
            factors.append('early_morning')
        
        # Check weekend
        if is_weekend:
            factors.append('weekend')
        
        return factors
    
    @classmethod
    def _get_performance_data(cls, pincode):
        """Get historical performance data for area"""
        from .models import PincodeAnalytics, Signature
        
        # Try cache
        cache_key = f"performance_data_{pincode}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Get last 7 days analytics
        week_ago = timezone.now().date() - timedelta(days=7)
        analytics = PincodeAnalytics.objects.filter(
            pincode=pincode,
            date__gte=week_ago
        )
        
        if analytics.exists():
            # Calculate completion rate
            total_bookings = sum(a.total_bookings for a in analytics)
            completed_bookings = sum(a.completed_bookings for a in analytics)
            completion_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
            
            # Get average satisfaction
            avg_satisfaction = analytics.aggregate(
                avg_rating=Avg('customer_satisfaction_avg')
            )['avg_rating'] or 0
        else:
            completion_rate = 100  # Default to neutral
            avg_satisfaction = 3.5  # Default to neutral
        
        data = {
            'completion_rate': round(completion_rate, 2),
            'avg_satisfaction': round(avg_satisfaction, 2) if avg_satisfaction else 0,
            'has_data': analytics.exists()
        }
        
        # Cache for 1 hour
        cache.set(cache_key, data, 3600)
        return data
    
    @classmethod
    def _calculate_demand_multiplier(cls, demand_data):
        """Calculate multiplier based on demand level"""
        return cls.DEMAND_MULTIPLIERS.get(demand_data['level'], cls.BASE_MULTIPLIER)
    
    @classmethod
    def _calculate_supply_multiplier(cls, supply_data):
        """Calculate multiplier based on supply level"""
        return cls.SUPPLY_MULTIPLIERS.get(supply_data['level'], cls.BASE_MULTIPLIER)
    
    @classmethod
    def _calculate_time_multiplier(cls, time_factors):
        """Calculate multiplier based on time factors"""
        multiplier = cls.BASE_MULTIPLIER
        
        if 'peak_hour' in time_factors:
            multiplier *= cls.PEAK_HOUR_MULTIPLIER
        
        if 'weekend' in time_factors:
            multiplier *= cls.WEEKEND_MULTIPLIER
        
        if 'late_night' in time_factors:
            multiplier *= cls.LATE_NIGHT_MULTIPLIER
        
        if 'early_morning' in time_factors:
            multiplier *= cls.EARLY_MORNING_MULTIPLIER
        
        return multiplier
    
    @classmethod
    def _calculate_performance_multiplier(cls, performance_data):
        """Calculate multiplier based on area performance"""
        multiplier = cls.BASE_MULTIPLIER
        
        # Reward high satisfaction areas
        if performance_data['avg_satisfaction'] >= 4.5:
            multiplier *= cls.HIGH_SATISFACTION_DISCOUNT
        
        # Surcharge for low completion areas
        if performance_data['completion_rate'] < 70:
            multiplier *= cls.LOW_COMPLETION_SURCHARGE
        
        return multiplier
    
    @classmethod
    def get_price_prediction(cls, service, pincode, date_range_days=7):
        """
        Predict price trends for the next N days
        
        Args:
            service: Service object
            pincode: Customer pincode
            date_range_days: Number of days to predict
            
        Returns:
            list of daily price predictions
        """
        predictions = []
        base_date = timezone.now()
        
        for day_offset in range(date_range_days):
            prediction_date = base_date + timedelta(days=day_offset)
            
            # Get price for different times of day
            morning_price = cls.calculate_dynamic_price(
                service, pincode, 
                prediction_date.replace(hour=9, minute=0)
            )
            
            afternoon_price = cls.calculate_dynamic_price(
                service, pincode,
                prediction_date.replace(hour=14, minute=0)
            )
            
            evening_price = cls.calculate_dynamic_price(
                service, pincode,
                prediction_date.replace(hour=18, minute=0)
            )
            
            predictions.append({
                'date': prediction_date.date().isoformat(),
                'day_of_week': prediction_date.strftime('%A'),
                'prices': {
                    'morning': morning_price['final_price'],
                    'afternoon': afternoon_price['final_price'],
                    'evening': evening_price['final_price']
                },
                'avg_price': round((
                    morning_price['final_price'] + 
                    afternoon_price['final_price'] + 
                    evening_price['final_price']
                ) / 3, 2),
                'best_time': min([
                    ('morning', morning_price['final_price']),
                    ('afternoon', afternoon_price['final_price']),
                    ('evening', evening_price['final_price'])
                ], key=lambda x: x[1])[0]
            })
        
        return predictions
    
    @classmethod
    def clear_cache(cls, pincode=None):
        """Clear pricing cache for a pincode or all"""
        if pincode:
            cache.delete(f"demand_data_{pincode}")
            cache.delete(f"supply_data_{pincode}")
            cache.delete(f"performance_data_{pincode}")
        else:
            # Clear all pricing-related cache
            cache.delete_pattern("demand_data_*")
            cache.delete_pattern("supply_data_*")
            cache.delete_pattern("performance_data_*")
