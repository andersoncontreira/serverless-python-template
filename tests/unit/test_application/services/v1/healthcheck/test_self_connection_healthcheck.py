"""
Self HealthCheck Service Unit Test for Application
Version: 1.0.0
"""
import unittest

from application.config import get_config
from application.services.v1.healthcheck import HealthStatus, HealthCheckResult
from application.services.v1.healthcheck.resources import SelfConnectionHealthCheck
from tests.unit.mocks.http_mocks import http_client_mock
from tests.unit.testutils import get_function_name, BaseUnitTestCase


class SelfConnectionHealthCheckTestCase(BaseUnitTestCase):
    EXECUTE_FIXTURE = True
    CONFIG = None

    @classmethod
    def setUpClass(cls):
        BaseUnitTestCase.setUpClass()
        cls.CONFIG = get_config()

    def setUp(self):
        super().setUp()
        self.config = get_config()
        self.http_client = http_client_mock
        self.service = SelfConnectionHealthCheck(self.logger, self.config, self.http_client)

    def test_check_health(self):
        self.logger.info('Running test: %s', get_function_name(__name__))

        result = self.service.check_health()

        self.assertIsInstance(result, HealthCheckResult)
        self.assertEqual(result.status, HealthStatus.HEALTHY)


if __name__ == '__main__':
    unittest.main()
