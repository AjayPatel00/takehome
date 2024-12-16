import aiohttp
import asyncio
import time
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

num_workers = 10
max_concurrent_tasks = 100
total_lines = 20507
ENDPOINT = "https://interview-challenge.decagon.workers.dev/"

cache = defaultdict(int)

async def process_line(session, line, retries=3):
    global cache
    if len(line) == 0:
        return 136261
    if line in cache:
        return cache[line]
    
    attempt = 0
    while attempt < retries:
        try:
            async with session.post(ENDPOINT, data=line) as response:
                response.raise_for_status()
                result = await response.json()
                score = result.get('score', 0)
                cache[line] = score
                return score
        except aiohttp.ClientError as e:
            attempt += 1
            if attempt < retries:
                backoff_time = 2 ** attempt
                await asyncio.sleep(backoff_time)
            else:
                return 0

async def process_chunk_async(lines):
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(max_concurrent_tasks)
        
        async def sem_process_line(line):
            async with semaphore:
                return await process_line(session, line)
        
        tasks = [sem_process_line(line) for line in lines]
        scores = await asyncio.gather(*tasks)
    return sum(scores)

def process_chunk(lines):
    logger.info(f"Processing chunk with {len(lines)} lines")
    result = asyncio.run(process_chunk_async(lines))
    logger.info("Finished processing chunk")
    return result

def read_lines_in_chunks(file_path, total_lines, num_workers):
    chunk_size = total_lines // num_workers
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for worker_id in range(num_workers):
            start_line = worker_id * chunk_size
            end_line = start_line + chunk_size if worker_id < num_workers - 1 else total_lines
            yield lines[start_line:end_line]

def main():
    start_time = time.time()
    chunks = list(read_lines_in_chunks('iliad.txt', total_lines, num_workers))
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(process_chunk, chunks))
    
    total_score = sum(results)

    elapsed_time = time.time() - start_time

    logger.info(f"Total Score: {total_score}")
    logger.info(f"Elapsed Time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()