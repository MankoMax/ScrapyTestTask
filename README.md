# Rental Parser

Service for parsing rental offers from https://kelm-immobilien.de/immobilien source using Scrapy-framework.

## Installation

```shell
poetry shell
poetry install
```
For Debug mode:

```shell
cd scrapy_rental
scrapy crawl kelm_immobilien --loglevel ERROR
```

For all logs Levels:

```shell
cd scrapy_rental
scrapy crawl kelm_immobilien
```

The output will be saved in structured format in `output` folder.
- Country
  - Domain
    - Rental Object