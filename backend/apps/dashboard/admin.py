from django.contrib import admin
from .models import (
    College,
    Department,
    Student,
    DepartmentKPI,
    Publication,
    ResearchProject,
    ProjectExpense,
)


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'college', 'created_at']
    list_filter = ['college']
    search_fields = ['name', 'college__name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id_number', 'name', 'department', 'program_level', 'status']
    list_filter = ['status', 'program_level', 'department__college']
    search_fields = ['student_id_number', 'name', 'email']


@admin.register(DepartmentKPI)
class DepartmentKPIAdmin(admin.ModelAdmin):
    list_display = ['department', 'evaluation_year', 'employment_rate', 'full_time_faculty_count']
    list_filter = ['evaluation_year', 'department__college']
    search_fields = ['department__name']


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['publication_id_str', 'title', 'department', 'publication_date', 'primary_author']
    list_filter = ['publication_date', 'department__college']
    search_fields = ['title', 'primary_author', 'publication_id_str']


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ['project_number', 'name', 'department', 'principal_investigator', 'total_funding_amount']
    list_filter = ['department__college']
    search_fields = ['project_number', 'name', 'principal_investigator']


@admin.register(ProjectExpense)
class ProjectExpenseAdmin(admin.ModelAdmin):
    list_display = ['execution_id', 'project', 'item', 'amount', 'status', 'execution_date']
    list_filter = ['status', 'execution_date']
    search_fields = ['execution_id', 'item', 'project__project_number']
