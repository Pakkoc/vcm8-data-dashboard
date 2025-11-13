from django.db import models


# ============= Core Entities =============

class College(models.Model):
    """단과대학 정보"""
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'colleges'
        verbose_name = 'College'
        verbose_name_plural = 'Colleges'

    def __str__(self):
        return self.name


class Department(models.Model):
    """학과 정보"""
    id = models.BigAutoField(primary_key=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        unique_together = [['college', 'name']]
        indexes = [
            models.Index(fields=['college']),
        ]

    def __str__(self):
        return f"{self.college.name} - {self.name}"


# ============= Enum Choices =============

class AcademicProgram(models.TextChoices):
    BACHELOR = '학사', '학사'
    MASTER = '석사', '석사'
    DOCTORAL = '박사', '박사'


class AcademicStatus(models.TextChoices):
    ENROLLED = '재학', '재학'
    LEAVE = '휴학', '휴학'
    GRADUATED = '졸업', '졸업'


class ProjectStatus(models.TextChoices):
    PROCESSING = '처리중', '처리중'
    COMPLETED = '집행완료', '집행완료'
    REJECTED = '반려', '반려'


# ============= Data Models =============

class Student(models.Model):
    """학생 명단"""
    id = models.BigAutoField(primary_key=True)
    student_id_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.RESTRICT, related_name='students')
    grade = models.SmallIntegerField(null=True, blank=True)
    program_level = models.CharField(max_length=10, choices=AcademicProgram.choices)
    status = models.CharField(max_length=10, choices=AcademicStatus.choices)
    gender = models.CharField(max_length=1, null=True, blank=True)
    admission_year = models.IntegerField(null=True, blank=True)
    advisor_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.student_id_number} - {self.name}"


class DepartmentKPI(models.Model):
    """학과별 핵심 성과 지표"""
    id = models.BigAutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='kpis')
    evaluation_year = models.IntegerField()
    employment_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    full_time_faculty_count = models.IntegerField(null=True, blank=True)
    visiting_faculty_count = models.IntegerField(null=True, blank=True)
    tech_transfer_income = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    international_conferences_count = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'department_kpis'
        verbose_name = 'Department KPI'
        verbose_name_plural = 'Department KPIs'
        unique_together = [['department', 'evaluation_year']]
        indexes = [
            models.Index(fields=['department', 'evaluation_year']),
        ]

    def __str__(self):
        return f"{self.department.name} - {self.evaluation_year}"


class Publication(models.Model):
    """논문 목록"""
    id = models.BigAutoField(primary_key=True)
    publication_id_str = models.CharField(max_length=100, unique=True, null=True, blank=True)
    publication_date = models.DateField()
    department = models.ForeignKey(
        Department, on_delete=models.RESTRICT, related_name='publications'
    )
    title = models.TextField()
    primary_author = models.CharField(max_length=100, null=True, blank=True)
    contributing_authors = models.TextField(null=True, blank=True)
    journal_name = models.TextField(null=True, blank=True)
    journal_rank = models.CharField(max_length=50, null=True, blank=True)
    impact_factor = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    is_project_linked = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'publications'
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['publication_date']),
        ]

    def __str__(self):
        return f"{self.publication_id_str} - {self.title[:50]}"


class ResearchProject(models.Model):
    """연구 과제 정보"""
    id = models.BigAutoField(primary_key=True)
    project_number = models.CharField(max_length=100, unique=True)
    name = models.TextField()
    principal_investigator = models.CharField(max_length=100, null=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.RESTRICT, related_name='research_projects'
    )
    funding_agency = models.CharField(max_length=255, null=True, blank=True)
    total_funding_amount = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'research_projects'
        verbose_name = 'Research Project'
        verbose_name_plural = 'Research Projects'
        indexes = [
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"{self.project_number} - {self.name[:50]}"


class ProjectExpense(models.Model):
    """연구 과제 집행 내역"""
    id = models.BigAutoField(primary_key=True)
    execution_id = models.CharField(max_length=100, unique=True)
    project = models.ForeignKey(
        ResearchProject, on_delete=models.CASCADE, related_name='expenses'
    )
    execution_date = models.DateField()
    item = models.CharField(max_length=255)
    amount = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=ProjectStatus.choices)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_expenses'
        verbose_name = 'Project Expense'
        verbose_name_plural = 'Project Expenses'
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.execution_id} - {self.item}"
