#!/bin/bash

# This script sets up PostgreSQL database and user for the Job Board application.
# It checks if PostgreSQL is installed, starts the service if not running,
# and creates a database and user if they do not exist.

# Variables
DB_NAME="jobboard_db"
DB_USER="jobboard_user"
DB_PASSWORD="@Boomerang231"
PG_SERVICE="postgresql@17"
POSTGRES_USER="ansa"  # The system user with access to PostgreSQL

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Installing now..."
    # Install PostgreSQL based on OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update && sudo apt install -y postgresql postgresql-contrib
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install postgresql
        brew services start postgresql
    else
        echo "Unsupported OS. Please install PostgreSQL manually."
        exit 1
    fi
else
    echo "PostgreSQL is already installed."
fi

# Ensure PostgreSQL service is running
if ! pg_isready -q; then
    echo "Starting PostgreSQL service..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start "$PG_SERVICE"
    else
        sudo systemctl start postgresql
    fi
fi

# Check if the database exists
DB_EXISTS=$(psql -d postgres -U "$POSTGRES_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';")

if [[ $DB_EXISTS != 1 ]]; then
    echo "Database $DB_NAME does not exist. Creating..."
    psql -d postgres -U "$POSTGRES_USER" -c "CREATE DATABASE $DB_NAME;"
    echo "Database $DB_NAME created."
else
    echo "Database $DB_NAME already exists."
fi

# Check if the user exists
USER_EXISTS=$(psql -d postgres -U "$POSTGRES_USER" -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER';")

if [[ $USER_EXISTS != 1 ]]; then
    echo "User $DB_USER does not exist. Creating..."
    psql -d postgres -U "$POSTGRES_USER" -c "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';"
    echo "User $DB_USER created."
else
    echo "User $DB_USER already exists."
fi

# Grant necessary privileges to the user
echo "Ensuring user $DB_USER has the required privileges on database $DB_NAME..."

# Allow the user to connect to the database
psql -d "$DB_NAME" -U "$POSTGRES_USER" -c "GRANT CONNECT ON DATABASE $DB_NAME TO $DB_USER;"

# Allow the user to create temporary tables
psql -d postgres -U "$POSTGRES_USER" -c "GRANT TEMPORARY ON DATABASE $DB_NAME TO $DB_USER;"

# Allow the user to create new databases (if needed)
psql -d postgres -U "$POSTGRES_USER" -c "ALTER USER $DB_USER WITH CREATEDB;"

# Allow schema usage and basic operations
psql -d "$DB_NAME" -U "$POSTGRES_USER" -c "GRANT USAGE ON SCHEMA public TO $DB_USER;"
psql -d "$DB_NAME" -U "$POSTGRES_USER" -c "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO $DB_USER;"
psql -d "$DB_NAME" -U "$POSTGRES_USER" -c "GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO $DB_USER;"
psql -d "$DB_NAME" -U "$POSTGRES_USER" -c "GRANT CREATE ON SCHEMA public TO $DB_USER;"

# Set default role parameters for the user
psql -d "$DB_NAME" -U "$POSTGRES_USER" -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
psql -d "$DB_NAME" -U "$POSTGRES_USER" -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
psql -d "$DB_NAME" -U "$POSTGRES_USER" -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"

echo "Privileges successfully assigned to $DB_USER."

echo "PostgreSQL setup completed successfully!"
