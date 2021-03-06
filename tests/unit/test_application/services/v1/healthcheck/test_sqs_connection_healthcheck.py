"""
SQS HealthCheck Service Unit Test for Application
Version: 1.0.0
"""
import unittest

from application.config import get_config
from application.aws.sqs import SQS
from application.services.v1.healthcheck import HealthStatus, HealthCheckResult
from application.services.v1.healthcheck.resources import SQSConnectionHealthCheck
from tests.unit.mocks.boto3_mocks import session_mock
from tests.unit.testutils import get_function_name, BaseUnitTestCase


class SQSConnectionHealthCheckTestCase(BaseUnitTestCase):
    EXECUTE_FIXTURE = True
    CONFIG = None

    @classmethod
    def setUpClass(cls):
        BaseUnitTestCase.setUpClass()
        cls.CONFIG = get_config()

    def setUp(self):
        super().setUp()
        self.config = get_config()
        # mock dependencies
        self.sqs = SQS(logger=self.logger, config=self.config, profile="default", session=session_mock)
        self.service = SQSConnectionHealthCheck(self.logger, self.config, self.sqs)

    def test_check_health(self):
        self.logger.info('Running test: %s', get_function_name(__name__))

        result = self.service.check_health()
        self.logger.info(result.to_dict())

        self.assertIsInstance(result, HealthCheckResult)
        self.assertEqual(result.status, HealthStatus.HEALTHY)


if __name__ == '__main__':
    unittest.main()
