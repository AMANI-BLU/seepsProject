# # signals.py
# import os
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Resource, Notification, User

# @receiver(post_save, sender=Resource)
# def send_resource_notification(sender, instance, created, **kwargs):
#     if created:  # Resource added
#         file_base_name = os.path.basename(instance.file.name)
#         message = f"Resource '{file_base_name}' with description '{instance.description}' added by {instance.added_by}"
        
#         department_name = instance.department_name
#         # Find all instructors in the department
#         instructors = User.objects.filter(department_name=department_name, is_instructor=True)
#         for instructor in instructors:
#             # Check if the same notification already exists for this resource and user
#             existing_notification = Notification.objects.filter(
#                 message=message,
#                 department=department_name,
#                 user=instructor,
#             ).first()
#             if not existing_notification:
#                 # Create a new notification if it doesn't already exist
#                 Notification.objects.create(
#                     message=message,
#                     department=department_name,
#                     user=instructor,
#                 )
