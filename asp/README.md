# Encodings

This folder contains 5 encodings which focus on malfunction handling.

## `graph_reschedule`and `graph_reschedule_naive`
They are simple timestepped graph approaches and use the worst case assumption to replan on malfunction.
The naive encoding just passes information differently. It passes the environment predicates instead of the computed graph.

## `graph_subcelld` and `graph_subcelld_naive`
They are two encodings aiming to reduce everything necessary from the previous ones. (Not completely functional right now.)

## `incremental`
It is the up to now, best approach and implements a hybrid approach, of using the given estimate for the first plan and only adding timesteps, when necessary.


---
All `params.py` files herein will be automatically used by `benchmark.py`.