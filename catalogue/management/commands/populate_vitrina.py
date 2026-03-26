"""
Management command: populate_vitrina
Uso: python manage.py populate_vitrina

Crea 3 proyectos inmobiliarios colombianos realistas con 30+ unidades,
características EAV completas y puntos de interés. Idempotente: si ya
existen los proyectos por nombre, los salta sin duplicar.
"""
from django.core.management.base import BaseCommand
from catalogue.models import Project, Property, FeatureCatalog, PropertyFeature, POICategory, PointOfInterest


# ─── Definición de los 3 proyectos ───────────────────────────────────────────

PROJECTS = [
    {
        "name": "Reserva del Bosque",
        "status": "CONSTRUCTION",
        "location": "Calle 127 # 19-45, Usaquén, Bogotá",
        "is_demo": True,
        "units": [
            # Torre 1 — Pisos 2 al 7 (2 aptos por piso)
            {"name": "101", "tower": "Torre 1", "floor": 1, "type": "APARTMENT", "price": 285_000_000, "status": "SOLD",      "beds": 2, "baths": 2, "area": 58, "parking": 1, "storage": False, "balcony": True,  "stratum": 4, "view": "Interior"},
            {"name": "102", "tower": "Torre 1", "floor": 1, "type": "APARTMENT", "price": 295_000_000, "status": "SOLD",      "beds": 3, "baths": 2, "area": 72, "parking": 1, "storage": True,  "balcony": True,  "stratum": 4, "view": "Zona Verde"},
            {"name": "201", "tower": "Torre 1", "floor": 2, "type": "APARTMENT", "price": 299_000_000, "status": "RESERVED",  "beds": 2, "baths": 2, "area": 58, "parking": 1, "storage": False, "balcony": True,  "stratum": 4, "view": "Interior"},
            {"name": "202", "tower": "Torre 1", "floor": 2, "type": "APARTMENT", "price": 310_000_000, "status": "AVAILABLE", "beds": 3, "baths": 2, "area": 72, "parking": 1, "storage": True,  "balcony": True,  "stratum": 4, "view": "Zona Verde"},
            {"name": "301", "tower": "Torre 1", "floor": 3, "type": "APARTMENT", "price": 305_000_000, "status": "AVAILABLE", "beds": 2, "baths": 2, "area": 58, "parking": 1, "storage": False, "balcony": True,  "stratum": 4, "view": "Interior"},
            {"name": "302", "tower": "Torre 1", "floor": 3, "type": "APARTMENT", "price": 318_000_000, "status": "AVAILABLE", "beds": 3, "baths": 2, "area": 72, "parking": 2, "storage": True,  "balcony": True,  "stratum": 4, "view": "Montaña"},
            {"name": "401", "tower": "Torre 1", "floor": 4, "type": "APARTMENT", "price": 312_000_000, "status": "AVAILABLE", "beds": 2, "baths": 2, "area": 58, "parking": 1, "storage": False, "balcony": True,  "stratum": 4, "view": "Ciudad"},
            {"name": "402", "tower": "Torre 1", "floor": 4, "type": "APARTMENT", "price": 325_000_000, "status": "AVAILABLE", "beds": 3, "baths": 3, "area": 80, "parking": 2, "storage": True,  "balcony": True,  "stratum": 4, "view": "Montaña"},
            # Torre 2 — Pisos 1 al 5
            {"name": "101", "tower": "Torre 2", "floor": 1, "type": "APARTMENT", "price": 278_000_000, "status": "SOLD",      "beds": 2, "baths": 1, "area": 52, "parking": 1, "storage": False, "balcony": False, "stratum": 4, "view": "Parqueadero"},
            {"name": "102", "tower": "Torre 2", "floor": 1, "type": "APARTMENT", "price": 289_000_000, "status": "AVAILABLE", "beds": 3, "baths": 2, "area": 68, "parking": 1, "storage": False, "balcony": True,  "stratum": 4, "view": "Zona Verde"},
            {"name": "201", "tower": "Torre 2", "floor": 2, "type": "APARTMENT", "price": 290_000_000, "status": "AVAILABLE", "beds": 2, "baths": 2, "area": 56, "parking": 1, "storage": False, "balcony": False, "stratum": 4, "view": "Interior"},
            {"name": "202", "tower": "Torre 2", "floor": 2, "type": "APARTMENT", "price": 302_000_000, "status": "AVAILABLE", "beds": 3, "baths": 2, "area": 70, "parking": 1, "storage": True,  "balcony": True,  "stratum": 4, "view": "Zona Verde"},
        ],
        "pois": [
            {"cat": "Educación",     "name": "Colegio Anglo Colombiano",    "mode": "DRIVING",  "minutes": 8},
            {"cat": "Educación",     "name": "Universidad de los Andes",    "mode": "DRIVING",  "minutes": 20},
            {"cat": "Supermercados", "name": "Éxito Calle 127",             "mode": "WALKING",  "minutes": 7},
            {"cat": "Supermercados", "name": "Carulla Usaquén",             "mode": "DRIVING",  "minutes": 12},
            {"cat": "Transporte",    "name": "Estación TransMilenio Toberín","mode": "WALKING", "minutes": 15},
            {"cat": "Transporte",    "name": "Portal Norte",                "mode": "DRIVING",  "minutes": 10},
            {"cat": "Parques",       "name": "Parque de Usaquén",           "mode": "DRIVING",  "minutes": 14},
            {"cat": "Parques",       "name": "Humedal Torca-Guaymaral",     "mode": "BIKING",   "minutes": 20},
            {"cat": "Salud",         "name": "Clínica Reina Sofía",         "mode": "DRIVING",  "minutes": 11},
            {"cat": "Comercio",      "name": "Hacienda Santa Bárbara",      "mode": "DRIVING",  "minutes": 9},
        ],
    },
    {
        "name": "Villas del Norte",
        "status": "DELIVERED",
        "location": "Carrera 7 # 185-20, Vereda el Mochuelo, Chía, Cundinamarca",
        "is_demo": False,
        "units": [
            {"name": "Casa 1",  "tower": "Manzana A", "floor": 1, "type": "HOUSE", "price": 480_000_000, "status": "SOLD",      "beds": 3, "baths": 3, "area": 140, "parking": 2, "storage": True,  "balcony": False, "stratum": 5, "view": "Jardín"},
            {"name": "Casa 2",  "tower": "Manzana A", "floor": 1, "type": "HOUSE", "price": 495_000_000, "status": "SOLD",      "beds": 4, "baths": 3, "area": 160, "parking": 2, "storage": True,  "balcony": True,  "stratum": 5, "view": "Montaña"},
            {"name": "Casa 3",  "tower": "Manzana A", "floor": 1, "type": "HOUSE", "price": 520_000_000, "status": "SOLD",      "beds": 4, "baths": 4, "area": 185, "parking": 3, "storage": True,  "balcony": True,  "stratum": 5, "view": "Montaña"},
            {"name": "Casa 4",  "tower": "Manzana A", "floor": 1, "type": "HOUSE", "price": 460_000_000, "status": "DELIVERED", "beds": 3, "baths": 2, "area": 130, "parking": 2, "storage": False, "balcony": False, "stratum": 5, "view": "Jardín"},
            {"name": "Casa 5",  "tower": "Manzana A", "floor": 1, "type": "HOUSE", "price": 505_000_000, "status": "DELIVERED", "beds": 4, "baths": 3, "area": 168, "parking": 2, "storage": True,  "balcony": True,  "stratum": 5, "view": "Montaña"},
            {"name": "Casa 6",  "tower": "Manzana B", "floor": 1, "type": "HOUSE", "price": 545_000_000, "status": "SOLD",      "beds": 4, "baths": 4, "area": 200, "parking": 3, "storage": True,  "balcony": True,  "stratum": 5, "view": "Sabana"},
            {"name": "Casa 7",  "tower": "Manzana B", "floor": 1, "type": "HOUSE", "price": 498_000_000, "status": "DELIVERED", "beds": 3, "baths": 3, "area": 145, "parking": 2, "storage": True,  "balcony": False, "stratum": 5, "view": "Jardín"},
            {"name": "Casa 8",  "tower": "Manzana B", "floor": 1, "type": "HOUSE", "price": 580_000_000, "status": "SOLD",      "beds": 5, "baths": 4, "area": 220, "parking": 3, "storage": True,  "balcony": True,  "stratum": 5, "view": "Sabana"},
            {"name": "Casa 9",  "tower": "Manzana B", "floor": 1, "type": "HOUSE", "price": 472_000_000, "status": "AVAILABLE", "beds": 3, "baths": 3, "area": 138, "parking": 2, "storage": False, "balcony": False, "stratum": 5, "view": "Jardín"},
            {"name": "Casa 10", "tower": "Manzana B", "floor": 1, "type": "HOUSE", "price": 610_000_000, "status": "AVAILABLE", "beds": 5, "baths": 5, "area": 245, "parking": 4, "storage": True,  "balcony": True,  "stratum": 5, "view": "Sabana y Montaña"},
        ],
        "pois": [
            {"cat": "Educación",     "name": "Colegio Gimnasio La Montaña",  "mode": "DRIVING",  "minutes": 6},
            {"cat": "Educación",     "name": "Universidad de La Sabana",     "mode": "DRIVING",  "minutes": 12},
            {"cat": "Supermercados", "name": "Jumbo Chía",                   "mode": "DRIVING",  "minutes": 10},
            {"cat": "Supermercados", "name": "Éxito Chía",                   "mode": "DRIVING",  "minutes": 8},
            {"cat": "Transporte",    "name": "Terminal de Transporte Chía",  "mode": "DRIVING",  "minutes": 15},
            {"cat": "Parques",       "name": "Parque Principal de Chía",     "mode": "DRIVING",  "minutes": 12},
            {"cat": "Parques",       "name": "Sendero Ecológico Río Frío",   "mode": "BIKING",   "minutes": 18},
            {"cat": "Salud",         "name": "Clínica Universitaria Chía",   "mode": "DRIVING",  "minutes": 9},
            {"cat": "Comercio",      "name": "Centro Comercial Fontanar",    "mode": "DRIVING",  "minutes": 7},
            {"cat": "Comercio",      "name": "Centro Comercial Chia Plaza",  "mode": "DRIVING",  "minutes": 11},
        ],
    },
    {
        "name": "Plaza Empresarial 80",
        "status": "PLANNING",
        "location": "Avenida Calle 80 # 69B-50, Engativá, Bogotá",
        "is_demo": True,
        "units": [
            # Locales comerciales planta baja (alta afluencia)
            {"name": "Local 101", "tower": "Bloque Comercial", "floor": 1, "type": "COMMERCIAL", "price": 320_000_000, "status": "AVAILABLE", "beds": 0, "baths": 1, "area": 45,  "parking": 2, "storage": True,  "balcony": False, "stratum": 4, "view": "Av. 80"},
            {"name": "Local 102", "tower": "Bloque Comercial", "floor": 1, "type": "COMMERCIAL", "price": 350_000_000, "status": "RESERVED",  "beds": 0, "baths": 1, "area": 58,  "parking": 2, "storage": True,  "balcony": False, "stratum": 4, "view": "Av. 80"},
            {"name": "Local 103", "tower": "Bloque Comercial", "floor": 1, "type": "COMMERCIAL", "price": 290_000_000, "status": "AVAILABLE", "beds": 0, "baths": 1, "area": 38,  "parking": 1, "storage": False, "balcony": False, "stratum": 4, "view": "Interior"},
            {"name": "Local 104", "tower": "Bloque Comercial", "floor": 1, "type": "COMMERCIAL", "price": 410_000_000, "status": "AVAILABLE", "beds": 0, "baths": 2, "area": 75,  "parking": 3, "storage": True,  "balcony": False, "stratum": 4, "view": "Esquinero Av. 80"},
            {"name": "Local 105", "tower": "Bloque Comercial", "floor": 1, "type": "COMMERCIAL", "price": 275_000_000, "status": "AVAILABLE", "beds": 0, "baths": 1, "area": 32,  "parking": 1, "storage": False, "balcony": False, "stratum": 4, "view": "Interior"},
            # Oficinas piso 2
            {"name": "Ofc 201",   "tower": "Bloque Empresarial", "floor": 2, "type": "COMMERCIAL", "price": 245_000_000, "status": "AVAILABLE", "beds": 0, "baths": 2, "area": 55,  "parking": 2, "storage": False, "balcony": False, "stratum": 4, "view": "Ciudad"},
            {"name": "Ofc 202",   "tower": "Bloque Empresarial", "floor": 2, "type": "COMMERCIAL", "price": 260_000_000, "status": "AVAILABLE", "beds": 0, "baths": 2, "area": 62,  "parking": 2, "storage": False, "balcony": True,  "stratum": 4, "view": "Ciudad"},
            {"name": "Ofc 203",   "tower": "Bloque Empresarial", "floor": 2, "type": "COMMERCIAL", "price": 380_000_000, "status": "RESERVED",  "beds": 0, "baths": 3, "area": 98,  "parking": 3, "storage": True,  "balcony": True,  "stratum": 4, "view": "Ciudad Panorámica"},
            # Oficinas piso 3
            {"name": "Ofc 301",   "tower": "Bloque Empresarial", "floor": 3, "type": "COMMERCIAL", "price": 255_000_000, "status": "AVAILABLE", "beds": 0, "baths": 2, "area": 58,  "parking": 2, "storage": False, "balcony": False, "stratum": 4, "view": "Ciudad"},
            {"name": "Ofc 302",   "tower": "Bloque Empresarial", "floor": 3, "type": "COMMERCIAL", "price": 440_000_000, "status": "AVAILABLE", "beds": 0, "baths": 3, "area": 115, "parking": 4, "storage": True,  "balcony": True,  "stratum": 4, "view": "Ciudad Panorámica"},
        ],
        "pois": [
            {"cat": "Transporte",    "name": "Estación TM Av. 68",           "mode": "WALKING",  "minutes": 5},
            {"cat": "Transporte",    "name": "Estación TM Carrera 77",       "mode": "WALKING",  "minutes": 8},
            {"cat": "Transporte",    "name": "Portal 80",                    "mode": "TRANSIT",  "minutes": 12},
            {"cat": "Supermercados", "name": "Éxito Calle 80",               "mode": "WALKING",  "minutes": 6},
            {"cat": "Supermercados", "name": "D1 Engativá",                  "mode": "WALKING",  "minutes": 4},
            {"cat": "Educación",     "name": "Universidad El Bosque",        "mode": "DRIVING",  "minutes": 15},
            {"cat": "Salud",         "name": "Hospital de Engativá",         "mode": "DRIVING",  "minutes": 8},
            {"cat": "Salud",         "name": "Clínica Colsanitas Calle 80",  "mode": "DRIVING",  "minutes": 10},
            {"cat": "Comercio",      "name": "Centro Comercial Multiplaza",  "mode": "DRIVING",  "minutes": 7},
            {"cat": "Parques",       "name": "Parque El Salitre",            "mode": "BIKING",   "minutes": 22},
        ],
    },
]


class Command(BaseCommand):
    help = "Puebla la vitrina con 3 proyectos y 32 unidades realistas para Colombia."

    def handle(self, *args, **kwargs):
        self.stdout.write("─" * 60)
        self.stdout.write("Iniciando población de la vitrina...")
        self.stdout.write("─" * 60)

        feature_catalog = self._ensure_feature_catalog()
        poi_categories = self._ensure_poi_categories()

        total_units = 0
        for proj_data in PROJECTS:
            project, created = Project.objects.get_or_create(
                name=proj_data["name"],
                defaults={
                    "status": proj_data["status"],
                    "location": proj_data["location"],
                    "is_demo": proj_data["is_demo"],
                },
            )
            action = "Creado" if created else "Ya existe"
            self.stdout.write(f"\n[{action}] Proyecto: {project.name} ({project.status})")

            if created:
                units_created = self._create_units(project, proj_data["units"], feature_catalog)
                self._create_pois(project, proj_data["pois"], poi_categories)
                self.stdout.write(f"  ✓ {units_created} unidades creadas")
                self.stdout.write(f"  ✓ {len(proj_data['pois'])} puntos de interés creados")
                total_units += units_created
            else:
                count = project.properties.count()
                self.stdout.write(f"  → Ya tiene {count} unidades registradas, se omite.")

        self.stdout.write("\n" + "─" * 60)
        self.stdout.write(f"Finalizado. Total unidades nuevas: {total_units}")

    # ── helpers ───────────────────────────────────────────────────────────────

    def _ensure_feature_catalog(self):
        """Crea o recupera las características del catálogo EAV."""
        features_def = [
            ("Habitaciones",   "NUMBER"),
            ("Baños",          "NUMBER"),
            ("Área m²",        "NUMBER"),
            ("Parqueaderos",   "NUMBER"),
            ("Depósito",       "BOOLEAN"),
            ("Balcón",         "BOOLEAN"),
            ("Estrato",        "NUMBER"),
            ("Vista",          "TEXT"),
        ]
        catalog = {}
        for name, data_type in features_def:
            feat, _ = FeatureCatalog.objects.get_or_create(name=name, defaults={"data_type": data_type})
            catalog[name] = feat
        self.stdout.write(f"Catálogo EAV listo: {len(catalog)} características.")
        return catalog

    def _ensure_poi_categories(self):
        """Crea o recupera las categorías de puntos de interés."""
        cats_def = [
            ("Educación",     "school"),
            ("Supermercados", "shopping_cart"),
            ("Transporte",    "directions_bus"),
            ("Parques",       "park"),
            ("Salud",         "local_hospital"),
            ("Comercio",      "store"),
        ]
        categories = {}
        for name, icon in cats_def:
            cat, _ = POICategory.objects.get_or_create(name=name, defaults={"icon_identifier": icon})
            categories[name] = cat
        return categories

    def _create_units(self, project, units_data, feature_catalog):
        """Crea las unidades y sus características EAV para el proyecto."""
        count = 0
        for u in units_data:
            prop, created = Property.objects.get_or_create(
                project=project,
                property_name=u["name"],
                tower_or_block=u["tower"],
                defaults={
                    "property_type": u["type"],
                    "floor_number": u["floor"],
                    "base_price": u["price"],
                    "status": u["status"],
                },
            )
            if not created:
                continue

            # Asigna las características EAV
            feature_values = {
                "Habitaciones": str(u["beds"]),
                "Baños":        str(u["baths"]),
                "Área m²":      str(u["area"]),
                "Parqueaderos": str(u["parking"]),
                "Depósito":     "Sí" if u["storage"] else "No",
                "Balcón":       "Sí" if u["balcony"] else "No",
                "Estrato":      str(u["stratum"]),
                "Vista":        u["view"],
            }
            for feat_name, value in feature_values.items():
                PropertyFeature.objects.get_or_create(
                    property=prop,
                    feature=feature_catalog[feat_name],
                    defaults={"value": value},
                )
            count += 1
        return count

    def _create_pois(self, project, pois_data, poi_categories):
        """Crea los puntos de interés del proyecto."""
        for p in pois_data:
            PointOfInterest.objects.get_or_create(
                project=project,
                name=p["name"],
                defaults={
                    "category": poi_categories[p["cat"]],
                    "travel_mode": p["mode"],
                    "time_in_minutes": p["minutes"],
                },
            )
