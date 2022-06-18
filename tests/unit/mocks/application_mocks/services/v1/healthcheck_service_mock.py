"""
HealthCheck Service Mock for Application
Version: 1.0.0
"""
from unittest.mock import Mock

from application.services.v1.healthcheck import HealthCheckResponse
from application.services.v1.healthcheck_service import HealthCheckService

healthcheck_service_mock = Mock(HealthCheckService)
healthcheck_service_mock.get_response.side_effect = lambda: HealthCheckResponse().get_response()
