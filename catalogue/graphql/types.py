"""
Tipos GraphQL del módulo Vitrina (catalogue).

Patrón usado: cada tipo wrappea la instancia Django via strawberry.Private
para evitar múltiples roundtrips a la DB. Los campos costosos (features, POIs)
se resuelven perezosamente y se benefician del prefetch_related del query raíz.
"""
import strawberry
from typing import Optional, Any
from decimal import Decimal


@strawberry.type
class FeatureType:
    """Característica EAV resuelta: nombre + tipo + valor para esta unidad."""
    name: str
    data_type: str
    value: str

    @classmethod
    def from_db(cls, property_feature) -> "FeatureType":
        return cls(
            name=property_feature.feature.name,
            data_type=property_feature.feature.data_type,
            value=property_feature.value,
        )


@strawberry.type
class POICategoryType:
    name: str
    icon_identifier: Optional[str]


@strawberry.type
class POIType:
    id: strawberry.ID
    name: str
    travel_mode: str
    travel_mode_display: str
    time_in_minutes: int
    category: POICategoryType

    @classmethod
    def from_db(cls, poi) -> "POIType":
        travel_labels = {
            "WALKING": "Caminando",
            "DRIVING": "Carro",
            "BIKING": "Bicicleta",
            "TRANSIT": "Transporte Público",
        }
        return cls(
            id=str(poi.id),
            name=poi.name,
            travel_mode=poi.travel_mode,
            travel_mode_display=travel_labels.get(poi.travel_mode, poi.travel_mode),
            time_in_minutes=poi.time_in_minutes,
            category=POICategoryType(
                name=poi.category.name,
                icon_identifier=poi.category.icon_identifier,
            ),
        )


@strawberry.type
class PropertyType:
    id: strawberry.ID
    property_name: str
    property_type: str
    property_type_display: str
    tower_or_block: Optional[str]
    floor_number: Optional[int]
    base_price: Decimal
    status: str
    status_display: str
    features: list[FeatureType]

    @classmethod
    def from_db(cls, prop) -> "PropertyType":
        type_labels = {
            "APARTMENT": "Apartamento",
            "HOUSE": "Casa",
            "COMMERCIAL": "Local Comercial",
            "RURAL_LOT": "Lote Campestre",
        }
        status_labels = {
            "AVAILABLE": "Disponible",
            "RESERVED": "Reservado",
            "SOLD": "Vendido",
            "BUILDING": "En Construcción",
            "DELIVERED": "Entregado",
        }
        # features usa prefetch_related('features__feature') del query raíz
        features = [
            FeatureType.from_db(pf)
            for pf in prop.features.all()
        ]
        return cls(
            id=str(prop.id),
            property_name=prop.property_name,
            property_type=prop.property_type,
            property_type_display=type_labels.get(prop.property_type, prop.property_type),
            tower_or_block=prop.tower_or_block,
            floor_number=prop.floor_number,
            base_price=prop.base_price,
            status=prop.status,
            status_display=status_labels.get(prop.status, prop.status),
            features=features,
        )


@strawberry.type
class ProjectType:
    id: strawberry.ID
    name: str
    status: str
    status_display: str
    location: Optional[str]
    is_demo: bool
    total_units: int
    available_units: int
    properties: list[PropertyType]
    points_of_interest: list[POIType]

    @classmethod
    def from_db(cls, project) -> "ProjectType":
        status_labels = {
            "PLANNING": "En Planos",
            "CONSTRUCTION": "En Construcción",
            "DELIVERED": "Entregado",
        }
        # Ambas relaciones vienen prefetcheadas desde el resolver raíz
        all_props = list(project.properties.all())
        return cls(
            id=str(project.id),
            name=project.name,
            status=project.status,
            status_display=status_labels.get(project.status, project.status),
            location=project.location,
            is_demo=project.is_demo,
            total_units=len(all_props),
            available_units=sum(1 for p in all_props if p.status == "AVAILABLE"),
            properties=[PropertyType.from_db(p) for p in all_props],
            points_of_interest=[POIType.from_db(poi) for poi in project.points_of_interest.all()],
        )


@strawberry.type
class ProjectSummaryType:
    """Versión ligera de proyecto sin sus unidades. Para listas/cards."""
    id: strawberry.ID
    name: str
    status: str
    status_display: str
    location: Optional[str]
    is_demo: bool
    total_units: int
    available_units: int

    @classmethod
    def from_db(cls, project, counts: dict) -> "ProjectSummaryType":
        status_labels = {
            "PLANNING": "En Planos",
            "CONSTRUCTION": "En Construcción",
            "DELIVERED": "Entregado",
        }
        return cls(
            id=str(project.id),
            name=project.name,
            status=project.status,
            status_display=status_labels.get(project.status, project.status),
            location=project.location,
            is_demo=project.is_demo,
            total_units=counts.get("total", 0),
            available_units=counts.get("available", 0),
        )
