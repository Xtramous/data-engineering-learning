"""
Auto-generate markdown documentation for all assets
"""
import logging
import os
from datetime import datetime

from config.connection import ConnectionConfig, log_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Sample documentation templates
DOCUMENTATION = {
    "tables": {
        "customer_dim": """# Customer Dimension

## Overview
The customer dimension table contains master data for all customers in the system.

## Technical Details
- **Schema**: public
- **Owner**: analytics-team
- **Row Count**: ~10,000
- **Last Updated**: Auto-updated daily

## Columns
- `customer_id` (INTEGER, Primary Key): Unique customer identifier
- `customer_name` (VARCHAR): Full name of the customer
- `email` (VARCHAR): Customer email address
- `phone` (VARCHAR): Customer phone number
- `city` (VARCHAR): Customer city
- `country` (VARCHAR): Customer country
- `signup_date` (DATE): Date customer signed up
- `is_active` (BOOLEAN): Whether customer is active
- `created_at` (TIMESTAMP): Record creation timestamp
- `updated_at` (TIMESTAMP): Record last update timestamp

## Business Description
This dimension table contains the core attributes of customers. It's used by multiple downstream processes including sales analysis and customer segmentation.

## Related Assets
- Tables: sales_fact, order_fact
- Dashboards: customer_dashboard, sales_dashboard
- DAGs: customer_etl

## SLA
- Freshness: Daily
- Availability: 99.9%
""",
        "sales_fact": """# Sales Fact Table

## Overview
Contains detailed transaction-level sales data.

## Technical Details
- **Schema**: public
- **Owner**: analytics-team
- **Row Count**: ~500,000
- **Last Updated**: Near real-time (15-minute increments)

## Columns
- `sales_id` (BIGINT, Primary Key): Unique sales transaction identifier
- `customer_id` (INTEGER, Foreign Key): Reference to customer_dim
- `product_id` (INTEGER, Foreign Key): Reference to product_dim
- `sales_date` (DATE): Date of sale
- `quantity` (INTEGER): Number of units sold
- `unit_price` (DECIMAL): Price per unit
- `total_amount` (DECIMAL): Total sale amount before discount
- `discount_amount` (DECIMAL): Discount applied
- `tax_amount` (DECIMAL): Tax applied
- `created_at` (TIMESTAMP): Record creation timestamp

## Business Description
This fact table captures every sales transaction. It's the primary source for revenue analysis, sales trends, and customer purchasing behavior.

## Related Assets
- Tables: customer_dim, product_dim
- Dashboards: sales_dashboard, financial_dashboard
- DAGs: sales_ingest

## SLA
- Freshness: 15 minutes
- Availability: 99.95%
""",
    },
    "dashboards": {
        "sales_dashboard": """# Sales Analytics Dashboard

## Purpose
Provides real-time insights into sales performance, trends, and customer behavior.

## Owner
sales-team

## Key Metrics
- Total Revenue
- Average Order Value
- Sales Trend
- Top Products
- Customer Acquisition

## Source Tables
- sales_fact
- customer_dim
- product_dim

## Refresh Schedule
- Every 4 hours

## Access
- Link: /dashboards/sales_dashboard
- Users: Sales, Analytics, Executive teams
""",
    },
    "processes": {
        "customer_etl": """# Customer ETL Process

## Overview
Daily ETL process that extracts customer data from source systems, transforms it, and loads it into the data warehouse.

## DAG Details
- **DAG ID**: customer_etl
- **Owner**: data-team
- **Schedule**: Daily at 2:00 AM UTC
- **Retries**: 2 with 5-minute backoff

## Task Flow
1. extract_customers - Extract raw customer data
2. transform_customers - Apply transformations and validations
3. load_customer_dim - Load into customer_dim table

## Source System
- raw_customers table

## Target
- customer_dim (10K rows daily)

## SLA
- Expected Runtime: 15-20 minutes
- Alerting: On failure
""",
    }
}


def create_documentation():
    """Generate markdown documentation"""
    try:
        log_config()

        logger.info("Generating documentation...")

        base_dir = "ingestion/templates/documentation"
        os.makedirs(f"{base_dir}/tables", exist_ok=True)
        os.makedirs(f"{base_dir}/dashboards", exist_ok=True)
        os.makedirs(f"{base_dir}/processes", exist_ok=True)

        # Create table documentation
        logger.info("Creating table documentation...")
        for table_name, content in DOCUMENTATION["tables"].items():
            filepath = f"{base_dir}/tables/{table_name}.md"
            with open(filepath, 'w') as f:
                f.write(content)
            logger.info(f"  ✓ Created {table_name}.md")

        # Create dashboard documentation
        logger.info("Creating dashboard documentation...")
        for dashboard_name, content in DOCUMENTATION["dashboards"].items():
            filepath = f"{base_dir}/dashboards/{dashboard_name}.md"
            with open(filepath, 'w') as f:
                f.write(content)
            logger.info(f"  ✓ Created {dashboard_name}.md")

        # Create process documentation
        logger.info("Creating process documentation...")
        for process_name, content in DOCUMENTATION["processes"].items():
            filepath = f"{base_dir}/processes/{process_name}.md"
            with open(filepath, 'w') as f:
                f.write(content)
            logger.info(f"  ✓ Created {process_name}.md")

        # Create business glossary
        logger.info("Creating business glossary...")
        glossary_content = """# Business Glossary

## Metrics & KPIs

### Revenue
Total monetary value of all sales transactions.

### Customer Lifetime Value (CLV)
The total net profit attributed to the entire future relationship with a customer.

### Churn Rate
The percentage of customers who stopped using our services during a given period.

### Inventory Turnover
The number of times inventory is sold and replaced over a period.

### Order Cycle Time
The average time from order placement to delivery.

## Data Entities

### Customer
An individual or organization that purchases our products or services.

### Product
An item or service that we offer for sale.

### Sales Transaction
A single purchase event recording the sale of one or more products to a customer.

### Order
A grouping of sales transactions from a single customer in a single session.

### Inventory
Stock levels of products across warehouse locations.

## Ownership Model

### analytics-team
Responsible for all core analytics tables and fact tables.

### data-team
Responsible for ETL processes and data quality.

### bi-team
Responsible for dashboard development and BI tools.

### finance-team
Responsible for financial reporting and reconciliation.
"""

        glossary_path = f"{base_dir}/GLOSSARY.md"
        with open(glossary_path, 'w') as f:
            f.write(glossary_content)
        logger.info(f"  ✓ Created GLOSSARY.md")

        # Create data dictionary
        logger.info("Creating data dictionary...")
        data_dict_content = """# Data Dictionary

## Table Schemas

### customer_dim
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| customer_id | INTEGER | No | Unique customer ID |
| customer_name | VARCHAR(255) | No | Full customer name |
| email | VARCHAR(255) | Yes | Customer email |
| phone | VARCHAR(20) | Yes | Customer phone |
| city | VARCHAR(100) | Yes | City of residence |
| country | VARCHAR(100) | Yes | Country of residence |
| signup_date | DATE | Yes | Date of signup |
| is_active | BOOLEAN | Yes | Active status |
| created_at | TIMESTAMP | No | Creation timestamp |
| updated_at | TIMESTAMP | No | Update timestamp |

### sales_fact
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| sales_id | BIGINT | No | Unique sales ID |
| customer_id | INTEGER | No | Reference to customer |
| product_id | INTEGER | No | Reference to product |
| sales_date | DATE | No | Date of sale |
| quantity | INTEGER | No | Units sold |
| unit_price | DECIMAL | No | Price per unit |
| total_amount | DECIMAL | No | Total before discount |
| discount_amount | DECIMAL | Yes | Discount given |
| tax_amount | DECIMAL | Yes | Tax applied |
| created_at | TIMESTAMP | No | Creation timestamp |

## View & Aggregate Definitions

### vw_sales_by_customer
Monthly sales aggregated by customer. Used for CLV calculations.

### vw_product_performance
Product-level metrics including sales, inventory, and profitability.
"""

        data_dict_path = f"{base_dir}/DATA_DICTIONARY.md"
        with open(data_dict_path, 'w') as f:
            f.write(data_dict_content)
        logger.info(f"  ✓ Created DATA_DICTIONARY.md")

        logger.info(f"✅ Documentation generated successfully!")

        return True

    except Exception as e:
        logger.error(f"Error creating documentation: {str(e)}")
        raise


if __name__ == "__main__":
    create_documentation()
