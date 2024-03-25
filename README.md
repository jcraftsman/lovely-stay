# lovely-stay

This repository contains some working examples that illustrates some design patterns in a Serverless ecosystem.

:warning: **This is a work in progress** :warning:

New content will be added regularly.

## The case study

The case study is a simple application that allows users to book a stay in a hotel.

## Repository structure

The repository is composed of the following directories:

- `snippets`: Contains some code snippets that illustrate some design patterns in a Serverless ecosystem
- Python projects
    - `lovely-stay-faas-all-in-one`: A simplistic implementation when all the functions are deployed in a single
      Serverless function. The challenge is to find the most straightforward way to implement the application with the
      minimum of indirections.
    - `lovely-stay-paas-transaction-script`: Separates the business logic from the infrastructure code. The business
      logic is implemented in a transaction script.
    - `lovely-stay-eda-process-manager`: A more complex implementation that orchestrates transactions in two separate
      bounded contexts (Booking and Pricing) and other external services. The business logic is implemented in a process
      manager.

## Conventions and tools used in Python Projects

Each Python uses project has the following structure:

- Architecture diagrams as plantuml code following the [C4 model](https://c4model.com/) are available in `architecture`
  directory for each project
- Source code, tests, and dependencies are managed by [poetry](https://python-poetry.org/docs/)
    - `src`: Contains the source code of the project
    - `tests`: Contains the tests of the project
- Automation code: deployment is automated using [pulumi](https://www.pulumi.com/docs/) in python. The automation code
  is in the `src/automation` directory of each project