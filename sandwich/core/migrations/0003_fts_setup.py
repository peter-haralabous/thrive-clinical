from django.db import migrations

# This sql was originally written for sqlite by Neil
# and then refactored by raoul to support uuids.
# i've asked claude 4 to conver it to postgresql 
# compatible sql since the 2 systems have different
# approaches to full text search.
# https://github.com/thrivehealth/sandwich/blob/63b4ed9019624bb7341b1b577257d32c5977dad0/sandwich/core/migrations/0012_fts_setup.py
# https://github.com/thrivehealth/sandwich/blob/63b4ed9019624bb7341b1b577257d32c5977dad0/sandwich/core/migrations/0014_update_fts_for_uuid.py
CREATE_PATIENT_FTS = """
-- Create FTS table for PostgreSQL with tsvector for full-text search
CREATE TABLE core_patient_fts (
    patient_uuid UUID PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    phn TEXT,
    email TEXT,
    search_vector tsvector
);

-- Create GIN index for efficient full-text search
CREATE INDEX core_patient_fts_search_idx ON core_patient_fts USING GIN(search_vector);

-- Create trigger functions for FTS operations
CREATE OR REPLACE FUNCTION insert_patient_fts()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO core_patient_fts(patient_uuid, first_name, last_name, phn, email, search_vector)
    VALUES (
        NEW.id, NEW.first_name, NEW.last_name, NEW.phn, NEW.email,
        setweight(to_tsvector('english', COALESCE(NEW.first_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.last_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.phn, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.email, '')), 'C')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_patient_fts()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM core_patient_fts WHERE patient_uuid = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_patient_fts()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE core_patient_fts SET
        first_name = NEW.first_name,
        last_name = NEW.last_name,
        phn = NEW.phn,
        email = NEW.email,
        search_vector = setweight(to_tsvector('english', COALESCE(NEW.first_name, '')), 'A') ||
                       setweight(to_tsvector('english', COALESCE(NEW.last_name, '')), 'A') ||
                       setweight(to_tsvector('english', COALESCE(NEW.phn, '')), 'B') ||
                       setweight(to_tsvector('english', COALESCE(NEW.email, '')), 'C')
    WHERE patient_uuid = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers that work with UUID primary keys
CREATE TRIGGER core_patient_after_insert
    AFTER INSERT ON core_patient
    FOR EACH ROW
    EXECUTE FUNCTION insert_patient_fts();

CREATE TRIGGER core_patient_after_delete
    AFTER DELETE ON core_patient
    FOR EACH ROW
    EXECUTE FUNCTION delete_patient_fts();

CREATE TRIGGER core_patient_after_update
    AFTER UPDATE ON core_patient
    FOR EACH ROW
    EXECUTE FUNCTION update_patient_fts();

-- Populate FTS table with existing data
INSERT INTO core_patient_fts(patient_uuid, first_name, last_name, phn, email, search_vector)
SELECT 
    id, first_name, last_name, phn, email,
    setweight(to_tsvector('english', COALESCE(first_name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(last_name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(phn, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(email, '')), 'C')
FROM core_patient;
"""

DROP_PATIENT_FTS = """
-- Drop PostgreSQL FTS table, triggers, and functions
DROP TRIGGER IF EXISTS core_patient_after_update ON core_patient;
DROP TRIGGER IF EXISTS core_patient_after_delete ON core_patient;
DROP TRIGGER IF EXISTS core_patient_after_insert ON core_patient;
DROP FUNCTION IF EXISTS update_patient_fts();
DROP FUNCTION IF EXISTS delete_patient_fts();
DROP FUNCTION IF EXISTS insert_patient_fts();
DROP INDEX IF EXISTS core_patient_fts_search_idx;
DROP TABLE IF EXISTS core_patient_fts;
"""


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_initial'),
    ]

    operations = [
        migrations.RunSQL(sql=CREATE_PATIENT_FTS, reverse_sql=DROP_PATIENT_FTS)
    ]
