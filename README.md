           ┌───────────────────┐
           │   Data Source      │
           │ nhatot.com Web     │
           │ Scraping/ Crawling│
           └─────────┬─────────┘
                     │
                     ▼
           ┌───────────────────┐
           │ Data Ingestion     │
           │ (Kafka Producer)   │
           │ Stream of Listings │
           └─────────┬─────────┘
                     │
                     ▼
           ┌───────────────────┐
           │ Stream Processing │
           │ (Apache Spark     │
           │ Structured Streaming) │
           │ - Clean data      │
           │ - Transformations │
           │ - UDFs, Aggregates│
           └─────────┬─────────┘
                     │
        ┌────────────┴─────────────┐
        │                          │
        ▼                          ▼
┌───────────────────┐       ┌───────────────────┐
│ Batch Storage     │       │ NoSQL Database    │
│ HDFS / S3         │       │ MongoDB / Cassandra│
│ Raw & Processed   │       │ Fast querying &   │
│ Data              │       │ analytics         │
└─────────┬─────────┘       └─────────┬─────────┘
          │                          │
          └────────────┬─────────────┘
                       ▼
               ┌───────────────┐
               │ Analytics &   │
               │ ML Processing │
               │ Spark MLlib   │
               │ GraphFrames   │
               │ Time Series   │
               └───────┬───────┘
                       │
                       ▼
               ┌───────────────┐
               │ Visualization │
               │ Dashboards    │
               │ (Grafana /    │
               │ Superset)     │
               └───────────────┘
