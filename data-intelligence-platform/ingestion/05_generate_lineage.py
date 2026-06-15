"""
Generate data lineage from SQL files and create Neo4j graph
"""
import logging
from neo4j import GraphDatabase

from config.connection import ConnectionConfig, log_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Predefined lineage relationships
LINEAGE_MAPPINGS = [
    {
        "source_table": "raw_customers",
        "target_table": "customer_dim",
        "dag": "customer_etl",
        "description": "Customer dimension transformation"
    },
    {
        "source_table": "raw_products",
        "target_table": "product_dim",
        "dag": "product_etl",
        "description": "Product dimension transformation"
    },
    {
        "source_table": "raw_sales",
        "target_table": "sales_fact",
        "dag": "sales_ingest",
        "description": "Sales transaction ingestion"
    },
    {
        "source_table": "raw_orders",
        "target_table": "order_fact",
        "dag": "order_processing",
        "description": "Order fact table creation"
    },
    {
        "source_table": "warehouse_api",
        "target_table": "inventory_fact",
        "dag": "inventory_sync",
        "description": "Inventory synchronization"
    },
    {
        "source_table": "customer_dim",
        "target_table": "sales_fact",
        "relationship": "USED_BY",
        "description": "Customer dimension used in sales"
    },
    {
        "source_table": "product_dim",
        "target_table": "sales_fact",
        "relationship": "USED_BY",
        "description": "Product dimension used in sales"
    },
    {
        "source_table": "customer_dim",
        "target_table": "order_fact",
        "relationship": "USED_BY",
        "description": "Customer dimension used in orders"
    },
    {
        "source_table": "sales_fact",
        "target_table": "sales_dashboard",
        "relationship": "FEEDS_INTO",
        "description": "Sales data feeds dashboard"
    },
    {
        "source_table": "customer_dim",
        "target_table": "customer_dashboard",
        "relationship": "FEEDS_INTO",
        "description": "Customer data feeds dashboard"
    },
]


def generate_lineage():
    """Generate and store lineage in Neo4j"""
    try:
        log_config()

        logger.info("Generating data lineage...")

        # Connect to Neo4j
        driver = GraphDatabase.driver(
            ConnectionConfig.get_neo4j_uri(),
            auth=(ConnectionConfig.NEO4J_USER, ConnectionConfig.NEO4J_PASSWORD)
        )

        with driver.session() as session:
            # Clear existing data (optional, for fresh start)
            logger.info("Clearing existing lineage data...")
            session.run("MATCH (n) DETACH DELETE n")

            # Create table nodes
            logger.info("Creating table nodes...")
            for mapping in LINEAGE_MAPPINGS:
                for table in [mapping.get("source_table"), mapping.get("target_table")]:
                    if table and not table.endswith("dashboard"):
                        session.run(
                            """
                            MERGE (t:Table {name: $name})
                            SET t.type = 'table', t.owner = 'data-team'
                            """,
                            name=table
                        )
                logger.info(f"  ✓ Created nodes for {mapping.get('source_table')} and {mapping.get('target_table')}")

            # Create dashboard nodes
            logger.info("Creating dashboard nodes...")
            dashboards = ["sales_dashboard", "customer_dashboard", "product_dashboard", "financial_dashboard", "operations_dashboard"]
            for dashboard in dashboards:
                session.run(
                    """
                    MERGE (d:Dashboard {name: $name})
                    SET d.type = 'dashboard', d.owner = 'bi-team'
                    """,
                    name=dashboard
                )
            logger.info(f"  ✓ Created {len(dashboards)} dashboard nodes")

            # Create relationships
            logger.info("Creating lineage relationships...")
            for mapping in LINEAGE_MAPPINGS:
                source = mapping.get("source_table")
                target = mapping.get("target_table")
                relationship = mapping.get("relationship", "FEEDS_INTO")

                if source and target:
                    if target.endswith("dashboard"):
                        session.run(
                            f"""
                            MATCH (s:Table {{name: $source}})
                            MATCH (t:Dashboard {{name: $target}})
                            MERGE (s)-[:{relationship} {{description: $description}}]->(t)
                            """,
                            source=source,
                            target=target,
                            description=mapping.get("description", "")
                        )
                    else:
                        session.run(
                            f"""
                            MATCH (s:Table {{name: $source}})
                            MATCH (t:Table {{name: $target}})
                            MERGE (s)-[:{relationship} {{description: $description}}]->(t)
                            """,
                            source=source,
                            target=target,
                            description=mapping.get("description", "")
                        )

                logger.info(f"  ✓ {source} -{relationship}-> {target}")

            # Verify lineage
            logger.info("\nVerifying lineage...")
            result = session.run("MATCH (n) RETURN COUNT(n) as count")
            count = result.single()["count"]
            logger.info(f"  Total nodes created: {count}")

            result = session.run("MATCH ()-[r]->() RETURN COUNT(r) as count")
            rel_count = result.single()["count"]
            logger.info(f"  Total relationships created: {rel_count}")

        driver.close()
        logger.info("✅ Lineage generated successfully!")

        return True

    except Exception as e:
        logger.error(f"Error generating lineage: {str(e)}")
        raise


if __name__ == "__main__":
    generate_lineage()
