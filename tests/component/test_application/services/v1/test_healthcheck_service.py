import unittest

from application.config import get_config
from application.database.mysql import MySQLConnector
from application.database.redis import RedisConnector
from application.logging import get_logger
from application.repositories.v1.mysql.product_repository import ProductRepository
from application.services.v1.healthcheck import HealthCheckResult
from application.services.v1.healthcheck.resources import MysqlConnectionHealthCheck, \
    RedisConnectionHealthCheck, \
    SelfConnectionHealthCheck
from application.services.v1.healthcheck_service import HealthCheckService
from tests.component.componenttestutils import BaseComponentTestCase
from tests.component.helpers.database.mysql_helper import MySQLHelper
from tests.unit.testutils import get_function_name


class HealthCheckServiceTestCase(BaseComponentTestCase):
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

            logger.info("Fixture: MYSQL Database connection")
            logger.info("Fixture: drop table")

            table_name = ProductRepository.BASE_TABLE
            cls.drop_table(logger, table_name)
            cls.fixture_table(logger, table_name)

            logger.info('Fixture: create sqs queue')

            queue_url = cls.CONFIG.APP_QUEUE
            cls.fixture_sqs(logger, queue_url)

    def setUp(self):
        super().setUp()
        self.config = get_config()
        self.mysql_connection = MySQLConnector().get_connection()
        self.redis_connection = RedisConnector().get_connection()
        self.service = HealthCheckService(self.logger, self.config)

    def test_add_check(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.service.add_check("MysqlConnection", MysqlConnectionHealthCheck(
            self.logger, self.config, self.mysql_connection), ["db"])

        result = self.service.get_result()
        self.logger.info(result)

        self.assertIsInstance(result, dict)
        self.assertTrue('status' in result)

    def test_add_lambda_check(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.service.add_check("Lambda test", lambda: HealthCheckResult.healthy("test success"), ["lambda_test"])

        result = self.service.get_result()
        self.logger.info(result)

        self.assertIsInstance(result, dict)
        self.assertTrue('status' in result)

    def test_add_multi_checks(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.service.add_check("self", SelfConnectionHealthCheck(self.logger, self.config), [])
        self.service.add_check("mysql", MysqlConnectionHealthCheck(
            self.logger, self.config, self.mysql_connection), ["db"])
        self.service.add_check("redis", RedisConnectionHealthCheck(
            self.logger, self.config, self.redis_connection), ["redis"])

        result = self.service.get_result()
        self.logger.info(result)

        self.assertIsInstance(result, dict)
        self.assertTrue('status' in result)

    def test_get_response(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.service.add_check("self", SelfConnectionHealthCheck(self.logger, self.config), [])
        self.service.add_check("mysql", MysqlConnectionHealthCheck(self.logger, self.config), ["db"])
        self.service.add_check("redis", RedisConnectionHealthCheck(self.logger, self.config), ["redis"])

        response = self.service.get_response()
        self.logger.info(response.data)
        self.assertIsNotNone(response.data)


if __name__ == '__main__':
    unittest.main()
