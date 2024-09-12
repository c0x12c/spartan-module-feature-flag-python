# spartan-module-feature-flag

This module provides a flexible and standardized way to manage feature flags in Python applications. It supports PostgreSQL for persistent storage and optional Redis caching for improved performance.

## Features
- **CRUD Operations**: Create, read, update, and delete feature flags.
- **Database Support**: PostgreSQL integration.
- **Optional Redis Caching**: Cache feature flag data for faster access. Redis integration is optional and can be omitted.

## Installation
To install the module and its dependencies, use:
  ```bash
  poetry install
  ```

## Example Usage
In the [`examples/basic-usage`](./examples/basic-usage) directory, you will find a complete example of how to use the Feature Flag module in a FastAPI application.

## Development

### Debugging & Fixing Issues:
Local Debugging: clone the module repository and install it in "editable" mode using `pip install -e .`.

### Install
- To install the module and its dev dependencies, use:
  ```bash
  poetry install --with dev
  ```

### Run docker-compose
- To run the PostgreSQL and Redis services, use:
  ```bash
  docker-compose -f docker-compose.ci.yml up -d
  ```

- To shut down the services, use:
  ```bash
  docker-compose -f docker-compose.ci.yml down
  ```

### Testing
To run the tests, use:
- Unit tests:
  ```bash
  poetry run pytest tests/unit
  ```

- Integration tests:
  ```bash
  poetry run pytest tests/integration
  ```

- Or we can run all tests:
  ```bash
  poetry run pytest tests/
  ```

## Release
Please follow guidelines in [docs/RELEASE.md](./docs/RELEASE.md)

## Contributors

<!-- readme: collaborators,contributors -start -->
<table>
	<tbody>
		<tr>
            <td align="center">
                <a href="https://github.com/spartan-ductduong">
                    <img src="https://avatars.githubusercontent.com/u/112845152?v=4" width="100;" alt="spartan-ductduong"/>
                    <br />
                    <sub><b>Duc Duong</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/spartan-haobui">
                    <img src="https://avatars.githubusercontent.com/u/146458589?v=4" width="100;" alt="spartan-haobui"/>
                    <br />
                    <sub><b>Hao Bui</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/spartan-tonydang">
                    <img src="https://avatars.githubusercontent.com/u/128400107?v=4" width="100;" alt="spartan-tonydang"/>
                    <br />
                    <sub><b>Tony DangK</b></sub>
                </a>
            </td>
		</tr>
	<tbody>
</table>
<!-- readme: collaborators,contributors -end -->
