"""
Extract table metadata from PostgreSQL
"""
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

from config.connection import ConnectionConfig, log_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_table_metadata():
    """Extract and store table metadata"""
    try:
        log_config()

        conn = psycopg2.connect(
            dbname=ConnectionConfig.PG_DATABASE,
            user=ConnectionConfig.PG_USER,
            password=ConnectionConfig.PG_PASSWORD,
            host=ConnectionConfig.PG_HOST,
            port=ConnectionConfig.PG_PORT
        )

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        logger.info("Extracting table metadata...")

        # Get all tables
        cursor.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name
        """)

        tables = cursor.fetchall()
        logger.info(f"Found {len(tables)} tables")

        for table in tables:
            schema = table['table_schema']
            table_name = table['table_name']

            # Get row count
            cursor.execute(f"SELECT COUNT(*) as cnt FROM {schema}.{table_name}")
            row_count = cursor.fetchone()['cnt']

            # Get column information
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """, (schema, table_name))

            columns = cursor.fetchall()

            logger.info(f"  Table: {schema}.{table_name}")
            logger.info(f"    - Rows: {row_count:,}")
            logger.info(f"    - Columns: {len(columns)}")
            logger.info(f"    - Owner: analytics-team")

            # Update metadata if table was created by init
            if schema == 'public':
                cursor.execute("""
                    UPDATE metadata.table_metadata
                    SET row_count = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE table_name = %s
                """, (row_count, table_name))

        conn.commit()
        logger.info("✅ Table metadata extracted successfully!")

        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"Error extracting table metadata: {str(e)}")
        raise


if __name__ == "__main__":
    extract_table_metadata()
