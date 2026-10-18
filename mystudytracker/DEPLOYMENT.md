# Deployment

## Vercel project setup

Set the Vercel project's **Root Directory** to `mystudytracker` (the directory
containing `manage.py` and `vercel.json`). Do not put database migrations in
the Vercel request handler: serverless instances can start concurrently, and
the database must be migrated once as a release step.

Configure these Vercel environment variables for Production (and Preview only
when Preview should use its own database):

- `DJANGO_SECRET_KEY`: a newly generated, private Django secret.
- `DATABASE_URL`: the connection URL for a persistent PostgreSQL database.
- `DJANGO_DEBUG`: `False`.

Vercel deployments intentionally fail fast if either required secret/database
setting is missing. SQLite is only a local development default; it is
ephemeral on serverless deployments and must not be used for production data.
Static assets are collected by the configured Vercel build command.

## Applying the missing DailyLog migration

Migration `track.0002_dailylog_evening_not_studied_and_more` already adds both
`morning_not_studied` and `evening_not_studied`. The reported missing column
means that migration has not been applied to the database used by the deployed
application, or Vercel is connected to a different database.

Before changing production, confirm `DATABASE_URL` points to the intended
database and take a database backup if its data matters. Run the following
from this directory in a trusted environment where `DATABASE_URL` is set to
that production database:

```powershell
python manage.py showmigrations track
python manage.py migrate --plan
python manage.py migrate
python manage.py showmigrations track
```

The final output should show `[X]` for `0002_dailylog_evening_not_studied_and_more`.
Run the migration once, not concurrently from multiple deployment/build
processes. If it is already marked applied but PostgreSQL still reports a
missing column, verify the database URL and inspect the production schema
before considering any repair; do not delete or recreate the database.

After configuring Vercel and applying the migration, redeploy and test the
dashboard and a daily log. For local development, use the default SQLite
database and run `python manage.py migrate`.
