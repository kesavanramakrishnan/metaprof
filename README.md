# MetaProf NV (v0)

NVIDIA-first profiling layer. Unifies Nsight Compute (ncu), Nsight Systems (nsys), and (v1) CUPTI/NVML into a canonical metrics schema with high-level recipes.

## Quick start

```bash
pip install -e .
metaprof --help
```

## Layout

- `metaprof_nv/core`: runner, schemas, results normalization, parsers, metrics catalog
- `metaprof_nv/adapters`: target launch adapters (python, pytest, binary)
- `metaprof_nv/storage`: artifact store
- CLI: `metaprof_nv/cli.py`; API: `metaprof_nv/api.py`

## License
Apache-2.0
