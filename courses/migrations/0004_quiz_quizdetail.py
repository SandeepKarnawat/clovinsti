# Generated by Django 2.0.2 on 2018-03-04 07:17

import courses.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_lecturedetail'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1024)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to=courses.models.upload_image_path)),
                ('course_detail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.CourseDetail')),
            ],
        ),
        migrations.CreateModel(
            name='QuizDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=1024)),
                ('choices', models.TextField()),
                ('answer', models.CharField(max_length=16)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Quiz')),
            ],
        ),
    ]
