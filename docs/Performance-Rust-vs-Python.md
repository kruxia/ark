# Performance comparisons

tldr; **Rust/Actix** --release **is 2x—10x faster than Python/Starlette** w/o --reload.
That seems like a very reasonable tradeoff for significantly faster development time
(10x—50x faster). Python becomes an excellent prototyping environment, and we can move
to Rust if and when performance demands.

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

## Python (Starlette w/Uvicorn --reload)

### /

```bash
wrk -c 100 -d 5 -t 5 http://127.0.0.1:8000
Running 5s test @ http://127.0.0.1:8000
  5 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    42.37ms   20.31ms 183.24ms   77.71%
    Req/Sec   484.21    149.12   800.00     67.34%
  12004 requests in 5.02s, 1.97MB read
Requests/sec:   2391.58
Transfer/sec:    401.71KB
```

### /health

```bash
wrk -c 100 -d 5 -t 5 http://127.0.0.1:8000/health
Running 5s test @ http://127.0.0.1:8000/health
  5 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.30s   482.05ms   1.90s    53.49%
    Req/Sec     9.67      8.12    40.00     70.83%
  117 requests in 5.07s, 27.42KB read
  Socket errors: connect 0, read 0, write 0, timeout 74
Requests/sec:     23.08
Transfer/sec:      5.41KB
```

## Python Release (uvicorn w/o reload)

### /

```bash
wrk -c 100 -d 5 -t 5 http://127.0.0.1:8000
Running 5s test @ http://127.0.0.1:8000
  5 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    36.11ms   15.05ms 149.87ms   75.89%
    Req/Sec   561.44    151.93     0.92k    68.27%
  13985 requests in 5.02s, 2.29MB read
Requests/sec:   2784.34
Transfer/sec:    467.68KB
```

### /health

```bash
wrk -c 100 -d 5 -t 5 http://127.0.0.1:8000/health
Running 5s test @ http://127.0.0.1:8000/health
  5 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.04s   455.63ms   1.96s    48.33%
    Req/Sec     9.86      7.32    30.00     72.92%
  152 requests in 5.08s, 35.62KB read
  Socket errors: connect 0, read 0, write 0, timeout 92
Requests/sec:     29.90
Transfer/sec:      7.01KB
```

