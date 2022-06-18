# Guidelines for projects
In this document you will find guidelines for your project to comply with the `guidelines`
defined by the architecture team, with the objective of making your project very complete.

## Topics
* Github templates
* Github actions/workflows
* Github docs
* Sonar
* OpenAPI/Swagger
* RESTful and HATEOS
* Healthcheck
* Docker
* config editor
* Serverless
* Logs and monitoring
* Automation scripts
* Environment configuration scripts
* Terraform
* Tests
* CI/CD files for AWS
* Metafiles




## Github templates
Include standardized templates for:
* Pull Request
* Issues
  * Bug Report
  * Documentation Request
  * Feature Request

## Github actions/workflows
Include scripts for the following actions:
* lint
* Unit Test
* Component Test
* Sonar
* Versioning

## Github docs
Include files focused on community use:
* README.md
* CHANGELOG.md
* CODE_OF_CONDUCT.md
* CONTRIBUTING.md
* LICENSE.md

### README.md
It is important that this file contains the following steps in it:
* Brief description
* requirements
* Functionalities
* Installation
* Execution
* Test execution
* Execution tools for development (optional)

### Other files
Follow the pattern of the reference architectures, you can copy them.

## Sonar
The project must have the sonar and action configuration file for analysis.
* sonar.properties
* .github/workflows/sonar.yml

## OpenAPI/Swagger
When the project is an API, it is necessary that it have documentation in the OpenAPI standard.

Consider using:
* UI
* Schemas
* routes

## RESTful and HATEOS
When the project is an API, it is desirable that it implements the definitions of the RESTful standard.
Even better if you can apply HATEOS concepts.

For more details see:
* [Designing-a-Beautiful-REST%2BJSON-API.pdf](https://docs.huihoo.com/apache/apachecon/us2014/Designing-a-Beautiful-REST%2BJSON-API.pdf)
* [HTTP Methods for RESTful Services](https://www.restapitutorial.com/lessons/httpmethods.html#:~:text=The%20primary%20or%20most%2Dcommonly,but%20are%20utilized%20less%20frequently. )
* [RESTful Web Services Resources](https://www.restapitutorial.com/resources.html)
* [REST-API-Design-Filtering-Sorting-and-Pagination](https://www.moesif.com/blog/technical/api-design/REST-API-Design-Filtering-Sorting-and-Pagination/)
* [HTTP Status Dogs](https://httpstatusdogs.com/)

## Healthcheck
When the project is an API, it is required to implement a `healthcheck` endpoint, it is recommended that
the project applies the defined standard of the guideline documentation, so that it is an intelligent endpoint.

For more details see:
* [Microsoft - Health Monitoring](https://docs.microsoft.com/en-us/dotnet/architecture/microservices/implement-resilient-applications/monitor-app-health)
* [Microsoft - Example with ASP.NET Core](https://docs.microsoft.com/en-us/aspnet/core/host-and-deploy/health-checks?view=aspnetcore-6.0)
* [Testfully - Article Health Check](https://testfully.io/blog/api-health-check-monitoring/)

## Docker
Docker files must be in the docker folder, being organized by context, examples:
* docker/
  * php/
    * Dockerfile
    * entrypoint.sh
  * nginx/
    *logs/*
    * Dockerfile
    * app.conf
    * nginx.conf
  * python/
    * Dockerfile
    * entrypoint.sh

## Editorconfig
It is extremely important that the project has a universal configuration file so that regardless of the tool that
use, the project does not undergo unwanted changes in file formatting, line break type, etc.

## Serverless
When applicable to the project, leave their respective files configured in the root of the project.

## Logs and monitoring
It is recommended that the project make a log interface to provide project execution information.
It is also recommended that it sends logs to NewRelic and that the project is instrumented there.

## Automation scripts
The project's development task execution automation scripts must be in the `scripts` folder;

## Environment configuration scripts
It is recommended that environment configuration files are saved in the `env/` folder.
Just the development file (with notes to local resources via Docker) and example integration file,
other configuration files must not be versioned.

Example:
```
./env/development.env
./env/integration.env.example
```
Or:
```
./env/.env.development
./env/.env.integration.example
```
## Terraform
Terraform files if present in the project must be in the `infrastructure` folder;

## Tests
It is highly recommended that the project has tests, mainly that follow the context approach, such as tests of
component, unit and integration. For projects that are focused on the front-end, it is interesting that we have the context
of usability and testing of application components.

For more details see:
* [Martin Fowler - Testing Microservices](https://martinfowler.com/articles/microservice-testing/)

## CI/CD files for AWS
When the project is properly configured, it is ideal that it has the CI/CD files for AWS.
These files should be mainly focused on actions aimed at the CD.
In the future, tasks focused on CI will be carried out via Github.

Example:
```
buildspec.yaml
appspec.yaml
```

## Metafiles
### Project resource
Create a project metadata file called `.projectrc`.
This file will contain project data like name, version and docker network,
this can be used for other purposes of executing `automation scripts,
In addition to integration with DX tools (Developer Experience).

Example:

```dotenv
APP_NAME=project-name-here
APP_VERSION=1.0.0
NETWORK_NAME=docker-network-name-here
```

### dockerignore
File with the references of folders and files that should be ignored by docker during copying
of the project folder's contents.

### gitignore
File with the references of folders and files that should be ignored by git during development
from the project.

### docker-compose.yml
File with settings for managing containers in the development environment.