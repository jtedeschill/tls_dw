# TLS Datawarehouse

<!-- checkbox -->
    [x] - Develop Bullhorn Extractor
    [ ] - Develop Hubspot Extractor
    [ ] - Develop Google BigQuery Loader
    [ ] - Write Github Actions
    [ ] - Write dbt incremental models
    [ ] - Write dbt tests

## Introduction

This repository contains pythons scripts to extract data from Bullhorn, Hubspot and write it to Google BigQuery.

## Bullhorn API Client

This Python package provides a client for authenticating and making requests to the Bullhorn API. It is designed to simplify interactions with Bullhorn's REST API for applications that require integration with Bullhorn's staffing and recruitment services.

### Features

- Authentication with the Bullhorn API using OAuth.
- Refreshing access tokens.
- Making authenticated requests to the Bullhorn REST API.
- Supports pagination and recursive data fetching.
- Logging for debugging purposes.

### Installation

To use this package, you need to have Python installed on your system. Clone this repository or download the source code to get started.

Before running the script, ensure you have the required dependencies installed:

```bash
pip install requests pandas python-dotenv