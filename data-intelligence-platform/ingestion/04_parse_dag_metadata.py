"""
Parse Airflow DAG metadata and create sample DAG configurations
"""
import logging
import os
from datetime import datetime

from config.connection import ConnectionConfig, log_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Sample DAG templates
SAMPLE_DAGS = [
    {
        "dag_id": "customer_etl",
        "owner": "data-team",
        "schedule": "0 2 * * *",
        "description": "Daily customer dimension ETL",
        "tasks": ["extract_customers", "transform_customers", "load_customer_dim"],
        "source_tables": ["raw_customers"],
        "target_tables": ["customer_dim"],
    },
    {
        "dag_id": "product_etl",
        "owner": "data-team",
        "schedule": "0 3 * * *",
        "description": "Daily product dimension ETL",
        "tasks": ["extract_products", "transform_products", "load_product_dim"],
        "source_tables": ["raw_products"],
        "target_tables": ["product_dim"],
    },
    {
        "dag_id": "sales_ingest",
        "owner": "analytics-team",
        "schedule": "*/15 * * * *",
        "description": "Ingest sales transactions every 15 minutes",
        "tasks": ["extract_sales", "validate_sales", "load_sales_fact"],
        "source_tables": ["raw_sales"],
        "target_tables": ["sales_fact"],
    },
    {
        "dag_id": "order_processing",
        "owner": "analytics-team",
        "schedule": "0 * * * *",
        "description": "Process and aggregate orders hourly",
        "tasks": ["fetch_orders", "deduplicate_orders", "load_order_fact"],
        "source_tables": ["raw_orders"],
        "target_tables": ["order_fact"],
    },
    {
        "dag_id": "inventory_sync",
        "owner": "ops-team",
        "schedule": "*/30 * * * *",
        "description": "Sync warehouse inventory every 30 minutes",
        "tasks": ["read_warehouse_api", "transform_inventory", "load_inventory_fact"],
        "source_tables": ["warehouse_api"],
        "target_tables": ["inventory_fact"],
    },
    {
        "dag_id": "data_quality_checks",
        "owner": "data-team",
        "schedule": "0 4 * * *",
        "description": "Run daily data quality checks",
        "tasks": ["check_nulls", "check_duplicates", "check_ranges", "alert_if_failed"],
        "source_tables": ["customer_dim", "product_dim", "sales_fact", "order_fact"],
        "target_tables": ["quality_report"],
    },
    {
        "dag_id": "reconciliation",
        "owner": "finance-team",
        "schedule": "0 5 * * 0",
        "description": "Weekly financial reconciliation",
        "tasks": ["reconcile_sales", "reconcile_orders", "generate_report"],
        "source_tables": ["sales_fact", "order_fact"],
        "target_tables": ["reconciliation_summary"],
    },
    {
        "dag_id": "dashboard_refresh",
        "owner": "bi-team",
        "schedule": "0 */4 * * *",
        "description": "Refresh all BI dashboards every 4 hours",
        "tasks": ["refresh_cache", "update_aggregates", "notify_users"],
        "source_tables": ["sales_fact", "customer_dim"],
        "target_tables": [],
    },
    {
        "dag_id": "model_retraining",
        "owner": "ml-team",
        "schedule": "0 6 * * 0",
        "description": "Retrain ML models weekly",
        "tasks": ["prepare_training_data", "train_model", "evaluate_model", "deploy_model"],
        "source_tables": ["sales_fact", "customer_dim"],
        "target_tables": ["model_metadata"],
    },
    {
        "dag_id": "archive_old_data",
        "owner": "data-team",
        "schedule": "0 0 1 * *",
        "description": "Archive old data monthly",
        "tasks": ["identify_old_data", "compress_data", "archive_to_s3"],
        "source_tables": ["sales_fact", "order_fact"],
        "target_tables": [],
    },
]


def parse_dag_metadata():
    """Parse and store DAG metadata"""
    try:
        log_config()

        logger.info("Parsing Airflow DAG metadata...")

        dag_dir = "ingestion/templates/dag_configs"
        os.makedirs(dag_dir, exist_ok=True)

        # Create sample DAG Python files
        logger.info(f"Creating {len(SAMPLE_DAGS)} sample DAG configurations...")

        for dag_config in SAMPLE_DAGS:
            dag_id = dag_config["dag_id"]
            filename = f"{dag_dir}/{dag_id}.py"

            # Generate a simple DAG Python file
            dag_code = f'''"""
{dag_config['description']}
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {{
    "owner": "{dag_config['owner']}",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2024, 1, 1),
}}

dag = DAG(
    "{dag_id}",
    default_args=default_args,
    description="{dag_config['description']}",
    schedule_interval="{dag_config['schedule']}",
    catchup=False,
)

# Tasks
'''

            # Add task definitions
            for i, task_name in enumerate(dag_config["tasks"]):
                dag_code += f'''
{task_name} = PythonOperator(
    task_id="{task_name}",
    python_callable=lambda: print("Executing {task_name}"),
    dag=dag,
)
'''

            # Add task dependencies
            if len(dag_config["tasks"]) > 1:
                dag_code += f"\n# Dependencies\n"
                for i in range(len(dag_config["tasks"]) - 1):
                    dag_code += f"{dag_config['tasks'][i]} >> {dag_config['tasks'][i+1]}\n"

            with open(filename, 'w') as f:
                f.write(dag_code)

            logger.info(f"  ✓ Created {dag_id}: {dag_config['description']}")

        logger.info(f"✅ {len(SAMPLE_DAGS)} DAG configurations created!")

        # Log DAG metadata
        logger.info("\n📊 DAG Summary:")
        for dag in SAMPLE_DAGS:
            logger.info(f"  {dag['dag_id']}")
            logger.info(f"    Owner: {dag['owner']}, Schedule: {dag['schedule']}")
            logger.info(f"    Sources: {', '.join(dag['source_tables'])}")
            logger.info(f"    Targets: {', '.join(dag['target_tables']) if dag['target_tables'] else 'N/A'}")

        return True

    except Exception as e:
        logger.error(f"Error parsing DAG metadata: {str(e)}")
        raise


if __name__ == "__main__":
    parse_dag_metadata()
