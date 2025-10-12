"""
Pincode Pulse Engine AI - Rule-based intelligent system for demand forecasting
and vendor optimization with hooks ready for ML enhancement
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from django.core.cache import cache
from decimal import Decimal

logger = logging.getLogger(__name__)


class PincodeAIEngine:
    """
    Intelligent Pincode Analysis Engine
    Currently rule-based with ML-ready architecture
    """
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes cache
        self.demand_thresholds = {
            'very_low': 0.5,
            'low': 1.0,
            'normal': 2.0,
            'high': 3.5,
            'very_high': 5.0,
            'extreme': 8.0
        }
    
    def analyze_pincode_pulse(self, pincode: str, analysis_period_days: int = 30) -> Dict:
        """
        Comprehensive pincode analysis with demand forecasting
        
        Args:
            pincode: Target pincode for analysis
            analysis_period_days: Historical data period for analysis
            
        Returns:
            Dict with pulse analysis including demand, supply, trends
        """
        cache_key = f"pincode_pulse_{pincode}_{analysis_period_days}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Import models here to avoid circular imports
            from django.apps import apps
            Booking = apps.get_model('core', 'Booking')
            User = apps.get_model('core', 'User')
            PincodeAnalytics = apps.get_model('core', 'PincodeAnalytics')
            VendorAvailability = apps.get_model('core', 'VendorAvailability')
            
            end_date = timezone.now()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            # Get historical data
            bookings = Booking.objects.filter(
                pincode=pincode,
                created_at__gte=start_date
            )
            
            vendors = User.objects.filter(
                role='vendor',
                pincode=pincode,
                is_active=True
            )
            
            # Calculate demand metrics
            demand_analysis = self._analyze_demand_patterns(bookings, analysis_period_days)
            
            # Calculate supply metrics
            supply_analysis = self._analyze_supply_capacity(vendors, pincode)
            
            # Trend analysis
            trend_analysis = self._analyze_trends(pincode, start_date, end_date)
            
            # Predictive insights
            predictions = self._generate_predictions(demand_analysis, supply_analysis, trend_analysis)
            
            # Recommendations
            recommendations = self._generate_recommendations(pincode, demand_analysis, supply_analysis)
            
            pulse_result = {
                'pincode': pincode,
                'analysis_period_days': analysis_period_days,
                'pulse_score': self._calculate_pulse_score(demand_analysis, supply_analysis),
                'demand_analysis': demand_analysis,
                'supply_analysis': supply_analysis,
                'trend_analysis': trend_analysis,
                'predictions': predictions,
                'recommendations': recommendations,
                'generated_at': timezone.now().isoformat()
            }
            
            # Cache result
            cache.set(cache_key, pulse_result, self.cache_timeout)
            
            logger.info(f"Pincode pulse analysis completed for {pincode}")
            return pulse_result
            
        except Exception as e:
            logger.error(f"Error analyzing pincode pulse for {pincode}: {str(e)}")
            return self._get_default_pulse_result(pincode)
    
    def _analyze_demand_patterns(self, bookings, period_days: int) -> Dict:
        """Analyze demand patterns from booking data"""
        total_bookings = bookings.count()
        completed_bookings = bookings.filter(status__in=['completed', 'signed']).count()
        pending_bookings = bookings.filter(status='pending').count()
        cancelled_bookings = bookings.filter(status='cancelled').count()
        
        # Daily average
        daily_avg = total_bookings / period_days if period_days > 0 else 0
        
        # Peak analysis (by hour)
        peak_hours = self._get_peak_hours(bookings)
        
        # Service type distribution
        service_distribution = self._get_service_distribution(bookings)
        
        # Completion rate
        completion_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        return {
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'pending_bookings': pending_bookings,
            'cancelled_bookings': cancelled_bookings,
            'daily_average': round(daily_avg, 2),
            'completion_rate': round(completion_rate, 2),
            'peak_hours': peak_hours,
            'service_distribution': service_distribution,
            'demand_level': self._classify_demand_level(daily_avg)
        }
    
    def _analyze_supply_capacity(self, vendors, pincode: str) -> Dict:
        """Analyze vendor supply capacity"""
        from django.apps import apps
        VendorAvailability = apps.get_model('core', 'VendorAvailability')
        
        total_vendors = vendors.count()
        available_vendors = vendors.filter(is_available=True).count()
        
        # Get vendor availability patterns
        availability_data = VendorAvailability.objects.filter(
            vendor__in=vendors,
            is_active=True
        )
        
        # Calculate average service radius
        avg_service_radius = availability_data.aggregate(
            avg_radius=Avg('service_radius_km')
        )['avg_radius'] or 25
        
        # Vendor utilization (simplified)
        utilization_rate = self._calculate_vendor_utilization(vendors)
        
        return {
            'total_vendors': total_vendors,
            'available_vendors': available_vendors,
            'availability_rate': round((available_vendors / total_vendors * 100) if total_vendors > 0 else 0, 2),
            'average_service_radius': round(avg_service_radius, 2),
            'utilization_rate': utilization_rate,
            'supply_level': self._classify_supply_level(available_vendors, total_vendors)
        }
    
    def _analyze_trends(self, pincode: str, start_date, end_date) -> Dict:
        """Analyze booking trends over time"""
        from django.apps import apps
        Booking = apps.get_model('core', 'Booking')
        
        # Week-over-week trend
        mid_date = start_date + (end_date - start_date) / 2
        
        first_half = Booking.objects.filter(
            pincode=pincode,
            created_at__gte=start_date,
            created_at__lt=mid_date
        ).count()
        
        second_half = Booking.objects.filter(
            pincode=pincode,
            created_at__gte=mid_date,
            created_at__lt=end_date
        ).count()
        
        # Calculate trend
        if first_half > 0:
            trend_percentage = ((second_half - first_half) / first_half) * 100
        else:
            trend_percentage = 100 if second_half > 0 else 0
        
        trend_direction = 'increasing' if trend_percentage > 5 else 'decreasing' if trend_percentage < -5 else 'stable'
        
        return {
            'trend_percentage': round(trend_percentage, 2),
            'trend_direction': trend_direction,
            'first_half_bookings': first_half,
            'second_half_bookings': second_half
        }
    
    def _generate_predictions(self, demand_analysis: Dict, supply_analysis: Dict, trend_analysis: Dict) -> Dict:
        """Generate demand and supply predictions"""
        current_demand = demand_analysis['daily_average']
        trend_multiplier = 1 + (trend_analysis['trend_percentage'] / 100)
        
        # Simple trend-based prediction
        next_week_demand = current_demand * trend_multiplier
        next_month_demand = current_demand * (trend_multiplier ** 4)  # Compound weekly
        
        # Supply-demand gap
        supply_demand_ratio = supply_analysis['available_vendors'] / max(current_demand, 1)
        
        return {
            'next_week_daily_demand': round(next_week_demand, 2),
            'next_month_daily_demand': round(next_month_demand, 2),
            'supply_demand_ratio': round(supply_demand_ratio, 2),
            'capacity_utilization_forecast': min(round(current_demand / supply_analysis['available_vendors'] * 100, 2) if supply_analysis['available_vendors'] > 0 else 100, 100),
            'recommended_vendor_count': max(1, round(next_month_demand * 1.2))  # 20% buffer
        }
    
    def _generate_recommendations(self, pincode: str, demand_analysis: Dict, supply_analysis: Dict) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        demand_level = demand_analysis['demand_level']
        supply_level = supply_analysis['supply_level']
        
        # High demand, low supply
        if demand_level in ['high', 'very_high', 'extreme'] and supply_level in ['very_low', 'low']:
            recommendations.append({
                'type': 'urgent',
                'category': 'vendor_recruitment',
                'title': 'Urgent Vendor Recruitment Needed',
                'description': f'Pincode {pincode} has {demand_level} demand but {supply_level} vendor availability',
                'action': 'Recruit 3-5 additional vendors immediately',
                'priority': 'high'
            })
        
        # Low completion rate
        if demand_analysis['completion_rate'] < 80:
            recommendations.append({
                'type': 'operational',
                'category': 'quality_improvement',
                'title': 'Improve Service Completion Rate',
                'description': f'Completion rate is {demand_analysis["completion_rate"]}%, below optimal 80%',
                'action': 'Review vendor performance and provide additional training',
                'priority': 'medium'
            })
        
        # Peak hour optimization
        if demand_analysis['peak_hours']:
            peak_hour = max(demand_analysis['peak_hours'], key=demand_analysis['peak_hours'].get)
            recommendations.append({
                'type': 'optimization',
                'category': 'scheduling',
                'title': 'Optimize Peak Hour Coverage',
                'description': f'Peak demand at {peak_hour}:00 with {demand_analysis["peak_hours"][peak_hour]} bookings',
                'action': 'Ensure maximum vendor availability during peak hours',
                'priority': 'low'
            })
        
        return recommendations
    
    def _calculate_pulse_score(self, demand_analysis: Dict, supply_analysis: Dict) -> int:
        """Calculate overall pulse score (0-100)"""
        # Base score from demand level
        demand_scores = {
            'very_low': 20, 'low': 40, 'normal': 70,
            'high': 85, 'very_high': 95, 'extreme': 100
        }
        
        supply_scores = {
            'very_low': 20, 'low': 40, 'normal': 70,
            'high': 85, 'very_high': 95, 'excellent': 100
        }
        
        demand_score = demand_scores.get(demand_analysis['demand_level'], 50)
        supply_score = supply_scores.get(supply_analysis['supply_level'], 50)
        
        # Weighted average (60% demand, 40% supply)
        pulse_score = (demand_score * 0.6) + (supply_score * 0.4)
        
        # Adjust for completion rate
        completion_adjustment = (demand_analysis['completion_rate'] - 80) / 2
        
        final_score = max(0, min(100, pulse_score + completion_adjustment))
        return round(final_score)
    
    def _get_peak_hours(self, bookings) -> Dict[int, int]:
        """Get peak booking hours"""
        peak_data = {}
        for booking in bookings:
            hour = booking.created_at.hour
            peak_data[hour] = peak_data.get(hour, 0) + 1
        return peak_data
    
    def _get_service_distribution(self, bookings) -> Dict[str, int]:
        """Get distribution of service types"""
        distribution = {}
        for booking in bookings:
            service_name = booking.service.name
            distribution[service_name] = distribution.get(service_name, 0) + 1
        return distribution
    
    def _classify_demand_level(self, daily_average: float) -> str:
        """Classify demand level based on daily average"""
        if daily_average >= self.demand_thresholds['extreme']:
            return 'extreme'
        elif daily_average >= self.demand_thresholds['very_high']:
            return 'very_high'
        elif daily_average >= self.demand_thresholds['high']:
            return 'high'
        elif daily_average >= self.demand_thresholds['normal']:
            return 'normal'
        elif daily_average >= self.demand_thresholds['low']:
            return 'low'
        elif daily_average >= self.demand_thresholds['very_low']:
            return 'very_low'
        else:
            return 'minimal'
    
    def _classify_supply_level(self, available_vendors: int, total_vendors: int) -> str:
        """Classify supply level based on vendor availability"""
        if available_vendors >= 15:
            return 'excellent'
        elif available_vendors >= 10:
            return 'very_high'
        elif available_vendors >= 6:
            return 'high'
        elif available_vendors >= 3:
            return 'normal'
        elif available_vendors >= 1:
            return 'low'
        else:
            return 'very_low'
    
    def _calculate_vendor_utilization(self, vendors) -> float:
        """Calculate vendor utilization rate (simplified)"""
        from django.apps import apps
        Booking = apps.get_model('core', 'Booking')
        
        total_capacity = vendors.count() * 8  # Assume 8 hours/day capacity
        if total_capacity == 0:
            return 0
        
        # Get recent bookings for these vendors
        recent_bookings = Booking.objects.filter(
            vendor__in=vendors,
            created_at__gte=timezone.now() - timedelta(days=7),
            status__in=['confirmed', 'in_progress', 'completed']
        ).count()
        
        utilization = (recent_bookings * 2) / total_capacity * 100  # Assume 2 hours per booking
        return min(round(utilization, 2), 100)
    
    def _get_default_pulse_result(self, pincode: str) -> Dict:
        """Return default result on error"""
        return {
            'pincode': pincode,
            'analysis_period_days': 30,
            'pulse_score': 50,
            'demand_analysis': {
                'total_bookings': 0,
                'daily_average': 0,
                'demand_level': 'unknown'
            },
            'supply_analysis': {
                'total_vendors': 0,
                'available_vendors': 0,
                'supply_level': 'unknown'
            },
            'trend_analysis': {
                'trend_direction': 'stable'
            },
            'predictions': {},
            'recommendations': [],
            'error': 'Analysis failed',
            'generated_at': timezone.now().isoformat()
        }


# Convenience function for easy access
def analyze_pincode_pulse(pincode: str, analysis_period_days: int = 30) -> Dict:
    """
    Easy-to-use function for pincode analysis
    
    Usage:
        from core.ai_services.pincode_ai import analyze_pincode_pulse
        result = analyze_pincode_pulse('400001')
    """
    engine = PincodeAIEngine()
    return engine.analyze_pincode_pulse(pincode, analysis_period_days)