// Create constraints
CREATE CONSTRAINT table_name_unique IF NOT EXISTS FOR (t:Table) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT column_name_unique IF NOT EXISTS FOR (c:Column) REQUIRE (c.table_name, c.name) IS UNIQUE;
CREATE CONSTRAINT dashboard_id_unique IF NOT EXISTS FOR (d:Dashboard) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT job_name_unique IF NOT EXISTS FOR (j:Job) REQUIRE j.name IS UNIQUE;

// Create indexes
CREATE INDEX table_owner IF NOT EXISTS FOR (t:Table) ON (t.owner);
CREATE INDEX table_schema IF NOT EXISTS FOR (t:Table) ON (t.schema);
CREATE INDEX column_type IF NOT EXISTS FOR (c:Column) ON (c.type);
CREATE INDEX job_status IF NOT EXISTS FOR (j:Job) ON (j.status);

// Note: Actual data will be inserted by Python ingestion scripts
// This file sets up the schema and constraints
