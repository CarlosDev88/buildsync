from django.contrib import admin
from .models import Project, Property, FeatureCatalog, PropertyFeature, POICategory, PointOfInterest

# --- INLINES ---
class PropertyFeatureInline(admin.TabularInline):
    model = PropertyFeature
    extra = 1

class PointOfInterestInline(admin.TabularInline):
    model = PointOfInterest
    extra = 1  

# --- REGISTROS PRINCIPALES ---

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'is_demo', 'created_at')
    list_filter = ('status', 'is_demo')
    search_fields = ('name',)
    inlines = [PointOfInterestInline] 

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('property_name', 'project', 'property_type', 'base_price', 'status')
    list_filter = ('status', 'project', 'property_type')
    search_fields = ('property_name', 'tower_or_block')
    inlines = [PropertyFeatureInline] 

@admin.register(FeatureCatalog)
class FeatureCatalogAdmin(admin.ModelAdmin):
    list_display = ('name', 'data_type')

@admin.register(POICategory)
class POICategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_identifier')