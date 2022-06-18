import unittest

from unittest_data_provider import data_provider
from tests.component.componenttestutils import BaseComponentTestCase
from tests.unit.helpers.product_helper import get_product_sample
from tests.unit.testutils import get_function_name

from application.config import get_config
from application.database.mysql import MySQLConnector
from application.logging import get_logger
from application.repositories.v1.mysql.product_repository import ProductRepository
from application.request_control import Pagination, Order
from application.vos.product import ProductVO



# def get_request():
#     request = ApiRequest()
#     request.offset = Pagination.OFFSET
#     request.limit = 2
#
#     request.where = {"random": random_string(10)}
#     return (request,),
#
#
# def get_event():
#     request = ApiRequest()
#     request.where = {"random": random_string(10)}
#     event_type = EventType.SALE_EVENT
#     event = EventVO(event_type, request)
#     event.hash = generate_hash(data=event.data)
#     return (event,),

def get_product():
    product_dict = get_product_sample()
    product_dict["id"] = None
    product = ProductVO(product_dict)

    return (product,),


def get_list_data():
    where = dict()
    offset = Pagination.OFFSET
    limit = Pagination.LIMIT
    fields = []
    sort_by = None
    order_by = None

    return (where, offset, limit, fields, sort_by, order_by), \
           (where, offset, limit, ['id', 'name'], sort_by, order_by), \
           (where, offset, limit, ['id', 'name'], sort_by, Order.DESC), \
           (
           {'uuid': 'fecfddd9-7cb8-413b-9de3-ec86de30a888'}, offset, limit, ['id', 'name'], sort_by,
           Order.DESC),


class ProductRepositoryTestCase(BaseComponentTestCase):
    EXECUTE_FIXTURE = False
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


    def setUp(self):
        super().setUp()
        self.connection = MySQLConnector().get_connection()
        self.repository = ProductRepository(mysql_connection=self.connection)
        self.repository.debug = True

    @data_provider(get_product)
    def test_create(self, product: ProductVO):
        self.logger.info('Running test: %s', get_function_name(__name__))

        result = self.repository.create(product)
        self.assertTrue(result)
        self.logger.info('Product created: {}'.format(product.id))

    @data_provider(get_product)
    def test_get(self, product: ProductVO):
        self.logger.info('Running test: %s', get_function_name(__name__))

        # change the values to create a new one
        product.name = product.name + ' V2'
        # valor para facilitar a tarefa do fixture
        product.uuid = "8374b976-a74e-475c-b78c-39717468926c"

        result = self.repository.create(product)

        response = self.repository.get(product.id)

        self.assertTrue(result)
        self.assertIsNotNone(response)

        response = self.repository.get(product.uuid, key='uuid')
        self.assertIsNotNone(response)

    @data_provider(get_list_data)
    def test_list(self, where, offset, limit, fields, sort_by, order_by):
        self.logger.info('Running test: %s', get_function_name(__name__))

        product = get_product()[0][0]
        self.repository.create(product)

        result = self.repository.list(where, offset, limit, fields, sort_by, order_by)
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

        self.logger.info('Product list count: {}'.format(len(result)))

    @data_provider(get_list_data)
    def test_count(self, where, offset, limit, fields, sort_by, order_by):
        self.logger.info('Running test: %s', get_function_name(__name__))

        result = self.repository.count(where, sort_by, order_by)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)

        self.logger.info('Product list count: {}'.format(result))

    # @data_provider(get_event)
    # def test_delete(self, event: EventVO):
    #     self.logger.info('Running test: %s', get_function_name(__name__))
    #
    #     event_type = event.type
    #     key = '%s:%s' % (event_type, event.hash)
    #
    #     config = get_config()
    #     connection = get_connection(config)
    #
    #     repository = EventRepository(redis_connection=connection)
    #
    #     with self.assertRaises(DatabaseException):
    #         repository.delete(key)
    #
    #     result = repository.create(key, event.to_json())
    #     self.assertTrue(result)
    #
    #     event.data = {**event.data, **{"updated": True}}
    #     result = repository.delete(key)
    #     self.assertTrue(result)
    #
    # @data_provider(get_event)
    # def test_update(self, event: EventVO):
    #     self.logger.info('Running test: %s', get_function_name(__name__))
    #
    #     event_type = event.type
    #     key = '%s:%s' % (event_type, event.hash)
    #
    #     config = get_config()
    #     connection = get_connection(config)
    #
    #     repository = EventRepository(redis_connection=connection)
    #
    #     with self.assertRaises(DatabaseException):
    #         repository.update(key, event.to_json())
    #
    #     result = repository.create(key, event.to_json())
    #     self.assertTrue(result)
    #
    #     event.data = {**event.data, **{"updated": True}}
    #     result = repository.update(key, event.to_json())
    #     self.assertTrue(result)


if __name__=='__main__':
    unittest.main()
