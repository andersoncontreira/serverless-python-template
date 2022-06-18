"""
SQS Unit Test for Application
Version: 1.0.0
"""
import unittest

from unittest_data_provider import data_provider

from application.config import get_config
from application.aws.sqs import SQS
from tests.unit.mocks.boto3_mocks import session_mock
from tests.unit.testutils import get_function_name, BaseUnitTestCase
from tests.unit.helpers.aws.sqs_helper import get_sqs_event_sample as sample


def get_sqs_event_sample():
    event = sample()
    return (event,),


class SQSTestCase(BaseUnitTestCase):
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

    def test_connect(self):
        self.logger.info('Running test: %s', get_function_name(__name__))

        connection = self.sqs.connect()
        self.assertIsNotNone(connection)

    @data_provider(get_sqs_event_sample)
    def test_send_message(self, message):
        self.logger.info('Running test: %s', get_function_name(__name__))
        queue_url = self.CONFIG.APP_QUEUE
        # return mock response
        response = self.sqs.send_message(message, queue_url)

        self.logger.info(response)

        self.assertIsNotNone(response)
        self.assertIsInstance(response, dict)
        self.assertTrue('MD5OfMessageBody' in response)
        self.assertTrue('MessageId' in response)


if __name__ == '__main__':
    unittest.main()
