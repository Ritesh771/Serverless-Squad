from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q, F
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


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