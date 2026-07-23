# R2D2: Research Repository for Data and Diagnostics

## Table of Contents

1. [What is R2D2?](#what-is-r2d2)
2. [How R2D2 Works](#how-r2d2-works)
3. [R2D2 Concepts](#r2d2-concepts)
4. [How Swell Uses R2D2](#how-swell-uses-r2d2)
5. [Store & Fetch Quick Reference](#store--fetch-quick-reference)
6. [Storing Observations in R2D2](../practical_examples/r2d2/r2d2_ingest.md)

---

## What is R2D2?

**R2D2** is a metadata + storage system for scientific data: it keeps a **MySQL database** of what files exist and where they live, while the **actual files** go in S3 or local storage. When you `fetch` or `store`, you talk to the R2D2 API for metadata; file transfers go **directly** to/from storage. Swell uses R2D2 to fetch observations, store backgrounds, and manage experiment data.

Think of R2D2 as a **central database for scientific data** that:
- Knows exactly where every file is stored
- Tracks what type of data each file contains (observations, forecasts, analyses, etc.)
- Remembers when data was created and by whom
- Can quickly retrieve the right file when you need it

**Swell + R2D2**: When you run a Swell experiment, it uses R2D2 to fetch observations, store/retrieve background and analysis files, and manage experiment metadata.

---

### Why R2D2

R2D2 serves as the centralized source for managing and accessing scientific data:

With R2D2 you can:
- Retrieve specific files easily:
  - 
    ```python
    r2d2.fetch(
        item='observation',
        provider='nasa',
        observation_type='airs',
        window_start='20240103T120000Z',
        window_length='PT6H',
        target_file='obs.nc4'
    )
    ```
- Store new data and make it accessible:
  - 
    ```python
    r2d2.store(
        item='analysis',
        model='geos',
        experiment='my_exp',
        file_extension='nc4',
        date='20240103T120000Z',
        source_file='./an.nc'
    )
    ```
- Automatically track data versions and timestamps
- Share data securely with authorized users across locations
- Prevent duplicate storage

---

## How R2D2 Works

### Architecture Example:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     R2D2 Server (metadata only)                             │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   R2D2 API                 │          MySQL / Database              │   │
│   │   (HTTP)                   │          (what exists)                 │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│              │                                                              │
│              │  Answers: "What files match? Where are they stored?"         │
└──────────────┼──────────────────────────────────────────────────────────────┘
               │
               │  Client does NOT send files through the server.
               │  Client talks to server for metadata, then transfers
               │  files directly to/from storage (S3, local, etc.).
               │
       ┌───────┴────────────────────────────────────────────────────┐
       │                    Compute client                          │
       │                   (HPC/Discover, cloud etc.)               │
       │                                                            │
       │   import r2d2                                              │
       │   r2d2.fetch(item='observation', provider='nasa', ...)     │
       │   r2d2.store(item='observation', source_file='obs.nc', ...)│
       └────────────────────────────────────────────────────────────┘
               │                                 ▲
               │  Fetch: get metadata and        │  Direct transfer
               │  download from storage          │  to/from storage
               ▼                                 │
       ┌─────────────────────────────────────────────────────────────┐
       │              Data storage (S3, local disk, etc.)            │
       │   observation/  forecast/  analysis/  bias_correction/  ... │
       └─────────────────────────────────────────────────────────────┘
```


1. **R2D2 Server**: Only handles metadata queries
   - "What observations exist for this window?"
   - "Where is this file stored?" (returns S3 path or local path)
   
2. **S3 / local storage**: Stores the actual data files
   - File transfers go **directly** between your client and S3; *not through the R2D2 server*

Even with a small EC2 instance, R2D2 can serve metadata for terabytes of data. The server doesn't proxy file I/O.

---

## R2D2 Concepts

### Data Hub
A **Data Hub** is a storage platform or cloud region where data can be stored.

| Property | Description | Example Values |
|----------|-------------|----------------|
| `name` | Unique identifier | `aws-us-east-1`, `discover-local`, `azure-eastus` |
| `platform` | Storage platform type | `aws`, `local`, `azure`, `gcloud` |
| `region` | Geographic region | `us-east-1`, `us-west-2` |

**Why it exists**: You may access data from different cloud providers or on-premise storage. A data hub tells R2D2 which storage system to use.

### Data Store
A **Data Store** is our data repository, think of it like a specific storage location (like an S3 bucket or file system path) within a Data Hub. 

| Property | Description | Example Values |
|----------|-------------|----------------|
| `name` | Unique identifier (often the bucket name) | `r2d2-experiments-prod-us-east-1` |
| `data_hub` | Which Data Hub this belongs to | `aws-us-east-1` |
| `data_store_type` | Category of data | `experiments`, `archive`, `skylab` |
| `basedir` | Base directory path | `/data/r2d2/` or empty for S3 root |
| `read_only` | Whether writes are allowed | `true` or `false` |


### Compute Host
A **Compute Host** is our compute environment, it represents a computing environment where scientists run their code.

| Property | Description | Example Values |
|----------|-------------|----------------|
| `name` | Unique identifier | `discover-intel`, `localhost-gnu`, `aws-graviton-gnu` |
| `hostname` | Machine identifier | `discover`, `localhost`, `ip179-99-99-99` |
| `compiler` | Compiler used to build software | `intel`, `gnu`, `nvhpc` |


### How They Connect

```
                    ┌───────────────────┐
                    │   Compute Host    │
                    │  (discover-intel) │
                    └───────────────────┘
                             │
                             │ "Where should I store/fetch data?"
                             │
                             ▼
           ┌─────────────────────────────────┐
           │     compute_host_register       │
           │  (links hosts to data hubs)     │
           │                                 │
           │  discover-intel → aws-us-east-1 │
           │  localhost-gnu → aws-us-east-1  │
           └─────────────────┬───────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Data Hub     │
                    │  (aws-us-east-1)│
                    └────────┬────────┘
                             │
                             │ "Which bucket within this hub?"
                             │
                             ▼
                    ┌─────────────────┐
                    │   Data Store    │
                    │  (r2d2-bucket)  │
                    └─────────────────┘
```

---

## How Swell Uses R2D2

When you run a Swell experiment, R2D2 is used behind the scenes in several tasks:

| Swell Task | What it does with R2D2 |
|------------|------------------------|
| **Get Observations** | Fetches observation files from R2D2 by `provider`, `observation_type`, `window_start`, `window_length`; falls back to empty observations if not found |
| **Store Background** | Stores forecast/background files so they can be reused by later cycles |
| **Get Background** | Fetches background files for the current cycle from R2D2 |
| **Ingest Obs** | Ingest suite that stores newly processed observations into R2D2 |
| **Save Obs Diags** | Stores feedback/diagnostic files (`item='feedback'`) |
| **Save Restart** | Stores forecast and analysis restart files for model components |

> **Note**: R2D2 adaptation in Swell is under active development. Task behavior and configuration may change as implementation continues.

---

## Store & Fetch Quick Reference

### Observation (shared input data — no experiment)

```python
# Fetch
r2d2.fetch(item='observation', 
           provider='ncdiag', 
           observation_type='airs',
           file_extension='nc4', 
           window_start='20240103T120000Z', 
           window_length='PT6H',
           target_file='obs.nc4')

# Store
r2d2.store(item='observation', 
           provider='ncdiag', 
           observation_type='airs',
           file_extension='nc4', 
           window_start='20240103T120000Z', 
           window_length='PT6H',
           source_file='./obs.nc4')
```

**Required:** `provider`, `observation_type`, `file_extension`, `window_start`, `window_length`

---

### Analysis & forecast/background (experiment-specific)

**Required:** `model`, `experiment`, `file_extension`, `date`. For forecast also: `resolution`, `step`.

```python
# Fetch analysis
r2d2.fetch(item='analysis', 
           model='geos', 
           experiment='my_exp', 
           file_extension='nc4',
           date='20240103T120000Z', 
           target_file='an.nc4')

# Fetch forecast (background)
r2d2.fetch(item='forecast', 
           model='geos', 
           experiment='my_exp', 
           file_extension='nc4',
           resolution='c90', 
           step='PT6H', 
           date='20240103T120000Z', 
           target_file='bkg.nc4')

# Store analysis
r2d2.store(item='analysis', 
           model='geos', 
           experiment='my_exp', 
           file_extension='nc4',
           date='20240103T120000Z', 
           source_file='./an.nc4')

# Store forecast
r2d2.store(item='forecast', 
           model='geos', 
           experiment='my_exp', 
           file_extension='nc4',
           resolution='c90', 
           step='PT6H', 
           date='20240103T120000Z', 
           source_file='./bkg.nc4')
```

**Note:** `experiment` must be registered in R2D2 first.

---

### Bias correction (experiment-specific)

**Required:** `model`, `experiment`, `provider`, `observation_type`, `file_extension`, `file_type`, `date`

```python
r2d2.fetch(item='bias_correction', 
           model='geos', 
           experiment='my_exp', 
           provider='gsi',
           observation_type='airs', 
           file_extension='satbias', 
           file_type='satbias',
           date='20240103T120000Z', 
           target_file='satbias.nc')
```
