"""
Queries GraphQL del módulo Vitrina.

Todas las queries usan prefetch_related / select_related para evitar N+1.
El endpoint de vitrina es público (no requiere JWT) ya que es la cara visible
del catálogo de propiedades para cualquier visitante.
"""
import strawberry
from typing import Optional
from decimal import Decimal
from django.db.models import Count, Q

from catalogue.models import Project, Property
from .types import ProjectType, ProjectSummaryType, PropertyType


@strawberry.type
class VitrinaQuery:

    @strawberry.field(description="Lista de proyectos. Opcionalmente filtrada por estado.")
    def projects(
        self,
        status: Optional[str] = strawberry.UNSET,
        only_available: Optional[bool] = False,
    ) -> list[ProjectSummaryType]:
        """
        Devuelve la lista de proyectos como tarjetas (sin sus unidades internas).
        Incluye conteos de unidades totales y disponibles para mostrar en las cards.

        Filtros:
          status        → 'PLANNING' | 'CONSTRUCTION' | 'DELIVERED'
          only_available → si True, solo proyectos con al menos 1 unidad disponible
        """
        qs = Project.objects.annotate(
            total=Count("properties"),
            available=Count("properties", filter=Q(properties__status="AVAILABLE")),
        ).order_by("name")

        if status and status is not strawberry.UNSET:
            qs = qs.filter(status=status)

        if only_available:
            qs = qs.filter(available__gt=0)

        return [
            ProjectSummaryType.from_db(p, {"total": p.total, "available": p.available})
            for p in qs
        ]

    @strawberry.field(description="Detalle completo de un proyecto: unidades + puntos de interés.")
    def project(self, id: strawberry.ID) -> Optional[ProjectType]:
        """
        Retorna un proyecto con TODAS sus unidades y puntos de interés.
        Usa prefetch_related para resolver features y POIs en queries mínimas.
        """
        try:
            project = (
                Project.objects
                .prefetch_related(
                    "properties__features__feature",
                    "points_of_interest__category",
                )
                .get(id=id)
            )
            return ProjectType.from_db(project)
        except Project.DoesNotExist:
            return None

    @strawberry.field(description="Lista de unidades con filtros múltiples.")
    def properties(
        self,
        project_id: Optional[strawberry.ID] = strawberry.UNSET,
        status: Optional[str] = strawberry.UNSET,
        property_type: Optional[str] = strawberry.UNSET,
        min_price: Optional[Decimal] = strawberry.UNSET,
        max_price: Optional[Decimal] = strawberry.UNSET,
        min_area: Optional[int] = strawberry.UNSET,
        bedrooms: Optional[int] = strawberry.UNSET,
    ) -> list[PropertyType]:
        """
        Catálogo filtrable de unidades. Diseñado para el buscador de la vitrina.

        Filtros disponibles:
          project_id   → UUID del proyecto
          status       → 'AVAILABLE' | 'RESERVED' | 'SOLD' | 'BUILDING' | 'DELIVERED'
          property_type→ 'APARTMENT' | 'HOUSE' | 'COMMERCIAL' | 'RURAL_LOT'
          min_price    → precio base mínimo en pesos
          max_price    → precio base máximo en pesos
          min_area     → área mínima en m² (filtra por feature EAV)
          bedrooms     → número de habitaciones exacto (filtra por feature EAV)
        """
        qs = Property.objects.select_related("project").prefetch_related(
            "features__feature"
        )

        if project_id and project_id is not strawberry.UNSET:
            qs = qs.filter(project_id=project_id)

        if status and status is not strawberry.UNSET:
            qs = qs.filter(status=status)

        if property_type and property_type is not strawberry.UNSET:
            qs = qs.filter(property_type=property_type)

        if min_price and min_price is not strawberry.UNSET:
            qs = qs.filter(base_price__gte=min_price)

        if max_price and max_price is not strawberry.UNSET:
            qs = qs.filter(base_price__lte=max_price)

        # Filtros sobre features EAV
        if min_area and min_area is not strawberry.UNSET:
            qs = qs.filter(
                features__feature__name="Área m²",
                features__value__gte=str(min_area),
            )

        if bedrooms and bedrooms is not strawberry.UNSET:
            qs = qs.filter(
                features__feature__name="Habitaciones",
                features__value=str(bedrooms),
            )

        return [PropertyType.from_db(p) for p in qs.distinct()]

    @strawberry.field(description="Detalle completo de una unidad con todas sus características.")
    def property(self, id: strawberry.ID) -> Optional[PropertyType]:
        """
        Retorna una unidad con todos sus features EAV.
        """
        try:
            prop = (
                Property.objects
                .prefetch_related("features__feature")
                .select_related("project")
                .get(id=id)
            )
            return PropertyType.from_db(prop)
        except Property.DoesNotExist:
            return None
