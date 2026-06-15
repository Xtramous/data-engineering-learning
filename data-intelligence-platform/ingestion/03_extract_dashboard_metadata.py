"""
Extract dashboard metadata from JSON configuration files
"""
import logging
import json
import os
from datetime import datetime

from config.connection import ConnectionConfig, log_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample dashboard configurations
SAMPLE_DASHBOARDS = [
    {
        "id": "sales_dashboard",
        "name": "Sales Analytics Dashboard",
        "owner": "sales-team",
        "description": "Real-time sales performance and trends",
        "tables": ["sales_fact", "customer_dim", "product_dim"],
        "metrics": ["total_revenue", "avg_order_value", "sales_trend"]
    },
    {
        "id": "customer_dashboard",
        "name": "Customer Analytics Dashboard",
        "owner": "marketing-team",
        "description": "Customer demographics and behavior analysis",
        "tables": ["customer_dim", "order_fact", "sales_fact"],
        "metrics": ["total_customers", "customer_lifetime_value", "churn_rate"]
    },
    {
        "id": "product_dashboard",
        "name": "Product Performance Dashboard",
        "owner": "product-team",
        "description": "Product inventory and sales analysis",
        "tables": ["product_dim", "inventory_fact", "sales_fact"],
        "metrics": ["inventory_levels", "product_sales", "turnover_rate"]
    },
    {
        "id": "financial_dashboard",
        "name": "Financial Dashboard",
        "owner": "finance-team",
        "description": "Financial metrics and profitability analysis",
        "tables": ["sales_fact", "order_fact"],
        "metrics": ["revenue", "profit", "margin"]
    },
    {
        "id": "operations_dashboard",
        "name": "Operations Dashboard",
        "owner": "ops-team",
        "description": "Operational metrics and efficiency",
        "tables": ["inventory_fact", "order_fact"],
        "metrics": ["fulfillment_rate", "order_cycle_time", "inventory_turnover"]
    },
]


def extract_dashboard_metadata():
    """Extract and store dashboard metadata"""
    try:
        log_config()

        logger.info("Extracting dashboard metadata...")

        dashboards_dir = "ingestion/templates/dashboard_configs"
        os.makedirs(dashboards_dir, exist_ok=True)

        # Create sample dashboard config files
        logger.info(f"Creating {len(SAMPLE_DASHBOARDS)} sample dashboards...")

        for i, dashboard in enumerate(SAMPLE_DASHBOARDS, 1):
            filename = f"{dashboards_dir}/{dashboard['id']}.json"

            # Add some variety with different numbers of dashboards per owner
            dashboard_data = {
                **dashboard,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "queries": len(dashboard["metrics"]) * 3,
                "widgets": len(dashboard["metrics"]) * 2
            }

            with open(filename, 'w') as f:
                json.dump(dashboard_data, f, indent=2)

            logger.info(f"  ✓ Created {dashboard['name']}")

        # Create additional dashboards for more realistic scenario
        logger.info("Creating additional dashboards...")
        for i in range(6, 21):  # Create 15 more dashboards
            dashboard_id = f"dashboard_{i}"
            dashboard_name = f"Custom Dashboard {i}"
            owner = [
                "analytics-team", "data-team", "bi-team",
                "sales-team", "marketing-team", "finance-team"
            ][i % 6]

            dashboard_data = {
                "id": dashboard_id,
                "name": dashboard_name,
                "owner": owner,
                "description": f"Custom analytics dashboard {i}",
                "tables": [
                    ["sales_fact", "customer_dim"][i % 2],
                    ["order_fact", "product_dim"][i % 2]
                ],
                "metrics": [f"metric_{j}" for j in range(i % 5 + 1)],
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "queries": (i % 5) + 2,
                "widgets": (i % 8) + 3
            }

            filename = f"{dashboards_dir}/{dashboard_id}.json"
            with open(filename, 'w') as f:
                json.dump(dashboard_data, f, indent=2)

            logger.info(f"  ✓ Created {dashboard_name}")

        logger.info(f"✅ {len(SAMPLE_DASHBOARDS) + 15} dashboards created!")

        return True

    except Exception as e:
        logger.error(f"Error extracting dashboard metadata: {str(e)}")
        raise


if __name__ == "__main__":
    extract_dashboard_metadata()
