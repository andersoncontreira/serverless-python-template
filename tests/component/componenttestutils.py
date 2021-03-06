import logging
import os
import unittest
import warnings

from sqlalchemy import Table, MetaData, create_engine, Column

from application import helper
from application.migrations import models
from application.database.mysql import get_uri, run_compatible_with_sqlalchemy
from boot import reset, load_dot_env, load_env
from application.config import reset as reset_config, get_config
from tests import ROOT_DIR
from tests.component.helpers.aws.sqs_helper import SQSHelper
from tests.component.helpers.database.mysql_helper import MySQLHelper


class BaseComponentTestCase(unittest.TestCase):
    """
    Classe base para testes de componentes
    """
    SQS_LOCALSTACK = 'http://localhost:4566'
    REDIS_LOCALSTACK = 'localhost'
    CONFIG = None
    LOGGER = None

    @classmethod
    def setUpClass(cls):
        # pass
        # reset config and env
        reset()
        reset_config()
        # load integration
        APP_TYPE = os.environ['APP_TYPE']
        if APP_TYPE=='Flask':
            load_dot_env()
        else:
            load_env()

        cls.CONFIG = get_config()
        cls.setUpLogger()

        # run_compatible_with_sqlalchemy
        run_compatible_with_sqlalchemy()

    @classmethod
    def setUpLogger(cls):
        log_name = 'component_test'
        log_filename = None
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=log_format, filename=log_filename, level=logging.DEBUG)
        cls.LOGGER = logging.getLogger(log_name)

    def setUp(self):
        self.logger = self.LOGGER

        # ignora falso positivos
        # https://github.com/boto/boto3/issues/454
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")

        # reset config and env
        reset()
        reset_config()
        # load integration
        APP_TYPE = os.environ['APP_TYPE']
        if APP_TYPE=='Flask':
            load_dot_env()
        else:
            load_env()
        self.config = get_config()

    @classmethod
    def fixture_sqs(cls, logger, queue_url, attributes=None):
        queue_name = SQSHelper.get_queue_name(queue_url)
        deleted = SQSHelper.delete_queue(queue_url)
        if deleted:
            logger.info(f'Deleting queue name: {queue_name}')

        if attributes is None:
            attributes = {'DelaySeconds': '0'}
        result = SQSHelper.create_queue(queue_url, attributes)
        if result is not None:
            logger.info(f'queue {queue_name} created')
        else:
            logger.error(f'queue {queue_name} not created')

    @classmethod
    def fixture_table(cls, logger, table_name):
        URI = get_uri(cls.CONFIG)
        engine = create_engine(URI)
        created = False
        populated = False

        if not table_name in models.REFERENCES.keys():
            raise Exception('{} not in models.REFERENCES.keys'.format(table_name))

        if not engine.dialect.has_table(engine.connect(), table_name):
            metadata = MetaData(engine)

            obj = models.REFERENCES[table_name]
            args = [x for x in obj.__dict__.values() if type(x)==Column]
            try:
                # Create a table with the appropriate Columns
                Table(table_name, metadata, *args)
                metadata.create_all()
                created = True
            except Exception as err:
                logger.error(str(err))

        # file_name = ROOT_DIR + f"tests/datasets/database/seeders/mysql/seeder.table.{database_name}.{table_name}.sql"
        # populated = False
        # try:
        #     populated = MySQLHelper.sow_table(mysql_connection, table_name, file_name)
        #     if populated:
        #         logger.info(f"Table populated:: {table_name}")
        # except Exception as err:
        #     logger.error(f"Error:: {err}")

        return created and populated

    @classmethod
    def drop_table(cls, logger, table_name):
        dropped = False
        try:
            URI = get_uri(cls.CONFIG)
            engine = create_engine(URI)
            if table_name in models.MODELS.keys():
                model = models.MODELS[table_name]
                dropped = model.__table__.drop(engine)

            if dropped:
                logger.info(f"Table deleted:: {table_name}")
        except Exception as err:
            logger.error(f"Error:: {err}")

        return dropped
