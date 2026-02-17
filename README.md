# Parks Pipeline

#### The Scenario:
You are a newly hired Data Engineer at a marketing analytics firm that specializes in customer 
behavior and loyalty programs.
One of the firm’s clients provides services to people who engage in outdoor activities. They are 
considering expanding that to providing services to people who are specifically National Park visitors, 
including lodging, guided activities inside the park, and activities outside the park that park visitors can participate in 
are likely to engage in. The client wants to launch a pilot program to better understand visitor 
frequency and behavior patterns across parks and seasons.

#### The Problem:
The client has a database that collects data on national park visits, but unfortunately, the group 
developing the loyalty program does not have access to it. Fortunately, someone had the foresight to 
build a secure API that can get the data the group needs. The group knows nothing about APIs, how 
they work, or how they would work with the data. They just want the data in a particular form.

#### The Ask:
“We need national park visit data to build a loyalty program. We don’t have direct access to the 
source data, so we need you to build a solution that gets the data and puts it in a data warehouse."

#### Project Description

# Parks Data Pipeline – Lakehouse & Dimensional Analytics

This project implements a **production-style data pipeline** designed to ingest PostgreSQL data exposed through a **Swagger-documented REST API**, process it through a **modern lakehouse architecture**, and store it in a **dimensional model** optimized for analytical workloads.

The primary objective of the pipeline is to **track and analyze user spending behavior** through reliable, reproducible batch processing.

---

##  Architecture Overview

The pipeline follows a **Bronze–Silver–Gold** data architecture pattern:

###  Bronze Layer – Raw Data Lake
- Data is fetched daily from a Swagger API endpoint backed by PostgreSQL
- Raw JSON responses are stored **as-is**
- No preprocessing, validation, or metadata is applied
- Serves as the immutable source of truth

---

### Silver Layer – Cleaned & Structured Data

The silver layer is split into two stages:

#### Step 1. Data Cleaning & Preprocessing
- Removal of invalid, duplicate, or irrelevant records
- Basic schema validation and normalization
- Ensures consistency and quality before analytics

#### Step 2. Parquet Transformation
- Cleaned data is converted into **Parquet format**
- Optimized for columnar storage and query performance
- Reduces storage footprint and improves downstream efficiency

---

###  Gold Layer – Analytics & Dimensional Modeling
- **DuckDB** is used to query the lakehouse as a relational database
- Data is modeled into a **dimensional schema (fact and dimension tables)**
- Enables efficient analytical queries such as:
  - User spending trends
  - Time-based aggregations
  - Behavioral and financial insights

---

##  Batch Processing
- The pipeline runs on a **daily batch schedule**
- Ensures continuous and consistent data ingestion
- Designed for scalability, reproducibility, and auditability

---

##  Use Case
This architecture enables:
- Reliable historical data storage
- Clear separation of raw, cleaned, and analytical data
- High-performance analytical querying
- A strong foundation for BI dashboards and advanced analytics

---

##  Pipeline Structure

![Pipeline Structure](https://github.com/Jurgen12345/Parks-Pipeline/blob/main/images/pipeline-structure.svg)
