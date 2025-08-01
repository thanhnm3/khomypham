# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_add_purchase_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='expiry_days',
            field=models.IntegerField(blank=True, default=365, null=True, verbose_name='Số ngày hết hạn'),
        ),
    ]
