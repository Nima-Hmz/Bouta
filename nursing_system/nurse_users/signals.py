from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SubSkill, NurseSkills, NurseSubSkill

@receiver(post_save, sender=SubSkill)
def add_new_subskill_to_nurse(sender, instance, created, **kwargs):
    """
    When a new SubSkill is created, automatically add it to all nurses
    who already have the parent Skill.
    """
    if created:  # Only run if it's a new subskill
        nurse_skills = NurseSkills.objects.filter(skill=instance.skill)

        for nurse_skill in nurse_skills:
            NurseSubSkill.objects.get_or_create(
                nurse=nurse_skill.nurse,
                subskill=instance,
                nurse_skill=nurse_skill,
                defaults={'custom_price': instance.standard_price}
            )