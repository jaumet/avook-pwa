# Backing Up Your Audiovook Instance

This guide provides simple instructions for manually backing up the critical data of your Audiovook instance: the PostgreSQL database and the local S3 object store provided by LocalStack.

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

## 2. Backing Up the S3 Bucket

The S3 bucket contains all the media files, such as audiobook chapters (HLS segments) and cover images. We will use the AWS CLI to sync the contents of the bucket to a local directory.

**Note:** This requires the `aws` CLI installed on your local machine. Installation instructions can be found here: [https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

**Step 1: Sync the bucket**
This command will copy the entire contents of the `audiovook-test` bucket to a local directory named `s3_backup`.
```bash
# This will create a 's3_backup' directory if it doesn't exist
aws --endpoint-url http://localhost:9000 s3 sync s3://audiovook-test ./s3_backup
```

The `aws s3 sync` command is idempotent, meaning you can run it repeatedly and it will only copy new or updated files, making it efficient for regular backups.
