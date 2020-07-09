# Performance comparisons

## Rust API (development w/cargo watch)

### /

```bash
wrk -c 100 -d 5 -t 5 http://127.0.0.1:8000
Running 5s test @ http://127.0.0.1:8000
  5 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    91.33ms  188.90ms   1.67s    95.65%
    Req/Sec   204.84    116.64   777.00     74.00%
  5117 requests in 5.03s, 784.54KB read
  Socket errors: connect 0, read 0, write 0, timeout 8
Requests/sec:   1017.06
Transfer/sec:    155.94KB
```

### /health

```bash
wrk -c 100 -d 5 -t 5 http://127.0.0.1:8000/health
Running 5s test @ http://127.0.0.1:8000/health
  5 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   265.21ms  164.22ms   1.84s    87.92%
    Req/Sec    16.58     11.79    80.00     72.43%
  362 requests in 5.05s, 80.96KB read
  Socket errors: connect 0, read 0, write 0, timeout 6
Requests/sec:     71.74
Transfer/sec:     16.04KB
```

## Rust Release API

### /

```bash
wrk -c 100 -d 5 -t 5 http://127.0.0.1:8000
Running 5s test @ http://127.0.0.1:8000
  5 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    25.60ms   14.48ms 117.19ms   77.56%
    Req/Sec   813.45    197.62     1.28k    69.64%
  20211 requests in 5.02s, 3.03MB read
Requests/sec:   4026.84
Transfer/sec:    617.40KB
```

### /health

```bash
wrk -c 100 -d 5 -t 5 http://127.0.0.1:8000/health
Running 5s test @ http://127.0.0.1:8000/health
  5 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   356.57ms  140.21ms   1.58s    77.28%
    Req/Sec    45.82     22.34   121.00     63.52%
  1113 requests in 5.03s, 248.90KB read
Requests/sec:    221.31
Transfer/sec:     49.49KB
```

## Python (FastAPI w/Uvicorn --reload)

### /

```bash
wrk -c 100 -d 5 -t 5 http://127.0.0.1:8000
Running 5s test @ http://127.0.0.1:8000
  5 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    51.87ms    8.22ms  94.91ms   71.75%
    Req/Sec   385.16     64.08   600.00     74.40%
  9659 requests in 5.05s, 1.60MB read
Requests/sec:   1911.87
Transfer/sec:    324.87KB
```

### /health

```bash
```

## Python Release (gunicorn w/o reload)

### /

```bash
```

### /health

```bash
```

