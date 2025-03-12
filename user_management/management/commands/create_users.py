import uuid
import random
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils.crypto import get_random_string

User = get_user_model()


class Command(BaseCommand):
    help = "Create users with role validation."

    def add_arguments(self, parser):
        """Add custom arguments to the command."""
        parser.add_argument(
            "--count", type=int, default=10, help="Number of users to create"
        )

    def handle(self, *args, **options):
        """Handle the command."""
        self.stdout.write(self.style.WARNING("Clearing existing user data..."))
        superuser = User.objects.filter(is_superuser=True).first()

        if superuser:
            deleted_count, _ = User.objects.exclude(user_id=superuser.user_id).delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {deleted_count} users, keeping the superuser."
                )
            )
        else:
            # If no superuser is found (which shouldn't happen normally), delete all users
            deleted_count, _ = User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted all users."))

        count = options["count"]
        roles = ["jobseeker", "employer"]

        existing_admin = User.objects.filter(role="admin").exists()
        if not existing_admin:
            self.create_admin()

        num_jobseekers = User.objects.filter(role="jobseeker").count()
        num_employers = User.objects.filter(role="employer").count()

        # if num_employers >= num_jobseekers:
        #     self.stdout.write(
        #         self.style.ERROR("There must be more jobseekers than employers!")
        #     )
        #     return

        created_users = []
        for _ in range(count):
            role = random.choice(roles)

            if role == "employer" and num_employers + 1 >= num_jobseekers:
                role = "jobseeker"

            user = self.create_user(role)
            if user:
                created_users.append(user)
                if role == "jobseeker":
                    num_jobseekers += 1
                else:
                    num_employers += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {len(created_users)} users - {num_employers} employers and {num_jobseekers} jobseekers!"
            )
        )

    def create_admin(self):
        """Create an admin user if one doesn't exist."""
        email = f"admin@{get_random_string(5)}.com"
        admin_user = User.objects.create(
            email=email,
            first_name="Admin",
            last_name="User",
            role="admin",
            password=make_password("Admin@1234"),
        )
        self.stdout.write(self.style.SUCCESS(f"Admin user created: {email}"))

    def create_user(self, role):
        """Create a user with validation."""
        email = f"user_{uuid.uuid4().hex[:6]}@example.com"
        password = make_password("User@1234")
        first_name = get_random_string(6).capitalize()
        last_name = get_random_string(6).capitalize()

        try:
            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(f"Created {role}: {email}"))
            return user
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f"Failed to create user: {e}"))
            return None
