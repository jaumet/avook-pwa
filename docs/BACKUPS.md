# Backing Up Your Audiovook Instance

This guide provides simple instructions for manually backing up the critical data of your Audiovook instance: the PostgreSQL database and the S3 object store (MinIO).

It is recommended to perform these backups regularly.

## 1. Backing Up the PostgreSQL Database

The database contains all the information about users, titles, products, QR codes, and listening progress. We will use `docker compose exec` to run the `pg_dump` command inside the running `db` container.

**Command:**
```bash
# Make sure you are in the root directory of the project
docker compose -f infra/docker-compose.yml exec -T db pg_dump -U user -d avook > backup_avook_db_$(date +%Y-%m-%d).sql
```

**Explanation:**
- `docker compose ... exec -T db`: Executes a command inside the `db` container without allocating a pseudo-TTY.
- `pg_dump -U user -d avook`: The standard PostgreSQL utility to dump a database's contents. `-U user` specifies the user and `-d avook` specifies the database name, as configured in `docker-compose.yml`.
- `> backup_avook_db_... .sql`: This redirects the output of the command to a new SQL file on your local machine, timestamped with the current date.

To restore from this backup, you would typically use the `psql` command.

## 2. Backing Up the S3 Bucket (MinIO)

The S3 bucket contains all the media files, such as audiobook chapters (HLS segments) and cover images. We will use the MinIO Client (`mc`) to mirror the contents of the bucket to a local directory.

**Note:** This requires you to have the `mc` client installed on your local machine. If you don't, you can find installation instructions here: [https://min.io/docs/minio/linux/reference/minio-client.html](https://min.io/docs/minio/linux/reference/minio-client.html)

**Step 1: Configure a local alias for your MinIO instance**
This only needs to be done once.
```bash
mc alias set local-minio http://localhost:9000 minioadmin minioadmin
```
This command tells `mc` how to connect to your local MinIO server running in Docker.

**Step 2: Mirror the bucket**
This command will copy the entire contents of the `avook` bucket to a local directory named `s3_backup`.
```bash
# This will create a 's3_backup' directory if it doesn't exist
mc mirror local-minio/avook ./s3_backup
```

The `mc mirror` command is idempotent, meaning you can run it repeatedly, and it will only copy new or updated files, making it efficient for regular backups.
