import unittest

from application.config import get_config
from application.logging import get_logger
from application.services.v1.healthcheck import HealthStatus, HealthCheckResult
from application.services.v1.healthcheck.resources import SelfConnectionHealthCheck
from tests.component.componenttestutils import BaseComponentTestCase
from tests.unit.testutils import get_function_name


class SelfConnectionHealthCheckTestCase(BaseComponentTestCase):
    EXECUTE_FIXTURE = True
    CONFIG = None

    @classmethod
    def setUpClass(cls):
        BaseComponentTestCase.setUpClass()
        cls.CONFIG = get_config()
        cls.CONFIG.SQS_ENDPOINT = cls.SQS_LOCALSTACK

        # fixture
        if cls.EXECUTE_FIXTURE:
            logger = get_logger()
            # logger.info('Fixture: create database')
            # todo a implementar

    def setUp(self):
        super().setUp()
        self.config = get_config()
        self.service = SelfConnectionHealthCheck(self.logger, self.config)

    def test_check_health(self):
        self.logger.info('Running test: %s', get_function_name(__name__))

        result = self.service.check_health()

        self.assertIsInstance(result, HealthCheckResult)
        self.assertEqual(result.status, HealthStatus.HEALTHY)


if __name__ == '__main__':
    unittest.main()
