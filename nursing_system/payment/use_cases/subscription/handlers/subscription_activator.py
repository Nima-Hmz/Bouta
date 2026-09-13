from nurse_users.models import Subscription
from django.utils.timezone import now
from datetime import timedelta

class SubscriptionActivator:
    def __init__(self, nurse, plan):
        self.nurse = nurse
        self.plan = plan

    def execute(self):
        try:
            self.nurse_subscription = Subscription.objects.get(nurse_user=self.nurse)
            self._update_sub()
        except Subscription.DoesNotExist:
            self.nurse_subscription = Subscription.objects.create(nurse_user=self.nurse, plan=self.plan, \
                                                                  status=True)
        except Exception:
            raise Exception("خطا در به روز رسانی اشتراک (با پشتیبانی تماس بگیرید)")
        
            
    def _update_sub(self):
        now = now().date()
        end = now + timedelta(days=self.plan.duration_days)

        self.nurse_subscription.start_date = now
        self.nurse_subscription.end_date = end
        self.nurse_subscription.start_date_j = now
        self.nurse_subscription.end_date_j= end

        self.nurse_subscription.save(update_fields=["start_date", "start_date_j", "end_date", "end_date_j"])
