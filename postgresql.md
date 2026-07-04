# PostgreSQL Docker

### my-postgres

Run PostgreSQL 18 in Docker:

```powershell
docker run --name my-postgres `
  -e POSTGRES_PASSWORD=postgresdb `
  -e POSTGRES_DB=goldsavings `
  -p 5432:5432 `
  -v pgdata18:/var/lib/postgresql/data `
  -d postgres:18
```

Check container status:

```powershell
docker ps -a --filter "name=my-postgres"
```

Open psql shell:

```powershell
docker exec -it my-postgres psql -U postgres -d goldsavings
```

Recreate container:

```powershell
docker rm -f my-postgres
docker volume rm pgdata18
docker run --name my-postgres `
  -e POSTGRES_PASSWORD=postgresdb `
  -e POSTGRES_DB=goldsavings `
  -p 5432:5432 `
  -v pgdata18:/var/lib/postgresql/data `
  -d postgres:18
```
