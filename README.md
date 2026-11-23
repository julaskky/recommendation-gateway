# Recommendation Gateway

### A Configuration-Driven, Application-Independent Gateway for Recommendation Systems

Recommendation Gateway is a Python-based API service designed to simplify the integration of heterogeneous applications with recommendation engines through a standardised data exchange interface.

Modern applications frequently maintain different data structures, naming conventions, event representations, and interaction formats. Integrating recommendation engines directly with these applications often introduces application-specific dependencies, duplicated transformation logic, and unnecessary coupling between software components.

Recommendation Gateway addresses this challenge through a configurable normalisation and validation layer that transforms application-specific recommendation data into a canonical request structure.

The gateway provides a reusable integration architecture that separates application data representation from recommendation-engine requirements.

---

## 1. Project Overview

Recommendation Gateway acts as an intermediary between client applications and recommendation services.

Rather than requiring every application to implement its own recommendation request transformation logic, the gateway provides a centralised interface for translating application-specific payloads into a consistent representation.

The architecture is designed to support multiple applications through independent JSON mapping configurations.

For example, a restaurant application may represent customers, food items, restaurants, and interaction events differently from an e-commerce or entertainment application.

The gateway uses application-specific mappings to translate these differences into a common recommendation request contract.

This approach promotes:

- Application independence.
- Recommendation-engine interoperability.
- Reusable data transformation.
- Configuration-driven integration.
- Consistent request validation.
- Reduced integration complexity.
- Extensibility across different application domains.

## 2. Problem Statement

Recommendation systems are commonly integrated directly into individual applications. This approach can create several engineering challenges:

1. Different applications use incompatible data structures.
2. Recommendation engines may require different input formats.
3. Application-specific transformation logic becomes duplicated.
4. Changes to recommendation contracts can affect multiple integrations.
5. Adding new applications increases integration and maintenance complexity.
6. Missing, malformed, or inconsistent request fields can compromise downstream processing.

Recommendation Gateway introduces an intermediary normalisation layer to address these challenges.

The gateway separates the representation of application data from the canonical structure expected by downstream recommendation services.

## 3. Design Objectives

The primary objectives are to:

1. Establish a standardised recommendation request contract.
2. Support multiple applications through configuration-driven mappings.
3. Transform application-specific payloads into canonical representations.
4. Validate normalised requests using structured data models.
5. Support nested source fields and configurable defaults.
6. Provide reusable transformation logic.
7. Minimise application-specific dependencies.
8. Establish a foundation for integrating heterogeneous recommendation engines.

## 4. System Architecture

The system follows a modular API gateway architecture.

```text
          CLIENT APPLICATIONS
                   |
          +--------+--------+
          |        |        |
          v        v        v
      Restaurant  E-commerce Other Apps
          |        |        |
          +--------+--------+
                   |
                   v
       +-------------------------+
       |  Recommendation Gateway |
       |                         |
       |  Application Resolver   |
       |  Mapping Configuration |
       |  Request Normalisation |
       |  Contract Validation   |
       +-------------------------+
                   |
                   v
       +-------------------------+
       |   Canonical Request     |
       |                         |
       |  User / Customer        |
       |  Items / Entities       |
       |  Interaction Events     |
       |  Collections            |
       |  Recommendation Limit   |
       +-------------------------+
                   |
                   v
       +-------------------------+
       | Downstream Integration  |
       |                         |
       | Recommendation Engine   |
       +-------------------------+
```

The gateway establishes a boundary between application-specific data structures and the standardised recommendation interface.

The normalisation and validation components are implemented independently of individual client applications.

## 5. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| API framework | FastAPI |
| Data validation | Pydantic |
| API documentation | OpenAPI / Swagger UI |
| Configuration mappings | JSON |
| Environment configuration | python-dotenv |
| ASGI server | Uvicorn |
| Testing framework | Pytest |
| Version control | Git |

The implementation uses a modular Python architecture and does not require a database for its current file-based mapping configuration.

## 6. Core Components

### 6.1 Application Registry and Mapping Configuration

The gateway uses application-specific JSON mapping files to define how incoming application data should be interpreted.

Each application can have its own mapping configuration without requiring the core normalisation service to be rewritten.

An example configuration is:

```text
app/mappings/restaurant_app.json
```

The restaurant application mapping defines transformations involving:

- Customers.
- Food items.
- Interaction events.
- Restaurants and related collections.

This configuration-driven approach makes it possible to introduce additional application integrations by defining new mappings.

### 6.2 Request Normalisation Engine

The normalisation service translates incoming application-specific payloads into the canonical recommendation request structure.

The implemented transformation capabilities include:

- Nested source-field resolution.
- Default-value assignment.
- Required-field handling.
- Value mapping.
- Data-type transformations.
- Collection mapping.
- Canonical request validation.

The normalisation service is designed to remain independent of the application consuming the gateway.

### 6.3 Canonical Recommendation Contract

The canonical recommendation schema establishes a consistent structure for recommendation requests.

Pydantic models provide structured validation of normalised data before it is passed to downstream components.

The canonical contract includes a recommendation limit, with a maximum supported value of 100.

This provides a common representation that can be used across different application integrations.

### 6.4 API Layer

FastAPI provides the HTTP interface for the gateway.

The API layer separates endpoint definitions from request schemas and normalisation logic.

This modular approach supports maintainability and allows new application integrations to be introduced without duplicating the core transformation implementation.

### 6.5 Application Independence

The gateway does not require every client application to adopt the same internal data model.

Instead, each application supplies its own mapping configuration, allowing the gateway to translate its payload into the canonical representation.

This separation reduces coupling between client applications and recommendation services.

## 7. Implemented API Endpoints

The current API foundation includes the following endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Root application endpoint |
| GET | `/api/v1/health` | Service health check |
| POST | `/api/v1/contracts/recommendations/validate` | Validate recommendation request contracts |
| POST | `/api/v1/applications/{application_id}/normalize` | Normalise application-specific recommendation requests |

### Health Check

```http
GET /api/v1/health
```

Provides a health-check interface for verifying API availability.

### Recommendation Contract Validation

```http
POST /api/v1/contracts/recommendations/validate
```

Validates recommendation request data against the canonical Pydantic contract.

### Application-Specific Normalisation

```http
POST /api/v1/applications/{application_id}/normalize
```

Transforms an incoming application-specific payload using the corresponding mapping configuration.

For the restaurant application, the application identifier is:

```text
restaurant_app
```

Example endpoint:

```http
POST /api/v1/applications/restaurant_app/normalize
```

The endpoint resolves the relevant application mapping, applies the configured transformations, and validates the resulting canonical request.

## 8. Project Structure

The current project architecture is organised into the following modules:

```text
recommendation-gateway/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── contracts.py
│   │       └── applications.py
│   │
│   ├── schemas/
│   │   ├── recommendation.py
│   │   └── application.py
│   │
│   ├── services/
│   │   └── normalization.py
│   │
│   └── mappings/
│       └── restaurant_app.json
│
├── tests/                  # Automated tests, as developed
│
├── requirements.txt        # Python dependencies
│
├── .env                    # Local environment configuration
│
├── .gitignore              # Git exclusion rules
│
└── README.md               # Project documentation
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `app/main.py` | FastAPI application entry point |
| `app/api/v1/contracts.py` | Recommendation contract validation endpoints |
| `app/api/v1/applications.py` | Application-specific normalisation endpoints |
| `app/schemas/recommendation.py` | Canonical recommendation data models |
| `app/schemas/application.py` | Application-related schemas |
| `app/services/normalization.py` | Core normalisation and transformation logic |
| `app/mappings/restaurant_app.json` | Restaurant application mapping configuration |

## 9. Installation and Setup

### Prerequisites

- Python 3.10 or later.
- pip.
- Git.
- Windows, Linux, or macOS.

XAMPP is not required to run this Python FastAPI application.

### Step 1: Clone the Repository

```bash
git clone https://github.com/julaskky/recommendation-gateway.git
```

Navigate into the project directory:

```bash
cd recommendation-gateway
```

### Step 2: Create a Virtual Environment

On Windows:

```cmd
python -m venv venv
```

Activate the environment:

```cmd
venv\Scripts\activate
```

On Linux or macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a local `.env` file if required by the application configuration.

The application configuration supports settings including:

```env
APP_NAME=Recommendation Gateway
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=true
```

Adjust the values according to the environment configuration implemented in the project.

Do not commit `.env` files or production secrets to version control.

### Step 5: Start the API Server

From the project root, run:

```bash
uvicorn app.main:app --reload
```

The development server will normally be available at:

```text
http://127.0.0.1:8000
```

## 10. API Documentation

FastAPI provides interactive API documentation.

Once the application is running, access:

**Swagger UI**

```text
http://127.0.0.1:8000/docs
```

**ReDoc**

```text
http://127.0.0.1:8000/redoc
```

**OpenAPI Schema**

```text
http://127.0.0.1:8000/openapi.json
```

These interfaces provide an interactive way to inspect the registered endpoints, request schemas, and API responses.

## 11. Testing

The project uses Pytest for automated testing.

Run the test suite from the project root:

```bash
pytest -v
```

Run tests with detailed output:

```bash
pytest -v -s
```

The application integration tests should verify:

- API availability.
- Health-check responses.
- Canonical recommendation contract validation.
- Application mapping resolution.
- Restaurant application normalisation.
- Nested source-field handling.
- Default-value assignment.
- Required-field validation.
- Value mapping and type transformations.
- Collection transformations.
- Invalid application and malformed request handling.

### Restaurant Application Integration

The initial restaurant application integration was tested successfully, returning HTTP 200 for a valid normalisation request.

This provides an initial verification of the configuration-driven integration workflow.

## 12. Extending the Gateway

One of the central design principles is that new application integrations should primarily be introduced through mapping configurations.

For example, additional integrations could include:

```text
app/mappings/
│
├── restaurant_app.json
├── ecommerce_app.json
├── entertainment_app.json
├── education_app.json
└── healthcare_app.json
```

These names illustrate possible future integrations; their corresponding mappings must be implemented before they can be used.

A new integration should define:

1. Its application identifier.
2. Source-field mappings.
3. Required fields.
4. Default values.
5. Value transformations.
6. Collection transformations.
7. The expected canonical output.

The normalisation service can then apply the mapping and validate the resulting request through the canonical contract.

## 13. Design Principles

The project follows several important software engineering principles.

**Separation of Concerns**

API routing, schema definitions, mapping configuration, and transformation services are maintained in separate modules.

**Configuration-Driven Integration**

Application-specific transformations are expressed through configuration rather than being hardcoded into individual API endpoints.

**Schema-Based Validation**

Pydantic provides structured validation of canonical recommendation requests.

**Application Independence**

The core normalisation service is designed to avoid dependencies on the internal implementation of individual client applications.

**Extensibility**

New integrations can be introduced through additional mappings and application registrations.

**Maintainability**

The modular architecture makes it easier to extend, test, and maintain the gateway.

## 14. Security Considerations

Production deployment should incorporate appropriate security controls, including:

- Authentication and authorisation for protected API operations.
- Input validation and request-size limits.
- Rate limiting and abuse prevention.
- Secure handling of environment variables.
- Restrictive CORS configuration.
- HTTPS communication.
- Structured error handling.
- Logging and monitoring.
- Protection against malformed or excessively complex payloads.
- Dependency and vulnerability management.

The gateway should not expose internal configuration files, secrets, or sensitive application data through API responses.

## 15. Future Development Roadmap

Potential areas for continued development include:

### Multi-Application Integration

- Additional application mapping configurations.
- Application registration and lifecycle management.
- Mapping validation and versioning.
- More comprehensive integration tests.

### Recommendation Engine Connectivity

- Standardised downstream recommendation interfaces.
- Multiple recommendation-engine adapters.
- Engine-specific request translation.
- Recommendation response normalisation.
- Provider selection and routing.

### Operational Capabilities

- API authentication.
- Rate limiting.
- Request tracing.
- Structured logging.
- Performance monitoring.
- Caching and observability.

### Platform Management

- Administrative dashboard.
- Application and mapping management.
- API usage analytics.
- Integration health monitoring.
- Mapping configuration management.

These are development opportunities rather than claims that the functionality is already implemented.

## 16. Current Project Status

Recommendation Gateway has an implemented FastAPI foundation, canonical recommendation schemas, application-specific normalisation endpoints, and a configuration-driven restaurant application integration.

The normalisation architecture supports nested paths, defaults, required fields, value mappings, type transformations, and collection mappings.

The initial restaurant application integration has passed an HTTP 200 test.

The project is being developed incrementally, with further application integrations, downstream recommendation-engine connectivity, and production operational capabilities forming part of the broader roadmap.

## 17. Repository

**Project:** Recommendation Gateway

**GitHub Repository:**

https://github.com/julaskky/recommendation-gateway

**Local Development Path:**

```text
C:\xampp\htdocs\recommendation-gateway
```

---

## 18. Conclusion

Recommendation Gateway establishes a reusable integration layer for connecting heterogeneous applications to recommendation services through a common data contract.

By combining configuration-driven normalisation, structured schema validation, and modular API architecture, the project provides a foundation for reducing integration complexity and improving interoperability across recommendation-driven applications.

Its longer-term objective is to support a flexible ecosystem in which multiple applications and recommendation engines can communicate through a consistent, maintainable, and extensible gateway.

**Recommendation Gateway — Standardising Data. Simplifying Integration. Enabling Intelligent Recommendations.**
