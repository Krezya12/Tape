from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, TextField, BooleanField, DateTimeField, ForeignKey, TextChoices, Model, \
    ImageField, BigIntegerField, ManyToManyField, FileField, DateField, IntegerField, CASCADE, PROTECT, \
    OneToOneField, DecimalField
from django.utils import timezone


class User(AbstractUser):
    class Role(TextChoices):
        ADMIN = "ADMIN", "Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"
        PARENT = "PARENT", "Parent"

    role = CharField(
        max_length=20,
        choices=Role,
        default=Role.STUDENT
    )

    phone = CharField(
        max_length=20,
        blank=True,
        null=True
    )

    avatar = ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    telegram_id = BigIntegerField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.username} - {self.role}"


class ParentStudent(Model):
    parent = ForeignKey(
        User,
        related_name="children",
        on_delete=CASCADE,
        limit_choices_to={
            "role": User.Role.PARENT
        }
    )

    student = ForeignKey(
        User,
        related_name="parents",
        on_delete=CASCADE,
        limit_choices_to={
            "role": User.Role.STUDENT
        }
    )

    created_at = DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "parent",
            "student"
        )

    def __str__(self):
        return f"{self.parent} -> {self.student}"


class Module(Model):

    class TechType(TextChoices):
        PYTHON = "PYTHON", "python"
        JAVA = "JAVA", "java"

    number = IntegerField(
        unique=True
    )

    technology = CharField(
        max_length=20,
        choices=TechType,
        default=TechType.PYTHON
    )


    price = DecimalField(
        max_digits=10,
        decimal_places=2
    )

    description = TextField(
        blank=True
    )

    def __str__(self):
        return f"Module {self.number}"


class Group(Model):
    class TechType(TextChoices):
        PYTHON = "PYTHON", "python"
        JAVA = "JAVA", "java"

    title = CharField(
        max_length=50,
        unique=True,
        blank=True, null=True
    )

    technology = CharField(
        max_length=20,
        choices=TechType,
        default=TechType.PYTHON
    )

    current_module = ForeignKey(
        Module,
        on_delete=PROTECT, blank=True, null=True
    )

    created_at = DateTimeField(
        auto_now_add=True
    )

    active = BooleanField(
        default=True
    )

    def get_current_lesson(self):

        return self.lessons.filter(
            date=timezone.now().date()
        ).first()

    def __str__(self):
        return self.title


class GroupModuleTeacher(Model):
    group = ForeignKey(
        Group,
        on_delete=CASCADE,
        related_name="module_teachers"
    )

    module = ForeignKey(
        Module,
        on_delete=PROTECT
    )

    teacher = ForeignKey(
        User,
        on_delete=PROTECT,
        limit_choices_to={
            "role": User.Role.TEACHER
        }
    )

    started_at = DateField(
        auto_now_add=True
    )

    finished_at = DateField(
        blank=True,
        null=True
    )

    class Meta:
        unique_together = (
            "group",
            "module",
        )

    def __str__(self):
        return (
            f"{self.group} - "
            f"{self.module} - "
            f"{self.teacher}"
        )


class GroupStudent(Model):
    student = ForeignKey('User', on_delete=CASCADE, related_name='student_groups')
    group = ForeignKey('Group', on_delete=CASCADE, related_name='student_groups')


class Lesson(Model):
    group = ForeignKey(
        Group,
        on_delete=CASCADE,
        related_name="lessons"
    )

    number = IntegerField()

    date = DateField()

    topic = CharField(
        max_length=255,
        blank=True,
        null=True
    )

    homework = TextField(
        blank=True,
        null=True
    )

    material_file = FileField(
        upload_to="lesson_materials/",
        blank=True,
        null=True
    )

    cancelled = BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.group} - Lesson {self.number}"


class Exam(Model):
    group = ForeignKey(
        Group,
        on_delete=CASCADE
    )

    module = ForeignKey(
        Module,
        on_delete=PROTECT
    )

    date = DateField()

    passing_score = IntegerField(
        default=60
    )

    def __str__(self):
        return f"{self.group} exam"


class StudentModuleProgress(Model):
    student = ForeignKey(
        User,
        on_delete=CASCADE
    )

    module = ForeignKey(
        Module,
        on_delete=PROTECT
    )

    exam_score = IntegerField(
        default=0
    )

    passed = BooleanField(
        default=False
    )

    completed_at = DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.student} - {self.module}"


# ==========================
# GRADES
# ==========================

class Grade(Model):
    student = ForeignKey(
        User,
        on_delete=CASCADE
    )

    lesson = ForeignKey(
        Lesson,
        on_delete=CASCADE
    )

    homework_points = IntegerField(
        default=0
    )

    classwork_points = IntegerField(
        default=0
    )

    teacher_comment = TextField(
        blank=True
    )

    created_at = DateTimeField(
        auto_now_add=True
    )

    @property
    def total_points(self):
        return (
                self.homework_points +
                self.classwork_points
        )

    def __str__(self):
        return f"{self.student} - {self.total_points}"


class Attendance(Model):
    class Status(TextChoices):
        PRESENT = "present", "Present"

        ABSENT = "absent", "Absent"

    student = ForeignKey(
        User,
        on_delete=CASCADE
    )

    lesson = ForeignKey(Lesson, on_delete=CASCADE, related_name='attendance')

    status = CharField(max_length=10, choices=Status, default=Status.ABSENT)


class Payment(Model):
    student = ForeignKey(
        User,
        on_delete=CASCADE
    )

    module = ForeignKey(
        Module,
        on_delete=PROTECT
    )

    paid = BooleanField(
        default=False
    )

    paid_date = DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.student} - {self.module}"


class TeacherSettings(Model):
    teacher = OneToOneField(
        User,
        on_delete=CASCADE
    )

    hide_student_avatars = BooleanField(
        default=False
    )

    hide_group_ratings = BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.teacher} settings"


class Notification(Model):
    user = ForeignKey(User, on_delete=CASCADE)

    title = CharField(max_length=255)

    message = TextField()

    is_read = BooleanField(default=False)

    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
