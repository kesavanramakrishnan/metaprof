# WarpLens NV (v0)

NVIDIA-first profiling layer you can drop under SwizzlePerf. Unifies Nsight Compute (ncu), Nsight Systems (nsys), and (v1) CUPTI/NVML into a canonical metrics schema with high-level recipes.

## Quick start

```bash
pip install -e .
warplens --help
```

## Layout

- `warplens_nv/core`: runner, schemas, results normalization, parsers, metrics catalog
- `warplens_nv/adapters`: target launch adapters (python, pytest, binary)
- `warplens_nv/storage`: artifact store
- CLI: `warplens_nv/cli.py`; API: `warplens_nv/api.py`

## License
Apache-2.0
