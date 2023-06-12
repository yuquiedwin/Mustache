#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --noinput  # Ejecuta las migraciones
echo "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.create_superuser('admin', 'admin@example.com', 'password'); from .models import Customer; customer = Customer.objects.create(user=user, email='admin@example.com', name='Admin Customer')" | python manage.py shell
