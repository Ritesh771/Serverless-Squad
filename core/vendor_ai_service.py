import numpy as np
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q, F
from django.core.cache import cache
import logging
import json

logger = logging.getLogger(__name__)


class VendorPerformanceAI:
    """AI-based vendor performance scoring and analytics system"""

    # Scoring weights for different metrics
    SCORING_WEIGHTS = {
        'completion_rate': 0.25,      # 25% weight
        'satisfaction_score': 0.30,   # 30% weight
        'response_time': 0.15,        # 15% weight
        'signature_rate': 0.20,       # 20% weight
        'reliability': 0.10           # 10% weight (cancellation rate, disputes)
    }

    # Performance categories
    PERFORMANCE_CATEGORIES = {
        'excellent': {'min_score': 85, 'color': '#28a745'},
        'good': {'min_score': 70, 'color': '#17a2b8'},
        'average': {'min_score': 55, 'color': '#ffc107'},
        'poor': {'min_score': 40, 'color': '#fd7e14'},
        'critical': {'min_score': 0, 'color': '#dc3545'}
    }

    @classmethod
    def calculate_vendor_score(cls, vendor, analysis_period_days=90):
        """
        Calculate comprehensive vendor performance score using AI algorithms

        Returns:
            dict: Complete scoring breakdown with predictions
        """
        try:
            # Get historical data
            end_date = timezone.now()
            start_date = end_date - timedelta(days=analysis_period_days)

            # Fetch vendor performance data
            performance_data = cls._gather_performance_data(vendor, start_date, end_date)

            if not performance_data['total_bookings']:
                return cls._generate_new_vendor_score()

            # Calculate individual metric scores
            metric_scores = cls._calculate_metric_scores(performance_data)

            # Apply AI weighting and calculate composite score
            composite_score = cls._calculate_composite_score(metric_scores)

            # Generate performance insights
            insights = cls._generate_performance_insights(vendor, performance_data, metric_scores)

            # Predict future performance trends
            predictions = cls._predict_performance_trends(vendor, performance_data)

            # Determine performance category
            category = cls._determine_performance_category(composite_score)

            # Calculate reliability indicators
            reliability = cls._calculate_reliability_indicators(performance_data)

            result = {
                'vendor_id': vendor.id,
                'vendor_name': vendor.get_full_name(),
                'analysis_period_days': analysis_period_days,
                'analysis_date': timezone.now().isoformat(),

                # Core scores
                'composite_score': round(composite_score, 2),
                'performance_category': category,
                'metric_scores': metric_scores,

                # Raw performance data
                'performance_data': performance_data,

                # AI insights and recommendations
                'insights': insights,
                'predictions': predictions,
                'reliability': reliability,

                # Recommendations
                'recommendations': cls._generate_recommendations(metric_scores, insights),

                # Risk assessment
                'risk_assessment': cls._assess_vendor_risk(performance_data, metric_scores)
            }

            # Cache the result
            cache_key = f"vendor_score_{vendor.id}_{analysis_period_days}"
            cache.set(cache_key, result, 3600)  # Cache for 1 hour

            return result

        except Exception as e:
            logger.error(f"Failed to calculate vendor score for {vendor.id}: {str(e)}")
            return cls._generate_error_score(vendor)

    @classmethod
    def _gather_performance_data(cls, vendor, start_date, end_date):
        """Gather comprehensive performance data for analysis"""
        from .models import Booking, Signature, Dispute

        # Get all bookings in the period
        bookings = Booking.objects.filter(
            vendor=vendor,
            created_at__range=[start_date, end_date]
        )

        total_bookings = bookings.count()

        if total_bookings == 0:
            return {
                'total_bookings': 0,
                'completed_bookings': 0,
                'cancelled_bookings': 0,
                'disputed_bookings': 0,
                'avg_satisfaction': 0,
                'signature_rate': 0,
                'avg_response_time': 0,
                'total_earnings': Decimal('0'),
                'booking_trends': []
            }

        # Calculate completion metrics
        completed_bookings = bookings.filter(status__in=['completed', 'signed']).count()
        cancelled_bookings = bookings.filter(status='cancelled').count()
        disputed_bookings = bookings.filter(status='disputed').count()

        # Signature metrics
        signed_bookings = bookings.filter(signature__status='signed').count()
        signature_rate = (signed_bookings / total_bookings * 100) if total_bookings > 0 else 0

        # Satisfaction metrics
        signatures = Signature.objects.filter(
            booking__in=bookings,
            status='signed',
            satisfaction_rating__isnull=False
        )
        avg_satisfaction = signatures.aggregate(avg=Avg('satisfaction_rating'))['avg'] or 0

        # Response time analysis
        response_times = []
        for booking in bookings.filter(vendor__isnull=False):
            if booking.created_at and booking.scheduled_date:
                response_time = (booking.scheduled_date - booking.created_at).total_seconds() / 3600
                if 0 < response_time <= 72:  # Reasonable response time range
                    response_times.append(response_time)

        avg_response_time = sum(response_times) / len(response_times) if response_times else 24

        # Financial metrics
        total_earnings = bookings.filter(
            status__in=['completed', 'signed']
        ).aggregate(total=Sum('total_price'))['total'] or Decimal('0')

        # Booking trends (weekly aggregation)
        booking_trends = cls._calculate_booking_trends(bookings, start_date, end_date)

        return {
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'disputed_bookings': disputed_bookings,
            'signed_bookings': signed_bookings,
            'avg_satisfaction': float(avg_satisfaction) if avg_satisfaction else 0,
            'signature_rate': signature_rate,
            'avg_response_time': avg_response_time,
            'total_earnings': total_earnings,
            'booking_trends': booking_trends,
            'response_times': response_times
        }

    @classmethod
    def _calculate_metric_scores(cls, data):
        """Calculate individual metric scores (0-100 scale)"""

        # Completion Rate Score (0-100)
        completion_rate = (data['completed_bookings'] / data['total_bookings'] * 100) if data['total_bookings'] > 0 else 0
        completion_score = min(100, completion_rate * 1.1)  # Slight boost for calculation

        # Satisfaction Score (convert 1-5 scale to 0-100)
        satisfaction_score = (data['avg_satisfaction'] / 5.0 * 100) if data['avg_satisfaction'] > 0 else 0

        # Response Time Score (inverse relationship - faster is better)
        # Optimal response time: 2-8 hours = 100 points
        # 24 hours = 50 points, 48+ hours = 0 points
        response_time = data['avg_response_time']
        if response_time <= 2:
            response_score = 100
        elif response_time <= 8:
            response_score = 100 - (response_time - 2) * 5  # Gradual decrease
        elif response_time <= 24:
            response_score = 70 - (response_time - 8) * 1.25
        else:
            response_score = max(0, 50 - (response_time - 24) * 2)

        # Signature Rate Score
        signature_score = min(100, data['signature_rate'] * 1.05)  # Slight boost

        # Reliability Score (based on cancellation and dispute rates)
        total_issues = data['cancelled_bookings'] + data['disputed_bookings']
        issue_rate = (total_issues / data['total_bookings'] * 100) if data['total_bookings'] > 0 else 0
        reliability_score = max(0, 100 - (issue_rate * 3))  # Heavy penalty for issues

        return {
            'completion_rate': round(completion_score, 2),
            'satisfaction_score': round(satisfaction_score, 2),
            'response_time': round(response_score, 2),
            'signature_rate': round(signature_score, 2),
            'reliability': round(reliability_score, 2)
        }

    @classmethod
    def _calculate_composite_score(cls, metric_scores):
        """Calculate weighted composite score using AI algorithms"""
        composite = 0

        for metric, score in metric_scores.items():
            weight = cls.SCORING_WEIGHTS.get(metric, 0)
            composite += score * weight

        # Apply AI-based adjustments based on score distribution
        score_variance = cls._calculate_score_variance(metric_scores)

        # Penalize vendors with highly inconsistent performance
        if score_variance > 400:  # High variance penalty
            composite *= 0.9
        elif score_variance < 100:  # Reward consistent performance
            composite *= 1.05

        return min(100, max(0, composite))

    @classmethod
    def _calculate_score_variance(cls, metric_scores):
        """Calculate variance in metric scores to assess consistency"""
        scores = list(metric_scores.values())
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        return variance

    @classmethod
    def _generate_performance_insights(cls, vendor, data, scores):
        """Generate AI-based performance insights"""
        insights = []

        # Completion rate insights
        completion_rate = (data['completed_bookings'] / data['total_bookings'] * 100) if data['total_bookings'] > 0 else 0
        if completion_rate >= 95:
            insights.append({
                'type': 'strength',
                'metric': 'completion_rate',
                'message': f"Excellent completion rate of {completion_rate:.1f}%",
                'impact': 'high'
            })
        elif completion_rate < 80:
            insights.append({
                'type': 'concern',
                'metric': 'completion_rate',
                'message': f"Low completion rate of {completion_rate:.1f}% needs attention",
                'impact': 'high'
            })

        # Satisfaction insights
        if data['avg_satisfaction'] >= 4.5:
            insights.append({
                'type': 'strength',
                'metric': 'satisfaction',
                'message': f"Outstanding customer satisfaction ({data['avg_satisfaction']:.1f}/5.0)",
                'impact': 'high'
            })
        elif data['avg_satisfaction'] < 3.5:
            insights.append({
                'type': 'concern',
                'metric': 'satisfaction',
                'message': f"Customer satisfaction needs improvement ({data['avg_satisfaction']:.1f}/5.0)",
                'impact': 'high'
            })

        # Response time insights
        if data['avg_response_time'] <= 4:
            insights.append({
                'type': 'strength',
                'metric': 'response_time',
                'message': f"Very fast response time ({data['avg_response_time']:.1f} hours)",
                'impact': 'medium'
            })
        elif data['avg_response_time'] > 24:
            insights.append({
                'type': 'concern',
                'metric': 'response_time',
                'message': f"Slow response time ({data['avg_response_time']:.1f} hours)",
                'impact': 'medium'
            })

        # Signature rate insights
        if data['signature_rate'] >= 90:
            insights.append({
                'type': 'strength',
                'metric': 'signature_rate',
                'message': f"High signature completion rate ({data['signature_rate']:.1f}%)",
                'impact': 'medium'
            })
        elif data['signature_rate'] < 70:
            insights.append({
                'type': 'concern',
                'metric': 'signature_rate',
                'message': f"Low signature rate ({data['signature_rate']:.1f}%) may delay payments",
                'impact': 'medium'
            })

        return insights

    @classmethod
    def _predict_performance_trends(cls, vendor, data):
        """Predict future performance trends using simple ML algorithms"""
        predictions = {}

        # Analyze booking trends
        trends = data['booking_trends']
        if len(trends) >= 4:  # Need at least 4 data points
            # Simple linear regression for booking volume
            weeks = list(range(len(trends)))
            booking_counts = [week['bookings'] for week in trends]

            # Calculate trend direction
            if len(booking_counts) >= 2:
                recent_avg = sum(booking_counts[-2:]) / 2
                earlier_avg = sum(booking_counts[:2]) / 2

                if recent_avg > earlier_avg * 1.1:
                    trend_direction = 'increasing'
                elif recent_avg < earlier_avg * 0.9:
                    trend_direction = 'decreasing'
                else:
                    trend_direction = 'stable'

                predictions['booking_trend'] = {
                    'direction': trend_direction,
                    'confidence': min(100, abs(recent_avg - earlier_avg) / earlier_avg * 100) if earlier_avg > 0 else 0
                }

        # Performance trajectory prediction
        if data['total_bookings'] >= 10:
            # Predict if vendor is improving or declining
            recent_performance_score = cls._calculate_recent_performance_score(vendor)
            overall_score = cls._calculate_composite_score(cls._calculate_metric_scores(data))

            if recent_performance_score > overall_score * 1.05:
                trajectory = 'improving'
            elif recent_performance_score < overall_score * 0.95:
                trajectory = 'declining'
            else:
                trajectory = 'stable'

            predictions['performance_trajectory'] = {
                'direction': trajectory,
                'recent_score': round(recent_performance_score, 2),
                'overall_score': round(overall_score, 2)
            }

        return predictions

    @classmethod
    def _calculate_recent_performance_score(cls, vendor):
        """Calculate performance score for recent period (last 30 days)"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        recent_data = cls._gather_performance_data(vendor, start_date, end_date)
        if recent_data['total_bookings'] == 0:
            return 0

        recent_scores = cls._calculate_metric_scores(recent_data)
        return cls._calculate_composite_score(recent_scores)

    @classmethod
    def _calculate_booking_trends(cls, bookings, start_date, end_date):
        """Calculate weekly booking trends"""
        trends = []
        current_date = start_date

        while current_date < end_date:
            week_end = min(current_date + timedelta(days=7), end_date)

            week_bookings = bookings.filter(
                created_at__range=[current_date, week_end]
            )

            trends.append({
                'week_start': current_date.date().isoformat(),
                'week_end': week_end.date().isoformat(),
                'bookings': week_bookings.count(),
                'completed': week_bookings.filter(status__in=['completed', 'signed']).count()
            })

            current_date = week_end

        return trends

    @classmethod
    def _determine_performance_category(cls, score):
        """Determine performance category based on score"""
        for category, config in cls.PERFORMANCE_CATEGORIES.items():
            if score >= config['min_score']:
                return {
                    'name': category,
                    'min_score': config['min_score'],
                    'color': config['color']
                }

        return cls.PERFORMANCE_CATEGORIES['critical']

    @classmethod
    def _calculate_reliability_indicators(cls, data):
        """Calculate reliability indicators"""
        total_bookings = data['total_bookings']

        if total_bookings == 0:
            return {'overall_reliability': 0, 'risk_level': 'unknown'}

        # Calculate various reliability metrics
        completion_reliability = (data['completed_bookings'] / total_bookings) * 100
        dispute_rate = (data['disputed_bookings'] / total_bookings) * 100
        cancellation_rate = (data['cancelled_bookings'] / total_bookings) * 100

        # Overall reliability score
        reliability_score = (
            completion_reliability * 0.5 +
            (100 - dispute_rate) * 0.3 +
            (100 - cancellation_rate) * 0.2
        )

        # Determine risk level
        if reliability_score >= 90:
            risk_level = 'low'
        elif reliability_score >= 75:
            risk_level = 'medium'
        elif reliability_score >= 60:
            risk_level = 'high'
        else:
            risk_level = 'critical'

        return {
            'overall_reliability': round(reliability_score, 2),
            'completion_reliability': round(completion_reliability, 2),
            'dispute_rate': round(dispute_rate, 2),
            'cancellation_rate': round(cancellation_rate, 2),
            'risk_level': risk_level
        }

    @classmethod
    def _generate_recommendations(cls, metric_scores, insights):
        """Generate AI-based recommendations for improvement"""
        recommendations = []

        # Find the lowest scoring metrics
        sorted_metrics = sorted(metric_scores.items(), key=lambda x: x[1])

        for metric, score in sorted_metrics[:2]:  # Focus on top 2 improvement areas
            if score < 70:
                if metric == 'completion_rate':
                    recommendations.append({
                        'category': 'completion_rate',
                        'priority': 'high',
                        'title': 'Improve Service Completion Rate',
                        'description': 'Focus on completing all accepted bookings to improve reliability.',
                        'action_items': [
                            'Review booking acceptance criteria',
                            'Improve time management and scheduling',
                            'Address common cancellation reasons'
                        ]
                    })

                elif metric == 'satisfaction_score':
                    recommendations.append({
                        'category': 'customer_satisfaction',
                        'priority': 'high',
                        'title': 'Enhance Customer Satisfaction',
                        'description': 'Improve service quality to achieve higher customer ratings.',
                        'action_items': [
                            'Request specific feedback from customers',
                            'Attend customer service training',
                            'Ensure thorough service delivery'
                        ]
                    })

                elif metric == 'response_time':
                    recommendations.append({
                        'category': 'responsiveness',
                        'priority': 'medium',
                        'title': 'Improve Response Time',
                        'description': 'Respond to booking requests more quickly to increase acceptance rates.',
                        'action_items': [
                            'Enable push notifications for new bookings',
                            'Check the app more frequently',
                            'Set up automatic availability updates'
                        ]
                    })

                elif metric == 'signature_rate':
                    recommendations.append({
                        'category': 'signature_completion',
                        'priority': 'medium',
                        'title': 'Increase Signature Completion Rate',
                        'description': 'Help customers complete satisfaction signatures promptly.',
                        'action_items': [
                            'Explain the signature process to customers',
                            'Follow up on pending signatures',
                            'Ensure service quality before requesting signatures'
                        ]
                    })

        return recommendations

    @classmethod
    def _assess_vendor_risk(cls, data, scores):
        """Assess vendor risk level for business decisions"""
        risk_factors = []
        risk_score = 0

        # Low completion rate risk
        completion_rate = (data['completed_bookings'] / data['total_bookings'] * 100) if data['total_bookings'] > 0 else 0
        if completion_rate < 70:
            risk_factors.append('Low completion rate')
            risk_score += 25

        # High dispute rate risk
        dispute_rate = (data['disputed_bookings'] / data['total_bookings'] * 100) if data['total_bookings'] > 0 else 0
        if dispute_rate > 5:
            risk_factors.append('High dispute rate')
            risk_score += 30

        # Low satisfaction risk
        if data['avg_satisfaction'] < 3.5:
            risk_factors.append('Low customer satisfaction')
            risk_score += 20

        # Poor response time risk
        if data['avg_response_time'] > 48:
            risk_factors.append('Poor response time')
            risk_score += 15

        # Low signature rate risk
        if data['signature_rate'] < 60:
            risk_factors.append('Low signature completion rate')
            risk_score += 10

        # Determine overall risk level
        if risk_score >= 50:
            risk_level = 'high'
        elif risk_score >= 25:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'recommended_actions': cls._get_risk_mitigation_actions(risk_level, risk_factors)
        }

    @classmethod
    def _get_risk_mitigation_actions(cls, risk_level, risk_factors):
        """Get recommended actions for risk mitigation"""
        if risk_level == 'high':
            return [
                'Consider temporary suspension pending improvement',
                'Require mandatory performance improvement plan',
                'Increase monitoring and support'
            ]
        elif risk_level == 'medium':
            return [
                'Provide additional training and support',
                'Monitor performance closely',
                'Set specific improvement targets'
            ]
        else:
            return [
                'Continue regular monitoring',
                'Provide positive reinforcement',
                'Consider for performance bonuses'
            ]

    @classmethod
    def _generate_new_vendor_score(cls):
        """Generate default score for new vendors"""
        return {
            'vendor_id': None,
            'vendor_name': 'New Vendor',
            'composite_score': 60,  # Neutral starting score
            'performance_category': {'name': 'average', 'color': '#ffc107'},
            'metric_scores': {
                'completion_rate': 60,
                'satisfaction_score': 60,
                'response_time': 60,
                'signature_rate': 60,
                'reliability': 60
            },
            'insights': [{
                'type': 'info',
                'message': 'New vendor - performance data will improve with more bookings',
                'impact': 'low'
            }],
            'recommendations': [{
                'category': 'general',
                'priority': 'medium',
                'title': 'Build Performance History',
                'description': 'Complete initial bookings with high quality to establish good performance metrics.',
                'action_items': [
                    'Focus on timely service delivery',
                    'Ensure high customer satisfaction',
                    'Complete all signature processes'
                ]
            }]
        }

    @classmethod
    def _generate_error_score(cls, vendor):
        """Generate error response for scoring failures"""
        return {
            'vendor_id': vendor.id,
            'vendor_name': vendor.get_full_name(),
            'error': 'Failed to calculate performance score',
            'composite_score': 0,
            'performance_category': {'name': 'unknown', 'color': '#6c757d'}
        }

    @classmethod
    def predict_service_duration(cls, service, vendor, pincode):
        """Predict service duration using AI based on historical data"""
        try:
            # Get historical data for similar services
            from .models import Booking

            similar_bookings = Booking.objects.filter(
                service=service,
                vendor=vendor,
                status__in=['completed', 'signed'],
                completion_date__isnull=False
            )[:20]  # Last 20 similar bookings

            if similar_bookings.count() < 3:
                # Not enough data, use service default + vendor adjustment
                base_duration = service.duration_minutes
                vendor_score = cls.calculate_vendor_score(vendor)
                efficiency_factor = vendor_score.get('composite_score', 60) / 100

                # Efficient vendors might complete faster
                if efficiency_factor > 0.8:
                    predicted_duration = base_duration * 0.9
                elif efficiency_factor < 0.6:
                    predicted_duration = base_duration * 1.2
                else:
                    predicted_duration = base_duration

                return {
                    'predicted_minutes': int(predicted_duration),
                    'confidence': 'low',
                    'based_on': 'service_default_with_vendor_adjustment',
                    'data_points': similar_bookings.count()
                }

            # Calculate durations from historical data
            durations = []
            for booking in similar_bookings:
                if booking.scheduled_date and booking.completion_date:
                    duration = (booking.completion_date - booking.scheduled_date).total_seconds() / 60
                    if 10 <= duration <= 480:  # Reasonable range: 10 minutes to 8 hours
                        durations.append(duration)

            if durations:
                # Use statistical analysis
                avg_duration = sum(durations) / len(durations)

                # Adjust for pincode factors (simplified)
                pincode_factor = 1.0
                if pincode.startswith('1'):  # Urban areas (simplified logic)
                    pincode_factor = 0.95  # Slightly faster in urban areas
                elif pincode.startswith('4'):  # Rural areas (simplified logic)
                    pincode_factor = 1.1   # Slightly longer in rural areas

                predicted_duration = avg_duration * pincode_factor

                return {
                    'predicted_minutes': int(predicted_duration),
                    'confidence': 'high' if len(durations) >= 10 else 'medium',
                    'based_on': 'historical_data',
                    'data_points': len(durations),
                    'avg_historical_duration': round(avg_duration, 1)
                }

            # Fallback to service default
            return {
                'predicted_minutes': service.duration_minutes,
                'confidence': 'low',
                'based_on': 'service_default',
                'data_points': 0
            }

        except Exception as e:
            logger.error(f"Failed to predict service duration: {str(e)}")
            return {
                'predicted_minutes': service.duration_minutes,
                'confidence': 'unknown',
                'error': str(e)
            }

    @classmethod
    def detect_fraudulent_patterns(cls, booking):
        """Detect potentially fraudulent booking patterns"""
        try:
            fraud_indicators = []
            risk_score = 0

            # Check for rapid booking patterns
            recent_bookings = Booking.objects.filter(
                customer=booking.customer,
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count()

            if recent_bookings > 5:
                fraud_indicators.append('Excessive bookings in 24 hours')
                risk_score += 30

            # Check for unusual pricing patterns
            if booking.total_price > booking.service.base_price * 3:
                fraud_indicators.append('Unusual pricing (3x base price)')
                risk_score += 20

            # Check for vendor-customer collusion patterns
            previous_bookings_with_vendor = Booking.objects.filter(
                customer=booking.customer,
                vendor=booking.vendor
            ).count()

            if previous_bookings_with_vendor > 10:
                fraud_indicators.append('High frequency vendor-customer pair')
                risk_score += 15

            # Check for signature manipulation patterns
            if hasattr(booking, 'signature') and booking.signature:
                signature_time = booking.signature.signed_at
                completion_time = booking.completion_date

                if signature_time and completion_time:
                    time_diff = (signature_time - completion_time).total_seconds() / 60
                    if time_diff < 1:  # Signed within 1 minute of completion
                        fraud_indicators.append('Suspiciously fast signature')
                        risk_score += 25

            # Determine risk level
            if risk_score >= 50:
                risk_level = 'high'
            elif risk_score >= 25:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'fraud_indicators': fraud_indicators,
                'requires_review': risk_score >= 30,
                'recommended_actions': cls._get_fraud_mitigation_actions(risk_level)
            }

        except Exception as e:
            logger.error(f"Failed to detect fraudulent patterns: {str(e)}")
            return {
                'risk_level': 'unknown',
                'error': str(e)
            }

    @classmethod
    def _get_fraud_mitigation_actions(cls, risk_level):
        """Get recommended actions for fraud mitigation"""
        if risk_level == 'high':
            return [
                'Flag for manual review immediately',
                'Temporarily hold payment processing',
                'Require additional verification'
            ]
        elif risk_level == 'medium':
            return [
                'Monitor closely for patterns',
                'Request additional documentation',
                'Review signature timing'
            ]
        else:
            return [
                'Continue normal processing',
                'Maintain standard monitoring'
            ]


# Singleton instance
vendor_ai_service = VendorPerformanceAI()