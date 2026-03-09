# Parks Pipeline

## The Scenario
You are a newly hired Data Engineer at a marketing analytics firm specializing in customer behavior and loyalty programs. One of the firm’s clients provides services to people who engage in outdoor activities and is considering expanding its offerings to visitors of U.S. National Parks. These services may include lodging, guided activities inside the park, and related activities outside the park that visitors are likely to participate in.

To support this initiative, the client wants to launch a **pilot loyalty program** designed to better understand **visitor frequency, spending patterns, and seasonal behavior across parks**.

---

## The Problem
The client already maintains a database that collects national park visit data. However, the loyalty program development team **does not have direct access to the database**.

Fortunately, the engineering team previously implemented a **secure REST API** that exposes the necessary data. The marketing analytics group, however, has no experience working with APIs or ingesting programmatic data. Their requirement is simple:

> “We need the data extracted from the API and organized in a data warehouse so we can analyze visitor behavior.”

---

## The Ask
Build a **reliable data pipeline** that retrieves data from the API and transforms it into a **structured analytical data warehouse** suitable for reporting, behavioral analysis, and future BI dashboards.

---

# Parks Data Pipeline – Lakehouse & Dimensional Analytics

This project implements a **production-style batch data pipeline** that ingests PostgreSQL data exposed through a **Swagger-documented REST API**, processes it through a **modern lakehouse architecture**, and models it into a **dimensional schema optimized for analytical workloads**.

The pipeline is designed to simulate real-world data engineering systems by incorporating:

- Automated orchestration
- Health monitoring
- Fault tolerance
- Structured logging
- Layered data architecture

The primary objective of the pipeline is to **track and analyze visitor spending behavior and park activity trends** through reliable and reproducible batch processing.

---

# Architecture Overview

The pipeline follows a **Bronze–Silver–Gold lakehouse architecture** managed by a centralized **orchestrator service**.

Each stage is responsible for a specific transformation level, ensuring clear separation between raw data ingestion, data preparation, and analytical modeling.

![Pipeline Architecture](https://github.com/Jurgen12345/Parks-Pipeline/blob/main/images/Screenshot%202026-03-09%20125112.png)

---

# Pipeline Orchestration

A custom **Python-based orchestrator** coordinates all pipeline components and ensures reliable execution.

The orchestrator is responsible for:

- Starting and managing all pipeline services
- Monitoring system health
- Restarting failed services automatically
- Logging pipeline activity and errors
- Ensuring dependencies between pipeline stages

Each service runs as an independent process, and the orchestrator continuously supervises them to ensure the pipeline remains operational.

---

# Health Monitoring

A dedicated **health check service** continuously monitors the status of the backend API.

- The health check periodically queries the API endpoint to verify that the backend database is functioning correctly.
- If the API reports warnings or failures, the health check notifies the orchestrator.
- The orchestrator can then **pause or restart the data collector** to prevent ingestion of corrupted or incomplete data.

This mechanism ensures that the pipeline only processes data when the source system is stable.

---

# Data Collection Service

The **collector service** is responsible for retrieving raw data from the API.

Responsibilities include:

- Fetching JSON data from the REST API
- Storing responses in the Bronze layer
- Running continuously while the backend system is healthy

If the backend becomes unstable, the orchestrator can automatically **stop and restart the collector** once the health check confirms the system has recovered.

---

# Bronze Layer – Raw Data Lake

The Bronze layer serves as the **immutable raw data storage layer**.

Characteristics:

- Raw JSON responses are stored **exactly as received**
- No preprocessing, validation, or transformation is applied
- Files are stored in a **schema-on-read format**
- Enables debugging, lineage tracking, and historical reprocessing

This layer acts as the **single source of truth** for all ingested data.

---

# Silver Layer – Cleaned & Structured Data

The Silver layer processes the raw Bronze data into a structured and validated format.

The Silver pipeline waits for the Bronze ingestion process to finish writing data before beginning transformations.

## Step 1: Data Cleaning & Validation

Operations include:

- Removal of invalid or corrupted records
- Duplicate record filtering
- Null value handling
- Basic schema normalization

This stage ensures the dataset is **consistent and analytics-ready**.

## Step 2: Parquet Transformation

Once cleaned, the datasets are converted into **Parquet files**.

Benefits include:

- Columnar storage format
- Reduced storage size
- Faster analytical query performance
- Efficient compatibility with analytical engines

---

# Gold Layer – Dimensional Analytics

The Gold layer transforms the curated Silver data into **business-ready analytical models**.

The process includes:

1. Reading Parquet datasets using **DuckDB**
2. Executing SQL transformations on the lakehouse data
3. Creating a **dimensional schema (fact and dimension tables)**

The resulting data model supports queries such as:

- Visitor spending trends
- Seasonal park activity
- Customer behavior segmentation
- Time-based revenue analysis

This layer is designed to support **business intelligence dashboards and analytical workloads**.

---

# Logging & Fault Tolerance

All pipeline services are supervised by the orchestrator and generate structured logs.

The orchestrator:

- Captures logs from each pipeline component
- Records execution status and errors
- Automatically restarts services if failures occur
- Maintains overall pipeline stability

This logging and recovery system ensures the pipeline can operate reliably even when unexpected errors occur.

---

# Batch Processing

The pipeline operates using a **daily batch ingestion model**.

Each execution cycle:

1. Collects new API data
2. Stores it in the Bronze data lake
3. Processes and converts it in the Silver layer
4. Builds analytical datasets in the Gold layer

This structure guarantees **consistent, reproducible data processing workflows**.

---

# Use Case

This architecture enables:

- Reliable historical data storage
- Clear separation between raw, curated, and analytical data
- High-performance analytical queries
- Reproducible data transformations
- A scalable foundation for BI dashboards and advanced analytics

---

### Running the application

In order to run the pipeline you first need to **uv sync** the pyproject and uv.lock files.

After that you can run the orchestrator and it will automatically run the pipleline as a whole.

**NOTE**: Change the API key to your key from the Swagger Docs website.


# Pipeline Structure

![Pipeline Structure](https://github.com/Jurgen12345/Parks-Pipeline/blob/main/images/pipeline-structure.svg)