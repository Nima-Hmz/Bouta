from nurse_users.models import Subscription
from django.utils.timezone import now
from datetime import timedelta

class SubscriptionDeactivator:
    def __init__(self, nurse, plan):
        self.nurse = nurse
        self.plan = plan

    def execute(self):
        try:
            self.nurse_subscription = Subscription.objects.get(nurse_user=self.nurse)
            self._deactivate_sub()
        except Subscription.DoesNotExist:
            raise Exception("اشتراکی برای حذف کردن وجود ندارد")
        except Exception:
            raise Exception("خطا دوباره تلاش کنید")
        
    def _deactivate_sub(self):
        self.nurse_subscription.start_date = now().date()
        self.nurse_subscription.end_date = now().date()
        self.nurse_subscription.start_date_j = now().date()
        self.nurse_subscription.end_date_j = now().date()

        self.nurse_subscription.save(update_fields=["start_date", "start_date_j", "end_date", "end_date_j"])
