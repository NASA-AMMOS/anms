#!/usr/bin/env python3
"""
Seed script for creating realistic OpenSearch and Grafana data.

Creates:
- OpenSearch indices with test data (reports, metrics, logs)
- Grafana dashboard definitions (if accessible)
- Datasource configurations for OpenSearch

Usage:
    cd ~/anms/anms-ui/integration_test
    python tests/seed/seed_dashboard.py [--count N] [--reset]

Options:
    --count N    Number of documents to create (default: 500)
    --reset      Clear test indices before seeding
"""

import os
import sys
import json
import random
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

# OpenSearch connection config
OPENSEARCH_URL = os.environ.get('OPENSEARCH_URL', 'https://localhost:9200')
OPENSEARCH_USER = os.environ.get('OPENSEARCH_USER', 'admin')
OPENSEARCH_PASS = os.environ.get('OPENSEARCH_PASS', 'Str0ng!Pass#2026')

GRAFANA_URL = os.environ.get('GRAFANA_URL', 'http://localhost:3000')
GRAFANA_USER = os.environ.get('GRAFANA_USER', 'admin')
GRAFANA_PASS = os.environ.get('GRAFANA_PASS', 'admin')


def generate_report_data(count: int = 500) -> List[Dict[str, Any]]:
    """Generate realistic report data for OpenSearch."""
    
    reports = []
    base_time = datetime.utcnow() - timedelta(days=7)
    
    # Report types and statuses
    report_types = [
        'network_latency', 'bandwidth_utilization', 'packet_loss',
        'throughput', 'error_rate', 'connection_count',
        'dns_resolution', 'ssl_certificate', 'config_change'
    ]
    
    statuses = ['completed', 'failed', 'in_progress', 'timeout']
    sources = ['ion-manager', 'amp-manager', 'external-monitor', 'internal']
    
    for i in range(count):
        report_time = base_time + timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        report = {
            'report_id': f'rpt-{i+1:06d}',
            'report_type': random.choice(report_types),
            'status': random.choice(statuses),
            'source': random.choice(sources),
            'timestamp': report_time.isoformat(),
            'reference_time': report_time.isoformat(),
            'agent_id': random.randint(1, 150),
            'metrics': {
                'latency_ms': round(random.uniform(1, 500), 2),
                'throughput_mbps': round(random.uniform(10, 1000), 2),
                'error_count': random.randint(0, 100),
                'packet_loss_pct': round(random.uniform(0, 10), 2),
            },
            'summary': f"Report {i+1}: {random.choice(report_types)} from {random.choice(sources)}",
        }
        
        reports.append(report)
    
    return reports


async def seed_opensearch(count: int = 500, reset: bool = False):
    """Seed OpenSearch with report data."""
    import httpx
    
    print(f"Connecting to OpenSearch: {OPENSEARCH_URL}")
    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        # Authenticate
        auth = (OPENSEARCH_USER, OPENSEARCH_PASS)
        
        # Create index if it doesn't exist
        index_name = 'anms-reports-test'
        print(f"Creating/updating index: {index_name}")
        
        if reset:
            # Delete existing index
            try:
                resp = await client.delete(f'{OPENSEARCH_URL}/{index_name}', auth=auth)
                if resp.status_code == 200:
                    print(f"  Deleted existing index")
            except:
                pass
        
        # Create index with mapping
        mapping = {
            "mappings": {
                "properties": {
                    'report_id': {'type': 'keyword'},
                    'report_type': {'type': 'keyword'},
                    'status': {'type': 'keyword'},
                    'source': {'type': 'keyword'},
                    'timestamp': {'type': 'date'},
                    'reference_time': {'type': 'date'},
                    'agent_id': {'type': 'integer'},
                    'metrics': {
                        'properties': {
                            'latency_ms': {'type': 'float'},
                            'throughput_mbps': {'type': 'float'},
                            'error_count': {'type': 'integer'},
                            'packet_loss_pct': {'type': 'float'},
                        }
                    },
                    'summary': {'type': 'text'}
                }
            }
        }
        
        resp = await client.put(f'{OPENSEARCH_URL}/{index_name}', json=mapping, auth=auth)
        if resp.status_code in [200, 201]:
            print(f"  Index created/updated")
        else:
            print(f"  Warning: Could not create index: {resp.status_code}")
            return
        
        # Generate and index reports
        print(f"Generating {count} reports...")
        reports = generate_report_data(count)
        
        # Bulk index
        bulk_data = []
        for report in reports:
            bulk_data.append(json.dumps({
                'index': {
                    '_index': index_name,
                    '_id': report['report_id']
                }
            }))
            bulk_data.append(json.dumps(report))
        
        print(f"Indexing reports...")
        resp = await client.post(
            f'{OPENSEARCH_URL}/_bulk',
            headers={'Content-Type': 'application/x-ndjson'},
            content='\n'.join(bulk_data) + '\n',
            auth=auth
        )
        
        if resp.status_code == 200:
            result = resp.json()
            errors = result.get('errors', False)
            if errors:
                print(f"  Warning: {len(result.get('items', []))} documents had errors")
            else:
                print(f"  Indexed {len(reports)} reports successfully")
        else:
            print(f"  Error: {resp.status_code} - {resp.text[:200]}")
        
        # Refresh index
        await client.post(f'{OPENSEARCH_URL}/{index_name}/_refresh', auth=auth)
        
        # Verify
        resp = await client.get(f'{OPENSEARCH_URL}/{index_name}/_count', auth=auth)
        if resp.status_code == 200:
            count_result = resp.json()
            print(f"\nSeed complete: {count_result.get('count', 0)} reports in {index_name}")
            
            # Show sample
            resp = await client.get(
                f'{OPENSEARCH_URL}/{index_name}/_search',
                headers={'Content-Type': 'application/json'},
                content=json.dumps({'query': {'match_all': {}}, 'size': 3}),
                auth=auth
            )
            if resp.status_code == 200:
                hits = resp.json()['hits']['hits']
                print("\nSample reports:")
                for hit in hits:
                    r = hit['_source']
                    print(f"  - {r['report_id']}: {r['report_type']} ({r['status']})")
                    print(f"    Source: {r['source']}, Time: {r['timestamp'][:19]}")
                    print(f"    Metrics: latency={r['metrics']['latency_ms']}ms, "
                          f"throughput={r['metrics']['throughput_mbps']}Mbps")


def get_grafana_auth():
    """Get Grafana authentication headers."""
    # Try different credential combinations
    credentials = [
        (GRAFANA_USER, 'admin'),  # Default Grafana
        (GRAFANA_USER, GRAFANA_PASS),  # Configured password
        ('admin', 'admin'),  # Common default
    ]
    
    import httpx
    for user, password in credentials:
        try:
            with httpx.Client(base_url=GRAFANA_URL, timeout=10) as client:
                resp = client.get('/api/health', auth=(user, password))
                if resp.status_code == 200:
                    print(f"  Authenticated as {user}")
                    return user, password
        except:
            continue
    
    print("  Could not authenticate with Grafana")
    return None, None


async def seed_grafana():
    """Seed Grafana with datasource and dashboard (if accessible)."""
    import httpx
    
    print(f"\n=== Grafana Seeding ===")
    print(f"URL: {GRAFANA_URL}")
    
    user, password = get_grafana_auth()
    if not user:
        print("  Skipping Grafana seeding (authentication failed)")
        return
    
    async with httpx.AsyncClient(
        base_url=GRAFANA_URL, 
        timeout=30,
        verify=False
    ) as client:
        # Create OpenSearch datasource if it doesn't exist
        datasource_name = 'OpenSearch'
        print(f"Checking for datasource: {datasource_name}")
        
        resp = await client.get('/api/datasources', auth=(user, password))
        if resp.status_code == 200:
            datasources = resp.json()
            existing = [ds for ds in datasources if ds['name'] == datasource_name]
            
            if not existing:
                print(f"  Creating OpenSearch datasource...")
                datasource = {
                    "name": datasource_name,
                    "type": "grafana-opensearch-datasource",
                    "url": OPENSEARCH_URL.replace('https://', 'http://'),  # Grafana uses HTTP internally
                    "access": "proxy",
                    "jsonData": {
                        "database": "",
                        "timeField": "timestamp",
                        "esVersion": "7.0.0",
                        "logLevelField": "",
                        "logMessageField": "",
                        "maxConcurrentShardRequests": 5,
                        "timeField": "@timestamp",
                    },
                    "secureJsonFields": {},
                }
                
                resp = await client.post('/api/datasources', json=datasource, auth=(user, password))
                if resp.status_code in [200, 201]:
                    print(f"  Created OpenSearch datasource")
                else:
                    print(f"  Warning: Could not create datasource: {resp.status_code}")
            else:
                print(f"  Datasource {datasource_name} already exists")
        else:
            print(f"  Could not list datasources: {resp.status_code}")


async def main():
    import argparse


    
    parser = argparse.ArgumentParser(description="Seed ANMS OpenSearch and Grafana with test data")
    parser.add_argument("--count", type=int, default=500, help="Number of documents to create")
    parser.add_argument("--reset", action="store_true", help="Clear test indices before seeding")
    parser.add_argument("--skip-grafana", action="store_true", help="Skip Grafana seeding")
    
    args = parser.parse_args()
    
    print(f"=== ANMS Dashboard Seeder ===")
    print(f"OpenSearch: {OPENSEARCH_URL}")
    print(f"Grafana: {GRAFANA_URL}")
    print(f"Count: {args.count}")
    print(f"Reset: {args.reset}")
    print()
    
    # Seed OpenSearch
    await seed_opensearch(args.count, args.reset)
    
    # Seed Grafana (optional)
    if not args.skip_grafana:
        await seed_grafana()


if __name__ == "__main__":
    asyncio.run(main())
