"""
App Component Test for Application
Version: 1.0.0
"""
import json
import os
import time
import unittest

import serverless_wsgi

import app
from application import APP_NAME, APP_VERSION
from application.config import get_config
from application.logging import get_logger
from application.repositories.v1.mysql.product_repository import ProductRepository
from tests.component.componenttestutils import BaseComponentTestCase
from tests.component.helpers.aws.sqs_helper import SQSHelper
from tests.unit.helpers.aws.sqs_helper import get_sqs_event_sample
from tests.unit.mocks.aws_mocks.aws_lambda_mock import FakeLambdaContext
from tests.unit.mocks.lambda_event_mocks.request_event import \
    create_aws_api_gateway_proxy_request_event
from tests.unit.testutils import get_function_name


def get_queue_message():
    queue_url = os.getenv("APP_QUEUE")

    message = get_sqs_event_sample()
    SQSHelper.create_message(message, queue_url)
    time.sleep(1)

    event = SQSHelper.get_message(queue_url)

    return (event,)


class AppTestCase(BaseComponentTestCase):
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

            # logger.info('Fixture: create sqs queue')
            # queue_url = cls.CONFIG.APP_QUEUE
            # cls.fixture_sqs(logger, queue_url)

    def test_index(self):
        self.logger.info('Running test: %s', get_function_name(__name__))

        event = create_aws_api_gateway_proxy_request_event('GET', '/')
        context = FakeLambdaContext()

        response = serverless_wsgi.handle_request(app.APP, event, context)

        self.assertTrue('statusCode' in response)
        self.assertTrue('body' in response)

        body = json.loads(response['body'])
        self.logger.info(body)

        self.assertTrue('app' in body)
        self.assertEqual(body['app'], "%s:%s" % (APP_NAME, APP_VERSION))

    def test_alive(self):
        self.logger.info('Running test: %s', get_function_name(__name__))

        event = create_aws_api_gateway_proxy_request_event('GET', '/alive')
        context = FakeLambdaContext()

        response = serverless_wsgi.handle_request(app.APP, event, context)

        self.assertTrue('statusCode' in response)
        self.assertTrue('body' in response)

        body = json.loads(response['body'])
        self.logger.info(body)

        self.assertTrue('status' in body)
        self.assertTrue('entries' in body)


if __name__ == '__main__':
    unittest.main()
