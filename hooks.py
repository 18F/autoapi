import os
import sys
import multiprocessing

sys.path.insert(0, os.getcwd())
import aws

def when_ready(server):
    pool = multiprocessing.Pool(processes=1)
    pool.apply_async(aws.fetch_bucket)
    pool.close()
