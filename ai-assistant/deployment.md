# AI Assistance — `docker-compose.yml` · `Dockerfile` · `.github/workflows/`

## Files Covered
- `Dockerfile` — builds the application container image
- `docker-compose.yml` — defines MongoDB, Dashboard, and Collector services
- `.github/workflows/ci-cd.yml` — test → build → push → deploy pipeline
- `.github/workflows/collect_data.yml` — scheduled data collection every 6 hours

---

## Dockerfile

### What AI Helped With
AI wrote the multi-stage-friendly Dockerfile using `python:3.11-slim` as the base
image and installing dependencies from `requirements.txt` before copying application
code (so Docker layer caching works efficiently):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
The `--server.address=0.0.0.0` flag is important — without it Streamlit only listens
on localhost inside the container and the port mapping does not work.

**My decision:** I chose `python:3.11-slim` over the full Python image to keep the
image smaller (faster pulls on the Azure VM). AI implemented this after I asked for a
lightweight base.

---

## docker-compose.yml

### What AI Helped With

**Three-Service Architecture**
AI designed the three services: `mongodb`, `dashboard`, and `collector`. The key
decisions AI made technically:

- `depends_on` with `condition: service_healthy` so dashboard and collector only start
  after MongoDB is confirmed healthy (not just started)
- MongoDB healthcheck using `mongosh --eval "db.adminCommand('ping')"` which is the
  correct command for MongoDB 7.0 (older `mongo` command does not exist)
- `restart: always` on mongodb and dashboard so they recover after Azure VM reboots

**Collector Profiles Pattern**
AI used Docker Compose `profiles: [collect]` on the collector service so it does not
start automatically with `docker compose up`. It only runs when explicitly triggered:
```bash
docker compose --profile collect run --rm collector
```
The `--rm` flag removes the container after it exits, so there are no leftover stopped
containers accumulating on the VM.

**My decision:** I identified the problem of the collector running continuously vs.
the dashboard which should always be running. AI suggested the profiles pattern as the
solution. I confirmed this was the right approach.

**Image Pull Instead of Build**
Originally AI generated `build: context: .` which would try to build the image on the
VM. I corrected this to `image: muneebbukhari555/github-pipeline-analysis:latest`
because the CI/CD pipeline already builds and pushes to Docker Hub — the VM should
only pull.

**Docker Internal Networking**
AI configured `MONGO_URI=mongodb://mongodb:27017` using the Docker service name as the
hostname. This works because both containers are on the same Docker Compose network,
so container names resolve as hostnames. Using `localhost` would fail because each
container has its own localhost.

---

## .github/workflows/ci-cd.yml

### What AI Helped With

**Three-Job Pipeline Structure**
AI structured three jobs with explicit dependencies:
1. `test` — runs pytest
2. `build-and-push` — builds Docker image and pushes to Docker Hub (only if tests pass)
3. `deploy` — SSHs into Azure VM and updates running containers (only if build succeeds)

**SSH Deployment Step**
AI used `appleboy/ssh-action@v1.0.3` to SSH into the Azure VM and run the deployment
commands remotely. The `.env` file is written on the VM from GitHub Secrets:
```yaml
cat > .env << 'ENVEOF'
GITHUB_TOKEN=${{ secrets.GH_API_TOKEN }}
MONGO_URI=mongodb://mongodb:27017
MONGO_DB=github_pipeline_analysis
ENVEOF
```
This avoids committing the `.env` file to the repository while still making secrets
available at runtime on the VM.

**My decision:** I corrected AI's initial use of `AWS_*` secret names to `AZURE_*`
because the VM is on Azure (with a PEM key), not AWS. I also identified that the VM
should pull from Docker Hub, not build — and corrected the deploy step accordingly.

---

## .github/workflows/collect_data.yml

### What AI Helped With
AI set up the cron schedule and the SSH collect step:
```yaml
on:
  schedule:
    - cron: '0 */6 * * *'
```
This runs at 00:00, 06:00, 12:00, and 18:00 UTC every day. AI wrote the SSH step
that SSHs into the Azure VM and runs only the collector container, then exits.

**My decision:** I chose the 6-hour frequency as a balance between data freshness and
GitHub API rate limit consumption. More frequent collection would exhaust the token
quota (5,000 requests/hour for authenticated requests, and each full collection uses
several hundred).

---

## What I Did

- Identified that the VM should pull images not build them (corrected AI)
- Corrected AWS secret names to Azure throughout both workflow files
- Chose 6-hour collection frequency based on API rate limit reasoning
- Decided on the three-service architecture (MongoDB + Dashboard + Collector)
- Specified that the collector should run-and-exit (not stay running like the dashboard)
- Understood Docker internal networking and verified `mongodb://mongodb:27017` is correct

---

## AI Tool Used
AI assistant — used for Docker Compose syntax, GitHub Actions YAML structure,
and SSH deployment patterns. Architecture decisions, frequency settings, and Azure
corrections were mine.
