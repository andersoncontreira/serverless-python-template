"""This is the main file of the lambda application

This module contains the handler method
"""
import base64
import os

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import boot
from application import APP_NAME, APP_VERSION, http_helper
from application import helper
from application.config import get_config
from application.core import Application
from application.database.mysql import run_compatible_with_sqlalchemy, get_uri
from application.enums.messages import MessagesEnum
from application.exceptions import ApiException, ValidationException, CustomException
from application.helper import open_vendor_file, print_routes
from application.http_helper import CUSTOM_DEFAULT_HEADERS, set_hateos_links, set_hateos_meta, \
    get_favicon_32x32_data, get_favicon_16x16_data
from application.http_resources.request import ApiRequest
from application.http_resources.response import ApiResponse
from application.logging import get_logger, set_debug_mode
from application.migrations import models
from application.openapi import spec, get_doc, generate_openapi_yml, api_schemas
from application.services.healthcheck_manager import HealthCheckManager
from application.services.product_manager import ProductManager

# # load directly by boot
# ENV = boot.get_environment()
# debug
DEBUG = helper.debug_mode()

# Logger
LOGGER = get_logger(force=True)


def create_app(configuration_object=None):
    global LOGGER
    # config
    if configuration_object is None:
        configuration_object = get_config()
    # keep in this order, the app generic stream handler will be removed
    app = Application(APP_NAME)
    # set configurations
    app.config.from_object(configuration_object)
    # override the APP logger
    app.logger = LOGGER

    return app


APP = create_app()

# override the log configs
if DEBUG:
    APP.debug = DEBUG
    # override to the level desired
    set_debug_mode(LOGGER)

# todo melhorar essa parte, removendo essas variaveis
API_ROOT = os.environ['API_ROOT'] if 'API_ROOT' in os.environ else ''
API_ROOT_ENDPOINT = API_ROOT if API_ROOT != '' or API_ROOT is None else '/'

LOGGER.info("API_ROOT_ENDPOINT: {}".format(API_ROOT_ENDPOINT))


@APP.route(API_ROOT_ENDPOINT)
def index():
    """
    API Root path

    :return: Returns the name and the current version of the project

    # pylint: disable=line-too-long

    :rtype: flask.Response
    """
    body = {"app": f'{APP_NAME}:{APP_VERSION}'}
    return http_helper.create_response(body=body, status_code=200)


@APP.route(API_ROOT + '/alive')
def alive():
    """
    Health check path

    :return Returns an intelligent healthcheck that describe what resource are working or not.

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#healthcheck

    # pylint: disable=line-too-long
    See https://docs.microsoft.com/en-us/dotnet/architecture/microservices/implement-resilient-applications/monitor-app-health

    :rtype: flask.Response

    ---

        get:
            summary: Service Health Method
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: HealthCheckSchema
                424:
                    description: Failed dependency response
                    content:
                        application/json:
                            schema: HealthCheckSchema
                503:
                    description: Service unavailable response
                    content:
                        application/json:
                            schema: HealthCheckSchema
        """
    service = HealthCheckManager()
    return service.check()


@APP.route(API_ROOT + '/favicon-32x32.png')
def favicon():
    """
    Favicon path

    :return Returns a favicon for the browser with size 32x32
    :rtype: flask.Response
    """
    headers = CUSTOM_DEFAULT_HEADERS.copy()
    headers['Content-Type'] = "image/png"
    data = get_favicon_32x32_data()

    if helper.is_running_on_lambda():
        data_b64 = {
            'headers': headers,
            'statusCode': 200,
            'body': data,
            'isBase64Encoded': True
        }
        data = helper.to_json(data_b64)
        headers = {"Content-Type": "application/json"}
    else:
        data = base64.b64decode(data)

    return http_helper.create_response(body=data, status_code=200, headers=headers)


@APP.route(API_ROOT + '/favicon-16x16.png')
def favicon16():
    """
    Favicon path

    :return Returns a favicon for the browser with size 16x16
    :rtype: flask.Response
    """
    headers = CUSTOM_DEFAULT_HEADERS.copy()
    headers['Content-Type'] = "image/png"
    data = get_favicon_16x16_data()

    if helper.is_running_on_lambda():
        data_b64 = {
            'headers': headers,
            'statusCode': 200,
            'body': data,
            'isBase64Encoded': True
        }
        data = helper.to_json(data_b64)
        headers = {"Content-Type": "application/json"}
    else:
        data = base64.b64decode(data)

    return http_helper.create_response(body=data, status_code=200, headers=headers)


@APP.route(API_ROOT + '/docs')
def docs():
    """
    Swagger OpenApi documentation

    :return Returns the Swagger UI interface for test operations

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#openapiswagger

    :rtype flask.Response
    """
    headers = CUSTOM_DEFAULT_HEADERS.copy()
    headers['Content-Type'] = "text/html"
    html_file = open_vendor_file('./public/swagger/index.html', 'r')
    html = html_file.read()
    return http_helper.create_response(
        body=html, status_code=200, headers=headers)


@APP.route(API_ROOT + '/openapi.yml')
def openapi():
    """
    Swagger OpenApi documentation route

    :return Returns the openapi.yml generated the API specification file

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#openapiswagger

    :rtype flask.Response
    """
    headers = CUSTOM_DEFAULT_HEADERS.copy()
    headers['Content-Type'] = "text/yaml"
    html_file = open_vendor_file('./public/swagger/openapi.yml', 'r')
    html = html_file.read()
    return http_helper.create_response(
        body=html, status_code=200, headers=headers)


# product routes
@APP.route(API_ROOT + '/v1/product', methods=['GET'])
def product_list():
    """
    Product list route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response

        ---
        get:
            summary: Product List
            parameters:
            - name: limit
              in: query
              description: "List limit"
              required: false
              schema:
                type: int
                example: 20
            - name: offset
              in: query
              description: "List offset"
              required: false
              schema:
                type: int
                example: 0
            - name: fields
              in: query
              description: "Filter fields with comma"
              required: false
              schema:
                type: string
                example:
            - name: order_by
              in: query
              description: "Ordination of list"
              required: false
              schema:
                type: string
                enum:
                 - "asc"
                 - "desc"
            - name: sort_by
              in: query
              description: "Sorting of the list"
              required: false
              schema:
                type: string
                example: id
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: HateosProductListResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: ProductListErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: ProductListErrorResponseSchema
        """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(True)

    manager = ProductManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:
        data = manager.list(request.to_dict())
        response.set_data(data)
        response.set_total(manager.count(request.to_dict()))

        # hateos
        response.links = None
        set_hateos_meta(request, response)
        # LOGGER.info(data)
        # LOGGER.info(response.data)
    except CustomException as err:
        LOGGER.error(err)
        error = ApiException(MessagesEnum.LIST_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route(API_ROOT + '/v1/product/<uuid>', methods=['GET'])
def product_get(uuid):
    """
    Product get route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
        ---
        get:
            summary: Product Get
            parameters:
            - in: path
              name: uuid
              description: "Product Id"
              required: true
              schema:
                type: string
                format: uuid
                example: 4bcad46b-6978-488f-8153-1c49f8a45244
            - name: fields
              in: query
              description: "Filter fields with comma"
              required: false
              schema:
                type: string
                example:
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: HateosProductGetResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: ProductGetErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: ProductGetErrorResponseSchema
    """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(True)

    manager = ProductManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:
        response.set_data(manager.get(request.to_dict(), uuid))

        # hateos
        set_hateos_links(request, response, uuid)
        set_hateos_meta(request, response, uuid)

    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.FIND_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route(API_ROOT + '/v1/product', methods=['POST'])
def product_create():
    """
    Product create route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
        ---
        post:
            summary: Product Create
            requestBody:
                description: 'Product to be created'
                required: true
                content:
                    application/json:
                        schema: ProductCreateRequestSchema
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: ProductCreateResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: ProductCreateErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: ProductCreateErrorResponseSchema
            """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(False)

    manager = ProductManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:
        response.set_data(manager.create(request.to_dict()))
        # response.set_total(manager.count(request))

        # hateos
        # set_hateos_links(request, response, uuid)
        # set_hateos_meta(request, response, uuid)
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.CREATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route('/v1/product/<uuid>', methods=['PUT'])
def product_update(uuid):
    """
    Product update route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
        ---
        put:
            summary: Complete Product Update
            parameters:
            - in: path
              name: uuid
              description: "Product Id"
              required: true
              schema:
                type: string
                format: uuid
                example: 4bcad46b-6978-488f-8153-1c49f8a45244
            requestBody:
                description: 'Product to be updated'
                required: true
                content:
                    application/json:
                        schema: ProductCompleteUpdateRequestSchema
            responses:
                200:
                    content:
                        application/json:
                            schema: ProductUpdateResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: ProductUpdateErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: ProductUpdateErrorResponseSchema
            """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(False)

    manager = ProductManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:

        response.set_data(manager.update(request.to_dict(), uuid))
        # response.set_total(manager.count(request))
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.UPDATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route('/v1/product/<uuid>', methods=['DELETE'])
def product_delete(uuid):
    """
    Product delete route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
            ---
            delete:
                summary: Soft Product Delete
                parameters:
                - in: path
                  name: uuid
                  description: "Product Id"
                  required: true
                  schema:
                    type: string
                    format: uuid
                    example: 4bcad46b-6978-488f-8153-1c49f8a45244
                responses:
                    200:
                        description: Success response
                        content:
                            application/json:
                                schema: ProductSoftDeleteResponseSchema
                    4xx:
                        description: Error response
                        content:
                            application/json:
                                schema: ProductSoftDeleteErrorResponseSchema
                    5xx:
                        description: Service fail response
                        content:
                            application/json:
                                schema: ProductSoftDeleteErrorResponseSchema
                    """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(False)

    manager = ProductManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:
        data = {"deleted": manager.delete(request.to_dict(), uuid)}
        response.set_data(data)
        # response.set_total(manager.count(request))
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.DELETE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


@APP.route('/v1/product/<uuid>', methods=['PATCH'])
def product_soft_update(uuid):
    """
    Product soft update route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
        ---
        patch:
            summary: Soft Product Update
            parameters:
            - in: path
              name: uuid
              description: "Product Id"
              required: true
              schema:
                type: string
                format: uuid
                example: 4bcad46b-6978-488f-8153-1c49f8a45244
            requestBody:
                description: 'Product field to be updated'
                required: true
                content:
                    application/json:
                        schema: ProductSoftUpdateRequestSchema

            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: ProductUpdateResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: ProductUpdateErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: ProductUpdateErrorResponseSchema
                """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request)
    response.set_hateos(False)

    manager = ProductManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:

        response.set_data(manager.soft_update(request.to_dict(), uuid))
        # response.set_total(manager.count(request))
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.UPDATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


# *************
# doc
# *************
spec.path(view=alive, path=API_ROOT + "/alive", operations=get_doc(alive))
# *************
# product
# *************
spec.path(view=product_list,
          path="/v1/product", operations=get_doc(product_list))
spec.path(view=product_get,
          path="/v1/product/{uuid}", operations=get_doc(product_get))
spec.path(view=product_create,
          path="/v1/product", operations=get_doc(product_create))
spec.path(view=product_update,
          path="/v1/product/{uuid}", operations=get_doc(product_update))
spec.path(view=product_soft_update,
          path="/v1/product/{uuid}", operations=get_doc(product_soft_update))
spec.path(view=product_delete,
          path="/v1/product/{uuid}", operations=get_doc(product_delete))
print_routes(APP, LOGGER)
LOGGER.info(f'Running at {APP.config.get("ENV")}')

# generate de openapi.yml
generate_openapi_yml(spec, LOGGER, force=True)

api_schemas.register()

# *************
# Migrations
# *************
# compatibility with sqlalchemy
run_compatible_with_sqlalchemy()
URI = get_uri(APP.config)

APP.config['SQLALCHEMY_DATABASE_URI'] = URI
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

APP.logger.info('URI: {}'.format(URI))

DB = SQLAlchemy(APP)
MIGRATE = Migrate(APP, DB)

# Models
models.create(DB)
