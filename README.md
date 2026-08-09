# Fio Hairstyles CRM

FastAPI (+ Mangum) backend and Next.js frontend for appointments, clients,
and income tracking — same architecture/style as the `worth` app.

- `api/` — FastAPI backend. See `api/run_local.sh` (uses `uv`).
- `ui/` — Next.js frontend. See `ui/run_local.sh` (uses `npm`).

## Running locally

```
cd api && ./run_local.sh   # http://localhost:8000
cd ui && ./run_local.sh    # http://localhost:3000
```

## Dynamo data architecture

- `pk=Client` `sk=client_id (uuid4)` — one item per client.
- `pk=Appointment#{YYYY-MM}` `sk=ServiceDateTime (ISO 8601)` — appointments,
  partitioned by month for the Appointments/Calendar pages' monthly queries.
