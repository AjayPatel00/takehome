## Overview

Here we compute scores for lines of text from an input file using a map-reduce approach 
I tried a lightweight approach using `asyncio` and a more heavyweight approach using the `ray` library that has a nice dashboard for monitoring

## Key Features

- **Deterministic Scores**: I tested and saw that scores for a line are deterministic
- **Batch Requesting**: Tried making batch requests using multiple keys like 'data', 'items', and 'lines', but these didn't work for the server
- **Map-Reduce Approach**: The input file is split into chunks, with the number of chunks matching the number of available CPU cores Each chunk gets processed in parallel, with concurrent tasks limited by `max_concurrent_tasks`
- **Lightweight Implementation**: Uses `asyncio` to handle HTTP sessions and process chunks and lines asynchronously with exponential backoff for retrying failed requests
- **Performance Observations**: Bumping `max_concurrent_tasks` beyond 100 didn't really help much The task is more about network than CPU, with an average of 4.15 seconds per line
- **Caching and Optimization**: Added caching and early returns for empty lines to speed things up (could probably use a LRU cache or something to save memory)
- **Performance Metrics**: Best processing time was 83.97 seconds using the lightweight approach
- **Ray Library Exploration**: Ray library lets you set the number of CPUs and allows for oversubscription (using more workers than available CPUs) With 32 workers and 64 threads, processing time dropped to 43 seconds, but this might cause issues in heavier workloads

## Technical Details

- **Concurrency**: using `ThreadPoolExecutor` for parallel processing and `asyncio` for asynchronous HTTP requests
- **Exponential Backoff**: retries with exponentially increasing wait times
- **Caching**: a dictionary to save results

## System Requirements

- **Operating System**: Tested on macOS with 10 available CPU cores
- **Python Libraries**: Needs `aiohttp`, `asyncio`, and `concurrent.futures`