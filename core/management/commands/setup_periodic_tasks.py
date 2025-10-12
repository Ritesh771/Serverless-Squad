"""
Django management command to set up Celery periodic tasks for automated messaging
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set up Celery Beat periodic tasks for automated messaging and business alerts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what tasks would be created without actually creating them',
        )

    def handle(self, *args, **options):
        try:
            from django_celery_beat.models import PeriodicTask, CrontabSchedule
            from django.utils import timezone
            
            self.stdout.write(self.style.SUCCESS('Setting up periodic tasks...'))
            
            # Define the tasks to be scheduled
            periodic_tasks = [
                {
                    'name': 'Generate Pincode Analytics',
                    'task': 'core.tasks.generate_pincode_analytics',
                    'schedule': {'hour': 1, 'minute': 0},  # Daily at 1:00 AM
                    'description': 'Generate daily analytics data for all pincodes'
                },
                {
                    'name': 'Send Pincode Demand Alerts',
                    'task': 'core.tasks.send_pincode_demand_alerts',
                    'schedule': {'hour': 9, 'minute': 0},  # Daily at 9:00 AM
                    'description': 'Send high-demand alerts to vendors'
                },
                {
                    'name': 'Send Vendor Bonus Alerts',
                    'task': 'core.tasks.send_vendor_bonus_alerts',
                    'schedule': {'hour': 10, 'minute': 0},  # Daily at 10:00 AM
                    'description': 'Send bonus alerts for high-demand areas'
                },
                {
                    'name': 'Send Promotional Campaigns',
                    'task': 'core.tasks.send_promotional_campaigns',
                    'schedule': {'hour': 11, 'minute': 0, 'day_of_week': '1,3,5'},  # Mon, Wed, Fri at 11:00 AM
                    'description': 'Send promotional campaigns to low-activity areas'
                },
                {
                    'name': 'Check Pending Signatures',
                    'task': 'core.tasks.check_pending_signatures',
                    'schedule': {'hour': '*', 'minute': 0},  # Every hour
                    'description': 'Check for signatures pending more than 24 hours'
                },
                {
                    'name': 'Check Payment Holds',
                    'task': 'core.tasks.check_payment_holds',
                    'schedule': {'hour': '*/2', 'minute': 0},  # Every 2 hours
                    'description': 'Check for payments stuck in escrow'
                },
                {
                    'name': 'Check Booking Timeouts',
                    'task': 'core.tasks.check_booking_timeouts',
                    'schedule': {'hour': '*/3', 'minute': 0},  # Every 3 hours
                    'description': 'Check for overdue bookings'
                },
                {
                    'name': 'Send Vendor Completion Reminders',
                    'task': 'core.tasks.send_vendor_completion_reminders',
                    'schedule': {'hour': '8,14,18', 'minute': 0},  # 8 AM, 2 PM, 6 PM
                    'description': 'Send completion reminders to vendors'
                },
                {
                    'name': 'Cleanup Old Notifications',
                    'task': 'core.tasks.cleanup_old_notifications',
                    'schedule': {'hour': 2, 'minute': 0, 'day_of_week': '0'},  # Weekly on Sunday at 2:00 AM
                    'description': 'Clean up old notification logs and business alerts'
                },
            ]
            
            created_count = 0
            updated_count = 0
            
            for task_config in periodic_tasks:
                try:
                    # Create or get the cron schedule
                    schedule, schedule_created = CrontabSchedule.objects.get_or_create(
                        **task_config['schedule']
                    )
                    
                    if options['dry_run']:
                        self.stdout.write(f"Would create/update task: {task_config['name']}")
                        continue
                    
                    # Create or update the periodic task
                    periodic_task, task_created = PeriodicTask.objects.update_or_create(
                        name=task_config['name'],
                        defaults={
                            'task': task_config['task'],
                            'crontab': schedule,
                            'enabled': True,
                            'description': task_config['description'],
                        }
                    )
                    
                    if task_created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Created task: {task_config['name']}")
                        )
                    else:
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f"↻ Updated task: {task_config['name']}")
                        )
                    
                except Exception as task_error:
                    self.stdout.write(
                        self.style.ERROR(f"✗ Error setting up task {task_config['name']}: {str(task_error)}")
                    )
                    continue
            
            if options['dry_run']:
                self.stdout.write(
                    self.style.SUCCESS(f"Dry run complete. {len(periodic_tasks)} tasks would be processed.")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Periodic tasks setup complete! "
                        f"Created: {created_count}, Updated: {updated_count}"
                    )
                )
                
                # Provide next steps
                self.stdout.write("\n" + "="*50)
                self.stdout.write(self.style.SUCCESS("Next Steps:"))
                self.stdout.write("1. Start Celery worker: celery -A homeserve_pro worker --loglevel=info")
                self.stdout.write("2. Start Celery beat: celery -A homeserve_pro beat --loglevel=info")
                self.stdout.write("3. Monitor tasks in Django Admin > Periodic Tasks")
                
        except ImportError:
            self.stdout.write(
                self.style.ERROR(
                    "django-celery-beat is not installed. "
                    "Please install it: pip install django-celery-beat"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error setting up periodic tasks: {str(e)}")
            )
            logger.error(f"Error in setup_periodic_tasks command: {str(e)}")