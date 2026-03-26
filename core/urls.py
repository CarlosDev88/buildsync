from django.contrib import admin
from django.urls import path, include
from strawberry.django.views import GraphQLView
from core.schema import schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    # GraphQL — vitrina pública (sin JWT requerido en este endpoint)
    # El GraphiQL playground queda disponible en /api/graphql/ desde el browser.
    path('api/graphql/', GraphQLView.as_view(schema=schema)),
]
