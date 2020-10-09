import multiprocessing

MemPool = multiprocessing.Queue()
discarded_txs = multiprocessing.Queue()