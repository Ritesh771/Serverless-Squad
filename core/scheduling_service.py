"""
Smart Scheduling Service for vendor calendar management with intelligent buffering
"""
import logging
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple
from django.utils import timezone
from django.db.models import Q, F
from .models import User, Booking, Service, VendorAvailability
from .travel_service import travel_service

logger = logging.getLogger(__name__)


class SmartSchedulingService:
    """Service for intelligent booking scheduling with travel time and buffer management"""
    
    def __init__(self):
        self.default_buffer_minutes = 30
        self.max_daily_bookings = 8
        self.min_break_between_bookings = 15  # Minimum break even with zero travel time
    
    def get_available_time_slots(self, vendor_id: int, service_id: int, customer_pincode: str, 
                                preferred_date: datetime.date, days_ahead: int = 7) -> List[Dict]:
        """
        Get intelligent time slots for a vendor considering travel times and buffers
        
        Returns:
            List of available time slots with scheduling metadata
        """
        try:
            vendor = User.objects.get(id=vendor_id, role='vendor')
            service = Service.objects.get(id=service_id)
        except (User.DoesNotExist, Service.DoesNotExist):
            return []
        
        available_slots = []
        
        # Check each day in the range
        for day_offset in range(days_ahead):
            check_date = preferred_date + timedelta(days=day_offset)
            day_slots = self._get_day_available_slots(vendor, service, customer_pincode, check_date)
            available_slots.extend(day_slots)
        
        return sorted(available_slots, key=lambda x: x['start_time'])
    
    def _get_day_available_slots(self, vendor: User, service: Service, customer_pincode: str, 
                                check_date: datetime.date) -> List[Dict]:
        """Get available slots for a specific day"""
        day_name = check_date.strftime('%A').lower()
        
        # Get vendor availability for this day
        availability_slots = VendorAvailability.objects.filter(
            vendor=vendor,
            day_of_week=day_name,
            is_active=True
        ).order_by('start_time')
        
        if not availability_slots.exists():
            return []
        
        # Get existing bookings for this day
        existing_bookings = Booking.objects.filter(
            vendor=vendor,
            scheduled_date__date=check_date,
            status__in=['confirmed', 'in_progress']
        ).order_by('actual_start_time')
        
        available_slots = []
        
        for availability in availability_slots:
            day_start = datetime.combine(check_date, availability.start_time)
            day_end = datetime.combine(check_date, availability.end_time)
            
            # Make timezone aware
            day_start = timezone.make_aware(day_start)
            day_end = timezone.make_aware(day_end)
            
            # Calculate travel time from vendor's location to customer
            travel_data = travel_service.get_travel_time(
                vendor.pincode or availability.primary_pincode,
                customer_pincode
            )
            
            # Skip if travel time exceeds vendor's maximum
            if travel_data['duration_minutes'] > availability.max_travel_time_minutes:
                continue
            
            # Find available slots within this availability window
            slots = self._find_slots_in_window(
                vendor, service, customer_pincode, day_start, day_end, 
                existing_bookings, availability, travel_data
            )
            
            available_slots.extend(slots)
        
        return available_slots
    
    def _find_slots_in_window(self, vendor: User, service: Service, customer_pincode: str,
                             window_start: datetime, window_end: datetime,
                             existing_bookings, availability: VendorAvailability,
                             travel_data: Dict) -> List[Dict]:
        """Find available time slots within a specific time window"""
        slots = []
        service_duration = service.duration_minutes
        travel_time = travel_data['duration_minutes']
        buffer_time = availability.preferred_buffer_minutes
        
        # Adjust buffer time based on traffic conditions
        adjusted_buffer_time = self._adjust_buffer_for_traffic(buffer_time, travel_data)
        
        # Total time needed for this booking (travel + buffer + service + buffer + travel back)
        total_time_needed = travel_time + adjusted_buffer_time + service_duration + adjusted_buffer_time + travel_time
        
        # Start checking from the beginning of the window
        current_time = window_start
        slot_duration_minutes = 60  # Check hourly slots
        
        while current_time + timedelta(minutes=total_time_needed) <= window_end:
            # Calculate when vendor needs to start traveling
            travel_start_time = current_time - timedelta(minutes=travel_time)
            
            # Calculate when vendor will be free after this booking
            booking_end_time = current_time + timedelta(minutes=service_duration)
            vendor_free_time = booking_end_time + timedelta(minutes=adjusted_buffer_time + travel_time)
            
            # Check if this slot conflicts with existing bookings
            conflicts = self._check_conflicts(
                existing_bookings, travel_start_time, vendor_free_time
            )
            
            if not conflicts:
                # Calculate next booking travel time (if any)
                next_booking = self._get_next_booking_after(existing_bookings, vendor_free_time)
                next_travel_time = 0
                
                if next_booking:
                    next_travel_data = travel_service.get_travel_time(
                        customer_pincode, next_booking.pincode
                    )
                    next_travel_time = next_travel_data['duration_minutes']
                
                # Create slot info
                slot_info = {
                    'start_time': current_time,
                    'end_time': booking_end_time,
                    'vendor_start_time': travel_start_time,
                    'vendor_free_time': vendor_free_time,
                    'service_duration_minutes': service_duration,
                    'travel_time_minutes': travel_time,
                    'buffer_before_minutes': adjusted_buffer_time,
                    'buffer_after_minutes': adjusted_buffer_time,
                    'total_duration_minutes': total_time_needed,
                    'travel_data': travel_data,
                    'next_travel_time_minutes': next_travel_time,
                    'confidence_score': travel_data.get('confidence_score', 1.0),
                    'source': travel_data.get('source', 'estimated'),
                    'traffic_adjusted': adjusted_buffer_time != buffer_time
                }
                
                slots.append(slot_info)
            
            # Move to next potential slot
            current_time += timedelta(minutes=slot_duration_minutes)
        
        return slots
    
    def _adjust_buffer_for_traffic(self, base_buffer: int, travel_data: Dict) -> int:
        """
        Adjust buffer time based on traffic conditions and confidence score
        """
        # Get traffic multiplier based on data source and confidence
        confidence = travel_data.get('confidence_score', 0.5)
        source = travel_data.get('source', 'estimated')
        
        # Traffic multipliers
        traffic_multiplier = 1.0
        
        # Higher multiplier for real-time traffic data
        if source == 'api' and 'duration_in_traffic_minutes' in travel_data:
            normal_duration = travel_data['duration_minutes']
            traffic_duration = travel_data['duration_in_traffic_minutes']
            if normal_duration > 0:
                traffic_multiplier = max(1.0, traffic_duration / normal_duration)
        
        # Adjust based on confidence (lower confidence = more buffer)
        confidence_multiplier = 1.0 + (1.0 - confidence)  # Add 0-100% more buffer for low confidence
        
        # Calculate adjusted buffer
        adjusted_buffer = int(base_buffer * traffic_multiplier * confidence_multiplier)
        
        # Ensure minimum buffer
        return max(self.min_break_between_bookings, adjusted_buffer)
    
    def _check_conflicts(self, existing_bookings, start_time: datetime, end_time: datetime) -> bool:
        """Check if proposed time conflicts with existing bookings"""
        for booking in existing_bookings:
            booking_start = booking.actual_start_time or booking.scheduled_date
            booking_end = booking.actual_end_time or (
                booking.scheduled_date + timedelta(minutes=booking.calculate_total_duration_minutes())
            )
            
            # Check for overlap
            if (start_time < booking_end and end_time > booking_start):
                return True
        
        return False
    
    def _get_next_booking_after(self, existing_bookings, after_time: datetime):
        """Get the next booking after specified time"""
        for booking in existing_bookings:
            booking_start = booking.actual_start_time or booking.scheduled_date
            if booking_start > after_time:
                return booking
        return None
    
    def optimize_vendor_schedule(self, vendor_id: int, date: datetime.date) -> Dict:
        """Optimize a vendor's schedule for a specific day"""
        try:
            vendor = User.objects.get(id=vendor_id, role='vendor')
        except User.DoesNotExist:
            return {'error': 'Vendor not found'}
        
        # Get all bookings for the day
        bookings = Booking.objects.filter(
            vendor=vendor,
            scheduled_date__date=date,
            status__in=['confirmed', 'in_progress']
        ).order_by('scheduled_date')
        
        if not bookings.exists():
            return {'message': 'No bookings to optimize'}
        
        optimization_suggestions = []
        total_travel_time = 0
        total_idle_time = 0
        
        # Analyze each booking
        previous_booking = None
        for booking in bookings:
            suggestion = self._analyze_booking_efficiency(booking, previous_booking)
            if suggestion:
                optimization_suggestions.append(suggestion)
            
            total_travel_time += (booking.travel_time_to_location_minutes or 0)
            total_travel_time += (booking.travel_time_from_location_minutes or 0)
            
            previous_booking = booking
        
        # Calculate total working time
        first_booking = bookings.first()
        last_booking = bookings.last()
        
        day_start = first_booking.actual_start_time or first_booking.scheduled_date
        day_end = last_booking.actual_end_time or (
            last_booking.scheduled_date + timedelta(minutes=last_booking.calculate_total_duration_minutes())
        )
        
        total_working_time = int((day_end - day_start).total_seconds() / 60)
        
        return {
            'vendor_id': vendor_id,
            'date': date,
            'total_bookings': bookings.count(),
            'total_working_time_minutes': total_working_time,
            'total_travel_time_minutes': total_travel_time,
            'total_service_time_minutes': sum(b.service.duration_minutes for b in bookings),
            'optimization_suggestions': optimization_suggestions,
            'efficiency_score': self._calculate_efficiency_score(bookings, total_working_time, total_travel_time)
        }
    
    def _analyze_booking_efficiency(self, booking: Booking, previous_booking: Optional[Booking]) -> Optional[Dict]:
        """Analyze individual booking for efficiency improvements"""
        if not previous_booking:
            return None
        
        # Calculate actual gap between bookings
        prev_end = previous_booking.actual_end_time or (
            previous_booking.scheduled_date + timedelta(minutes=previous_booking.calculate_total_duration_minutes())
        )
        current_start = booking.actual_start_time or booking.scheduled_date
        
        gap_minutes = int((current_start - prev_end).total_seconds() / 60)
        
        # Check if there's excessive idle time
        if gap_minutes > 60:  # More than 1 hour gap
            return {
                'type': 'excessive_gap',
                'booking_id': str(booking.id),
                'gap_minutes': gap_minutes,
                'suggestion': f'Consider filling {gap_minutes} minute gap between bookings',
                'severity': 'medium' if gap_minutes > 120 else 'low'
            }
        
        # Check for inefficient travel routing
        if previous_booking.pincode and booking.pincode:
            travel_data = travel_service.get_travel_time(previous_booking.pincode, booking.pincode)
            actual_travel = booking.travel_time_to_location_minutes or 0
            
            if actual_travel > travel_data['duration_minutes'] * 1.5:  # 50% more than expected
                return {
                    'type': 'inefficient_routing',
                    'booking_id': str(booking.id),
                    'expected_travel': travel_data['duration_minutes'],
                    'actual_travel': actual_travel,
                    'suggestion': 'Route optimization needed',
                    'severity': 'high'
                }
        
        return None
    
    def _calculate_efficiency_score(self, bookings, total_working_time: int, total_travel_time: int) -> float:
        """Calculate efficiency score (0-100) for a day's schedule"""
        if total_working_time == 0:
            return 0.0
        
        total_service_time = sum(b.service.duration_minutes for b in bookings)
        
        # Efficiency = (service time / total working time) * 100
        # Penalize excessive travel time
        travel_penalty = min(20, (total_travel_time / total_working_time) * 100)
        
        efficiency = ((total_service_time / total_working_time) * 100) - travel_penalty
        
        return max(0, min(100, efficiency))
    
    def suggest_optimal_booking_time(self, vendor_id: int, service_id: int, customer_pincode: str,
                                   preferred_date: datetime.date) -> Optional[Dict]:
        """Suggest the most optimal booking time considering all factors"""
        available_slots = self.get_available_time_slots(
            vendor_id, service_id, customer_pincode, preferred_date, days_ahead=1
        )
        
        if not available_slots:
            return None
        
        # Score each slot based on multiple factors
        scored_slots = []
        for slot in available_slots:
            score = self._calculate_slot_score(slot)
            scored_slots.append({**slot, 'optimization_score': score})
        
        # Return the highest scored slot
        best_slot = max(scored_slots, key=lambda x: x['optimization_score'])
        return best_slot
    
    def _calculate_slot_score(self, slot: Dict) -> float:
        """Calculate optimization score for a time slot (0-100)"""
        score = 50  # Base score
        
        # Prefer shorter travel times
        travel_time = slot['travel_time_minutes']
        if travel_time <= 15:
            score += 20
        elif travel_time <= 30:
            score += 10
        elif travel_time <= 45:
            score += 5
        else:
            score -= 10
        
        # Prefer higher confidence travel data
        confidence = slot.get('confidence_score', 0.5)
        score += confidence * 15
        
        # Prefer times that don't require travel between distant locations
        next_travel = slot.get('next_travel_time_minutes', 0)
        if next_travel <= 15:
            score += 10
        elif next_travel > 45:
            score -= 10
        
        # Prefer morning/afternoon slots over evening
        hour = slot['start_time'].hour
        if 9 <= hour <= 11:  # Morning prime time
            score += 15
        elif 14 <= hour <= 16:  # Afternoon prime time
            score += 10
        elif hour >= 18:  # Evening
            score -= 5
        
        # Prefer non-traffic-adjusted slots (more predictable)
        if not slot.get('traffic_adjusted', False):
            score += 5
            
        return max(0, min(100, score))
    
    def reschedule_booking_for_eta_change(self, booking: Booking, new_eta_minutes: int) -> Dict:
        """
        Reschedule a booking when ETA changes significantly
        """
        try:
            # Calculate the difference
            current_travel_time = booking.travel_time_to_location_minutes or 0
            time_difference = new_eta_minutes - current_travel_time
            
            # Only reschedule if difference is significant (more than 30 minutes)
            if abs(time_difference) < 30:
                return {
                    'action': 'no_change',
                    'message': 'ETA change is minimal, no rescheduling needed'
                }
            
            # Get vendor availability
            vendor = booking.vendor
            if not vendor:
                return {
                    'action': 'error',
                    'message': 'No vendor assigned to this booking'
                }
            
            # Get vendor availability for the current day
            day_name = booking.scheduled_date.strftime('%A').lower()
            availability = VendorAvailability.objects.filter(
                vendor=vendor,
                day_of_week=day_name,
                is_active=True
            ).first()
            
            if not availability:
                return {
                    'action': 'error',
                    'message': 'No availability found for vendor on this day'
                }
            
            # Calculate new time slot
            if time_difference > 0:  # Delay - move booking later
                new_scheduled_time = booking.scheduled_date + timedelta(minutes=time_difference)
            else:  # Early - can potentially move booking earlier
                new_scheduled_time = max(
                    booking.scheduled_date + timedelta(minutes=time_difference),
                    booking.actual_start_time or booking.scheduled_date
                )
            
            # Update booking with new scheduled time
            booking.scheduled_date = new_scheduled_time
            booking.travel_time_to_location_minutes = new_eta_minutes
            booking.update_calculated_times()
            booking.save()
            
            return {
                'action': 'rescheduled',
                'message': f'Booking rescheduled due to ETA change of {time_difference} minutes',
                'new_scheduled_time': new_scheduled_time,
                'new_travel_time': new_eta_minutes
            }
            
        except Exception as e:
            logger.error(f"Error rescheduling booking {booking.id}: {str(e)}")
            return {
                'action': 'error',
                'message': f'Failed to reschedule booking: {str(e)}'
            }


# Singleton instance
scheduling_service = SmartSchedulingService()