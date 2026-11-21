Deploying is easy:
1. put POSTGRES_PASSWORD in .env
2. docker compose up -d
3. dashboard: I built web/ and copied dist/ into the VM's nginx, it's at http://10.20.0.15:8080
4. API is on http://10.20.0.15:8000

Works perfectly on my laptop with `admitflow serve`.
