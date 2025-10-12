from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q, F
from django.core.cache import cache
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import logging
import json

logger = logging.getLogger(__name__)


class AdvancedVendorBonusService:
    """
    Advanced ML-based vendor bonus calculation with performance analytics
    Currently rule-based with ML-ready architecture
    """
    
    @staticmethod
    def calculate_performance_bonuses(vendor, period_days: int = 30) -> Dict:
        """
        Advanced bonus calculation with ML-based performance analysis
        
        Args:
            vendor: Vendor user object
            period_days: Analysis period in days
            
        Returns:
            Dict with bonus analysis and recommendations
        """
        try:
            # Get performance data
            performance_data = AdvancedVendorBonusService._get_vendor_performance_data(vendor, period_days)
            
            # ML-based performance scoring
            performance_score = AdvancedVendorBonusService._calculate_ml_performance_score(performance_data)
            
            # Calculate bonuses based on performance
            bonus_calculations = AdvancedVendorBonusService._calculate_advanced_bonuses(vendor, performance_data, performance_score)
            
            # Predictive insights
            predictions = AdvancedVendorBonusService._generate_performance_predictions(performance_data, performance_score)
            
            # Recommendations
            recommendations = AdvancedVendorBonusService._generate_bonus_recommendations(vendor, performance_data, bonus_calculations)
            
            result = {
                'vendor_id': vendor.id,
                'vendor_name': vendor.get_full_name(),
                'analysis_period_days': period_days,
                'performance_data': performance_data,
                'performance_score': performance_score,
                'bonus_calculations': bonus_calculations,
                'predictions': predictions,
                'recommendations': recommendations,
                'total_bonus_amount': bonus_calculations.get('total_bonus', 0),
                'analysis_timestamp': timezone.now().isoformat()
            }
            
            logger.info(f"Advanced bonus calculation completed for vendor {vendor.id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate advanced bonuses for vendor {vendor.id}: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def _get_vendor_performance_data(vendor, period_days: int) -> Dict:
        """Get comprehensive performance data for analysis"""
        from django.apps import apps
        Booking = apps.get_model('core', 'Booking')
        Signature = apps.get_model('core', 'Signature')
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Get bookings
        bookings = Booking.objects.filter(
            vendor=vendor,
            created_at__gte=start_date
        )
        
        completed_bookings = bookings.filter(status__in=['completed', 'signed'])
        
        # Calculate metrics
        total_bookings = bookings.count()
        total_completed = completed_bookings.count()
        total_cancelled = bookings.filter(status='cancelled').count()
        total_disputed = bookings.filter(status='disputed').count()
        
        # Revenue metrics
        total_revenue = completed_bookings.aggregate(total=Sum('total_price'))['total'] or Decimal('0')
        avg_booking_value = completed_bookings.aggregate(avg=Avg('total_price'))['avg'] or Decimal('0')
        
        # Signature metrics
        signatures = Signature.objects.filter(
            booking__in=completed_bookings,
            status='signed'
        )
        
        signature_count = signatures.count()
        avg_satisfaction = signatures.aggregate(avg=Avg('satisfaction_rating'))['avg'] or 0
        
        # Response time analysis
        response_times = []
        for booking in bookings.filter(vendor__isnull=False):
            if booking.scheduled_date and booking.created_at:
                response_time = (booking.scheduled_date - booking.created_at).total_seconds() / 3600
                if 0 < response_time < 168:  # Valid response time (1 week max)
                    response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 24
        
        # Service type distribution
        service_distribution = {}
        for booking in completed_bookings:
            service_name = booking.service.name
            service_distribution[service_name] = service_distribution.get(service_name, 0) + 1
        
        # Time-based patterns
        hourly_distribution = {}
        for booking in bookings:
            hour = booking.created_at.hour
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
        
        return {
            'total_bookings': total_bookings,
            'completed_bookings': total_completed,
            'cancelled_bookings': total_cancelled,
            'disputed_bookings': total_disputed,
            'completion_rate': (total_completed / total_bookings * 100) if total_bookings > 0 else 0,
            'cancellation_rate': (total_cancelled / total_bookings * 100) if total_bookings > 0 else 0,
            'dispute_rate': (total_disputed / total_bookings * 100) if total_bookings > 0 else 0,
            'total_revenue': float(total_revenue),
            'avg_booking_value': float(avg_booking_value),
            'signature_count': signature_count,
            'signature_rate': (signature_count / total_completed * 100) if total_completed > 0 else 0,
            'avg_satisfaction': round(float(avg_satisfaction), 2),
            'avg_response_time_hours': round(avg_response_time, 2),
            'service_distribution': service_distribution,
            'hourly_distribution': hourly_distribution,
            'revenue_per_day': float(total_revenue) / period_days if period_days > 0 else 0
        }
    
    @staticmethod
    def _calculate_ml_performance_score(performance_data: Dict) -> Dict:
        """Calculate ML-based performance score (rule-based implementation ready for ML)"""
        scores = {}
        weights = {
            'completion_rate': 0.25,
            'satisfaction_score': 0.20,
            'signature_rate': 0.15,
            'response_time': 0.15,
            'revenue_consistency': 0.10,
            'dispute_handling': 0.10,
            'service_diversity': 0.05
        }
        
        # Completion rate score (0-100)
        completion_rate = performance_data['completion_rate']
        scores['completion_rate'] = min(100, completion_rate * 1.1)  # Slight bonus for high completion
        
        # Satisfaction score (0-100)
        satisfaction = performance_data['avg_satisfaction']
        scores['satisfaction_score'] = (satisfaction / 5.0) * 100 if satisfaction > 0 else 50
        
        # Signature rate score (0-100)
        signature_rate = performance_data['signature_rate']
        scores['signature_rate'] = min(100, signature_rate * 1.05)  # Slight bonus
        
        # Response time score (0-100, lower is better)
        response_time = performance_data['avg_response_time_hours']
        if response_time <= 1:
            scores['response_time'] = 100
        elif response_time <= 4:
            scores['response_time'] = 90 - (response_time - 1) * 10
        elif response_time <= 12:
            scores['response_time'] = 60 - (response_time - 4) * 5
        else:
            scores['response_time'] = max(20, 60 - response_time)
        
        # Revenue consistency score
        if performance_data['total_bookings'] > 5:
            scores['revenue_consistency'] = min(100, 70 + (performance_data['total_bookings'] - 5) * 3)
        else:
            scores['revenue_consistency'] = 40
        
        # Dispute handling score (inverse of dispute rate)
        dispute_rate = performance_data['dispute_rate']
        scores['dispute_handling'] = max(0, 100 - dispute_rate * 10)
        
        # Service diversity score
        service_count = len(performance_data['service_distribution'])
        scores['service_diversity'] = min(100, service_count * 25)
        
        # Calculate weighted overall score
        overall_score = sum(scores[metric] * weights[metric] for metric in scores)
        
        # Performance tier
        if overall_score >= 90:
            tier = 'exceptional'
        elif overall_score >= 80:
            tier = 'excellent'
        elif overall_score >= 70:
            tier = 'good'
        elif overall_score >= 60:
            tier = 'satisfactory'
        else:
            tier = 'needs_improvement'
        
        return {
            'individual_scores': scores,
            'weights': weights,
            'overall_score': round(overall_score, 2),
            'performance_tier': tier,
            'tier_description': AdvancedVendorBonusService._get_tier_description(tier)
        }
    
    @staticmethod
    def _calculate_advanced_bonuses(vendor, performance_data: Dict, performance_score: Dict) -> Dict:
        """Calculate bonuses based on advanced performance analysis"""
        bonuses = {
            'performance_bonus': 0,
            'efficiency_bonus': 0,
            'customer_satisfaction_bonus': 0,
            'consistency_bonus': 0,
            'special_achievement_bonus': 0,
            'total_bonus': 0
        }
        
        base_revenue = performance_data['total_revenue']
        overall_score = performance_score['overall_score']
        
        # Performance bonus based on overall score
        if overall_score >= 90:
            bonuses['performance_bonus'] = base_revenue * 0.15  # 15% bonus
        elif overall_score >= 80:
            bonuses['performance_bonus'] = base_revenue * 0.10  # 10% bonus
        elif overall_score >= 70:
            bonuses['performance_bonus'] = base_revenue * 0.05  # 5% bonus
        
        # Efficiency bonus (quick response + high completion)
        if (performance_data['avg_response_time_hours'] <= 2 and 
            performance_data['completion_rate'] >= 95):
            bonuses['efficiency_bonus'] = base_revenue * 0.08
        
        # Customer satisfaction bonus
        if performance_data['avg_satisfaction'] >= 4.8:
            bonuses['customer_satisfaction_bonus'] = base_revenue * 0.10
        elif performance_data['avg_satisfaction'] >= 4.5:
            bonuses['customer_satisfaction_bonus'] = base_revenue * 0.06
        
        # Consistency bonus (high booking volume + low dispute rate)
        if (performance_data['total_bookings'] >= 20 and 
            performance_data['dispute_rate'] <= 2):
            bonuses['consistency_bonus'] = base_revenue * 0.05
        
        # Special achievement bonuses
        achievements = []
        if performance_data['signature_rate'] >= 98:
            achievements.append('signature_master')
            bonuses['special_achievement_bonus'] += base_revenue * 0.03
        
        if performance_data['total_bookings'] >= 50:
            achievements.append('volume_leader')
            bonuses['special_achievement_bonus'] += base_revenue * 0.02
        
        if performance_data['avg_satisfaction'] >= 4.9:
            achievements.append('customer_champion')
            bonuses['special_achievement_bonus'] += base_revenue * 0.03
        
        # Calculate total bonus
        bonuses['total_bonus'] = sum(bonuses.values()) - bonuses['total_bonus']  # Exclude total from sum
        
        # Cap total bonus at 25% of revenue
        max_bonus = base_revenue * 0.25
        if bonuses['total_bonus'] > max_bonus:
            bonuses['total_bonus'] = max_bonus
            bonuses['capped'] = True
        
        bonuses['achievements'] = achievements
        bonuses['base_revenue'] = base_revenue
        
        return bonuses
    
    @staticmethod
    def _generate_performance_predictions(performance_data: Dict, performance_score: Dict) -> Dict:
        """Generate performance predictions and trends"""
        current_score = performance_score['overall_score']
        
        # Simple trend analysis based on current performance
        if current_score >= 85:
            trend = 'improving'
            next_month_score = min(100, current_score + 2)
        elif current_score >= 70:
            trend = 'stable'
            next_month_score = current_score
        else:
            trend = 'declining'
            next_month_score = max(40, current_score - 3)
        
        # Revenue prediction
        current_daily_revenue = performance_data['revenue_per_day']
        if trend == 'improving':
            predicted_daily_revenue = current_daily_revenue * 1.1
        elif trend == 'stable':
            predicted_daily_revenue = current_daily_revenue
        else:
            predicted_daily_revenue = current_daily_revenue * 0.9
        
        return {
            'performance_trend': trend,
            'predicted_next_month_score': round(next_month_score, 2),
            'current_daily_revenue': round(current_daily_revenue, 2),
            'predicted_daily_revenue': round(predicted_daily_revenue, 2),
            'revenue_change_percentage': round(((predicted_daily_revenue - current_daily_revenue) / current_daily_revenue * 100) if current_daily_revenue > 0 else 0, 2),
            'growth_potential': 'high' if current_score < 80 else 'moderate' if current_score < 90 else 'optimized'
        }
    
    @staticmethod
    def _generate_bonus_recommendations(vendor, performance_data: Dict, bonus_calculations: Dict) -> List[Dict]:
        """Generate actionable recommendations for bonus optimization"""
        recommendations = []
        
        # Low completion rate
        if performance_data['completion_rate'] < 90:
            recommendations.append({
                'type': 'improvement',
                'category': 'completion_rate',
                'title': 'Improve Completion Rate',
                'description': f'Current completion rate: {performance_data["completion_rate"]:.1f}%',
                'action': 'Focus on accepting only bookings you can complete. Target: 95%+',
                'potential_bonus_increase': performance_data['total_revenue'] * 0.05,
                'priority': 'high'
            })
        
        # Low customer satisfaction
        if performance_data['avg_satisfaction'] < 4.5:
            recommendations.append({
                'type': 'improvement',
                'category': 'customer_satisfaction',
                'title': 'Enhance Customer Satisfaction',
                'description': f'Current avg rating: {performance_data["avg_satisfaction"]:.1f}/5',
                'action': 'Focus on service quality, communication, and professionalism',
                'potential_bonus_increase': performance_data['total_revenue'] * 0.06,
                'priority': 'high'
            })
        
        # Slow response time
        if performance_data['avg_response_time_hours'] > 4:
            recommendations.append({
                'type': 'improvement',
                'category': 'response_time',
                'title': 'Faster Response Time',
                'description': f'Current avg response: {performance_data["avg_response_time_hours"]:.1f} hours',
                'action': 'Respond to bookings within 2 hours for efficiency bonus',
                'potential_bonus_increase': performance_data['total_revenue'] * 0.08,
                'priority': 'medium'
            })
        
        # High dispute rate
        if performance_data['dispute_rate'] > 5:
            recommendations.append({
                'type': 'critical',
                'category': 'dispute_resolution',
                'title': 'Reduce Dispute Rate',
                'description': f'Current dispute rate: {performance_data["dispute_rate"]:.1f}%',
                'action': 'Review service quality and customer communication practices',
                'potential_bonus_increase': 0,
                'priority': 'critical'
            })
        
        # Bonus optimization opportunities
        if bonus_calculations['total_bonus'] < performance_data['total_revenue'] * 0.15:
            recommendations.append({
                'type': 'optimization',
                'category': 'bonus_maximization',
                'title': 'Maximize Bonus Potential',
                'description': f'Current bonus: ₹{bonus_calculations["total_bonus"]:.0f}',
                'action': 'Focus on achieving 90+ overall performance score',
                'potential_bonus_increase': performance_data['total_revenue'] * 0.15 - bonus_calculations['total_bonus'],
                'priority': 'medium'
            })
        
        return recommendations
    
    @staticmethod
    def _get_tier_description(tier: str) -> str:
        """Get description for performance tier"""
        descriptions = {
            'exceptional': 'Outstanding performance across all metrics. Eligible for maximum bonuses.',
            'excellent': 'High performance with minor areas for improvement. Strong bonus eligibility.',
            'good': 'Solid performance meeting most targets. Moderate bonus eligibility.',
            'satisfactory': 'Acceptable performance with room for improvement. Limited bonus eligibility.',
            'needs_improvement': 'Performance below standards. Focus on improvement required.'
        }
        return descriptions.get(tier, 'Performance tier not recognized')


class VendorBonusService:
    """Service for calculating and managing vendor performance bonuses"""
    
    # Bonus configuration
    PERFORMANCE_THRESHOLDS = {
        'completion_rate': {
            'excellent': {'threshold': 95, 'bonus_percentage': 15},
            'good': {'threshold': 90, 'bonus_percentage': 10},
            'satisfactory': {'threshold': 85, 'bonus_percentage': 5}
        },
        'satisfaction_score': {
            'excellent': {'threshold': 4.8, 'bonus_percentage': 12},
            'good': {'threshold': 4.5, 'bonus_percentage': 8},
            'satisfactory': {'threshold': 4.0, 'bonus_percentage': 4}
        },
        'signature_rate': {
            'excellent': {'threshold': 95, 'bonus_percentage': 10},
            'good': {'threshold': 90, 'bonus_percentage': 6},
            'satisfactory': {'threshold': 85, 'bonus_percentage': 3}
        }
    }
    
    SURGE_MULTIPLIERS = {
        'high_demand': Decimal('1.20'),    # 20% bonus for high demand areas
        'very_high_demand': Decimal('1.30'), # 30% bonus for very high demand
        'critical_demand': Decimal('1.50')   # 50% bonus for critical demand
    }
    
    @classmethod
    def calculate_monthly_bonuses(cls, vendor, year, month):
        """Calculate all bonuses for a vendor for a specific month"""
        from .models import Booking, Signature, VendorBonus
        
        try:
            # Define period
            period_start = datetime(year, month, 1).date()
            if month == 12:
                period_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                period_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
            # Get vendor bookings for the period
            bookings = Booking.objects.filter(
                vendor=vendor,
                completion_date_date_range=[period_start, period_end],
                status__in=['completed', 'signed']
            )
            
            if not bookings.exists():
                logger.info(f"No completed bookings for vendor {vendor.id} in {year}-{month}")
                return []
            
            # Calculate performance metrics
            metrics = cls._calculate_performance_metrics(vendor, bookings)
            
            # Calculate different types of bonuses
            bonuses = []
            
            # 1. Performance-based bonuses
            performance_bonuses = cls._calculate_performance_bonuses(vendor, metrics, period_start, period_end)
            bonuses.extend(performance_bonuses)
            
            # 2. Surge pricing bonuses (calculated per booking)
            surge_bonuses = cls._calculate_surge_bonuses(vendor, bookings, period_start, period_end)
            bonuses.extend(surge_bonuses)
            
            # 3. Monthly incentive bonus
            monthly_bonus = cls._calculate_monthly_incentive(vendor, metrics, period_start, period_end)
            if monthly_bonus:
                bonuses.append(monthly_bonus)
            
            # Save all calculated bonuses
            saved_bonuses = []
            for bonus_data in bonuses:
                bonus = VendorBonus.objects.create(**bonus_data)
                saved_bonuses.append(bonus)
                logger.info(f"Created bonus: {bonus.bonus_type} - ₹{bonus.amount} for vendor {vendor.id}")
            
            return saved_bonuses
            
        except Exception as e:
            logger.error(f"Failed to calculate monthly bonuses for vendor {vendor.id}: {str(e)}")
            return []
    
    @classmethod
    def _calculate_performance_metrics(cls, vendor, bookings):
        """Calculate performance metrics for a vendor"""
        from .models import Signature
        
        total_bookings = bookings.count()
        
        # Completion rate (already filtered for completed/signed)
        completion_rate = 100.0  # Since we're only looking at completed bookings
        
        # Signature rate
        signed_bookings = bookings.filter(signature__status='signed').count()
        signature_rate = (signed_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        # Average satisfaction score
        signatures = Signature.objects.filter(
            booking__in=bookings,
            status='signed',
            satisfaction_rating__isnull=False
        )
        avg_satisfaction = signatures.aggregate(avg_rating=Avg('satisfaction_rating'))['avg_rating'] or 0
        
        # Average response time (simplified - time from booking creation to vendor assignment)
        response_times = []
        for booking in bookings:
            if booking.vendor and booking.created_at:
                # Using scheduled_date as proxy for assignment time
                response_time = (booking.scheduled_date - booking.created_at).total_seconds() / 3600
                if response_time > 0:
                    response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 24
        
        # Total earnings for bonus calculation base
        total_earnings = bookings.aggregate(total=Sum('total_price'))['total'] or Decimal('0')
        
        return {
            'total_bookings': total_bookings,
            'completion_rate': completion_rate,
            'signature_rate': signature_rate,
            'avg_satisfaction': float(avg_satisfaction),
            'avg_response_time': avg_response_time,
            'total_earnings': total_earnings,
            'signed_bookings': signed_bookings
        }
    
    @classmethod
    def _calculate_performance_bonuses(cls, vendor, metrics, period_start, period_end):
        """Calculate performance-based bonuses"""
        bonuses = []
        base_amount = min(metrics['total_earnings'] * Decimal('0.05'), Decimal('5000'))  # Max 5% of earnings or ₹5000
        
        # Completion rate bonus (already 100% since we filter completed bookings)
        # This would be more meaningful with cancelled/failed bookings included
        
        # Signature rate bonus
        signature_rate = metrics['signature_rate']
        for tier, config in cls.PERFORMANCE_THRESHOLDS['signature_rate'].items():
            if signature_rate >= config['threshold']:
                bonus_amount = base_amount * Decimal(str(config['bonus_percentage'] / 100))
                bonuses.append({
                    'vendor': vendor,
                    'bonus_type': 'completion_rate',
                    'amount': bonus_amount,
                    'percentage': config['bonus_percentage'],
                    'criteria_met': {
                        'signature_rate': signature_rate,
                        'threshold': config['threshold'],
                        'tier': tier
                    },
                    'calculation_details': {
                        'base_amount': float(base_amount),
                        'bonus_percentage': config['bonus_percentage'],
                        'total_bookings': metrics['total_bookings'],
                        'signed_bookings': metrics['signed_bookings']
                    },
                    'period_start': period_start,
                    'period_end': period_end,
                    'notes': f"High signature rate ({signature_rate:.1f}%) - {tier} tier"
                })
                break  # Only award highest applicable tier
        
        # Satisfaction score bonus
        avg_satisfaction = metrics['avg_satisfaction']
        for tier, config in cls.PERFORMANCE_THRESHOLDS['satisfaction_score'].items():
            if avg_satisfaction >= config['threshold']:
                bonus_amount = base_amount * Decimal(str(config['bonus_percentage'] / 100))
                bonuses.append({
                    'vendor': vendor,
                    'bonus_type': 'satisfaction',
                    'amount': bonus_amount,
                    'percentage': config['bonus_percentage'],
                    'criteria_met': {
                        'avg_satisfaction': avg_satisfaction,
                        'threshold': config['threshold'],
                        'tier': tier
                    },
                    'calculation_details': {
                        'base_amount': float(base_amount),
                        'bonus_percentage': config['bonus_percentage'],
                        'total_bookings': metrics['total_bookings']
                    },
                    'period_start': period_start,
                    'period_end': period_end,
                    'notes': f"High customer satisfaction ({avg_satisfaction:.1f}/5) - {tier} tier"
                })
                break
        
        return bonuses
    
    @classmethod
    def _calculate_surge_bonuses(cls, vendor, bookings, period_start, period_end):
        """Calculate surge pricing bonuses for high-demand periods"""
        from .models import PincodeAnalytics
        
        bonuses = []
        
        # Group bookings by pincode and date
        surge_bookings = {}
        for booking in bookings:
            key = (booking.pincode, booking.completion_date.date())
            if key not in surge_bookings:
                surge_bookings[key] = []
            surge_bookings[key].append(booking)
        
        # Check each pincode-date combination for surge conditions
        for (pincode, date), booking_list in surge_bookings.items():
            try:
                # Get analytics for that day
                analytics = PincodeAnalytics.objects.filter(
                    pincode=pincode,
                    date=date
                ).first()
                
                if not analytics:
                    continue
                
                # Determine surge level based on demand ratio
                demand_ratio = analytics.demand_ratio
                surge_level = None
                
                if demand_ratio >= 8:
                    surge_level = 'critical_demand'
                elif demand_ratio >= 5:
                    surge_level = 'very_high_demand'
                elif demand_ratio >= 3:
                    surge_level = 'high_demand'
                
                if surge_level:
                    multiplier = cls.SURGE_MULTIPLIERS[surge_level]
                    
                    # Calculate bonus for each booking in this surge period
                    for booking in booking_list:
                        base_earning = booking.total_price
                        bonus_amount = base_earning * (multiplier - Decimal('1.0'))  # Only the bonus portion
                        
                        bonuses.append({
                            'vendor': vendor,
                            'booking': booking,
                            'bonus_type': 'surge',
                            'amount': bonus_amount,
                            'percentage': float((multiplier - Decimal('1.0')) * 100),
                            'criteria_met': {
                                'demand_ratio': demand_ratio,
                                'surge_level': surge_level,
                                'pincode': pincode,
                                'date': date.isoformat()
                            },
                            'calculation_details': {
                                'base_earning': float(base_earning),
                                'surge_multiplier': float(multiplier),
                                'available_vendors': analytics.available_vendors,
                                'total_bookings': analytics.total_bookings
                            },
                            'period_start': period_start,
                            'period_end': period_end,
                            'notes': f"Surge bonus for {surge_level.replace('_', ' ')} in {pincode}"
                        })
                
            except Exception as e:
                logger.error(f"Failed to calculate surge bonus for {pincode} on {date}: {str(e)}")
                continue
        
        return bonuses
    
    @classmethod
    def _calculate_monthly_incentive(cls, vendor, metrics, period_start, period_end):
        """Calculate monthly incentive for overall performance"""
        
        # Criteria for monthly incentive:
        # - At least 20 completed bookings
        # - Signature rate >= 90%
        # - Average satisfaction >= 4.0
        
        if (metrics['total_bookings'] >= 20 and
            metrics['signature_rate'] >= 90 and
            metrics['avg_satisfaction'] >= 4.0):
            
            # Tiered monthly incentive
            if metrics['total_bookings'] >= 50:
                incentive_amount = Decimal('3000')
                tier = 'platinum'
            elif metrics['total_bookings'] >= 35:
                incentive_amount = Decimal('2000')
                tier = 'gold'
            else:
                incentive_amount = Decimal('1000')
                tier = 'silver'
            
            return {
                'vendor': vendor,
                'bonus_type': 'monthly_incentive',
                'amount': incentive_amount,
                'criteria_met': {
                    'total_bookings': metrics['total_bookings'],
                    'signature_rate': metrics['signature_rate'],
                    'avg_satisfaction': metrics['avg_satisfaction'],
                    'tier': tier
                },
                'calculation_details': {
                    'minimum_bookings': 20,
                    'minimum_signature_rate': 90,
                    'minimum_satisfaction': 4.0,
                    'tier_achieved': tier
                },
                'period_start': period_start,
                'period_end': period_end,
                'notes': f"Monthly incentive - {tier} tier ({metrics['total_bookings']} bookings)"
            }
        
        return None
    
    @classmethod
    def calculate_real_time_surge_bonus(cls, booking):
        """Calculate surge bonus for a single booking in real-time"""
        from .models import PincodeAnalytics
        
        try:
            # Get today's analytics for the booking's pincode
            today = timezone.now().date()
            analytics = PincodeAnalytics.objects.filter(
                pincode=booking.pincode,
                date=today
            ).first()
            
            if not analytics:
                return None
            
            # Check if surge conditions are met
            demand_ratio = analytics.demand_ratio
            surge_level = None
            
            if demand_ratio >= 8:
                surge_level = 'critical_demand'
            elif demand_ratio >= 5:
                surge_level = 'very_high_demand'
            elif demand_ratio >= 3:
                surge_level = 'high_demand'
            
            if surge_level:
                multiplier = cls.SURGE_MULTIPLIERS[surge_level]
                base_price = booking.total_price
                bonus_amount = base_price * (multiplier - Decimal('1.0'))
                
                return {
                    'surge_level': surge_level,
                    'multiplier': float(multiplier),
                    'bonus_amount': bonus_amount,
                    'demand_ratio': demand_ratio,
                    'total_price_with_bonus': base_price + bonus_amount
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to calculate real-time surge bonus: {str(e)}")
            return None
    
    @classmethod
    def get_vendor_bonus_summary(cls, vendor, year=None, month=None):
        """Get bonus summary for a vendor"""
        from .models import VendorBonus
        
        try:
            bonuses = VendorBonus.objects.filter(vendor=vendor)
            
            if year and month:
                period_start = datetime(year, month, 1).date()
                if month == 12:
                    period_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    period_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
                
                bonuses = bonuses.filter(
                    period_start__gte=period_start,
                    period_end__lte=period_end
                )
            
            summary = {
                'total_bonuses': bonuses.count(),
                'total_amount': bonuses.aggregate(total=Sum('amount'))['total'] or Decimal('0'),
                'pending_amount': bonuses.filter(status='pending').aggregate(total=Sum('amount'))['total'] or Decimal('0'),
                'paid_amount': bonuses.filter(status='paid').aggregate(total=Sum('amount'))['total'] or Decimal('0'),
                'by_type': {},
                'by_month': {},
                'recent_bonuses': []
            }
            
            # Group by bonus type
            for bonus_type, display_name in VendorBonus.BONUS_TYPE_CHOICES:
                type_bonuses = bonuses.filter(bonus_type=bonus_type)
                if type_bonuses.exists():
                    summary['by_type'][display_name] = {
                        'count': type_bonuses.count(),
                        'amount': type_bonuses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
                    }
            
            # Recent bonuses (last 5)
            recent = bonuses.order_by('-created_at')[:5]
            for bonus in recent:
                summary['recent_bonuses'].append({
                    'id': str(bonus.id),
                    'type': bonus.get_bonus_type_display(),
                    'amount': float(bonus.amount),
                    'status': bonus.get_status_display(),
                    'created_at': bonus.created_at.isoformat(),
                    'notes': bonus.notes
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get vendor bonus summary: {str(e)}")
            return {}


# Singleton instance
vendor_bonus_service = VendorBonusService()