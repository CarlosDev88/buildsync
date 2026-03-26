from django.apps import AppConfig


class LoanflowConfig(AppConfig):
    name = 'loanflow'

    def ready(self):
        import loanflow.signals  # noqa: F401 — registra los receivers al arrancar Django
