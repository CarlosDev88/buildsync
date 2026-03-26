"""
Schema GraphQL raíz de PropSync.

Cada módulo expone su propio tipo Query que se fusiona aquí.
Al agregar nuevos módulos (CRM, LoanFlow, ERP) solo hay que
importar su Query y añadirlo a la lista de bases de RootQuery.
"""
import strawberry
from catalogue.graphql.queries import VitrinaQuery


@strawberry.type
class RootQuery(VitrinaQuery):
    """
    Punto de entrada único de la API GraphQL.
    Hereda todas las queries de cada módulo.
    """
    pass


schema = strawberry.Schema(query=RootQuery)
