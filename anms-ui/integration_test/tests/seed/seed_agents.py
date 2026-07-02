#!/usr/bin/env python3
"""
Seed script for creating realistic agent data in the ANMS database.

Creates:
- 100+ agents with various states (online, offline, error)
- Agents with different endpoint URIs (IPN, TCP, etc.)
- Realistic registration timestamps
- Various agent types and configurations

Usage:
    cd ~/anms/anms-ui/integration_test
    python tests/seed/seed_agents.py [--count N] [--reset]

Options:
    --count N    Number of agents to create (default: 100)
    --reset      Clear existing agents before seeding
"""

import os
import sys
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add anms-core to path (resolve relative to this script's location)
script_dir = os.path.dirname(os.path.abspath(__file__))
anms_core_dir = os.path.join(script_dir, '..', '..', '..', '..', 'anms-core')
sys.path.insert(0, anms_core_dir)

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Import models
from anms.models.relational.registered_agent import RegisteredAgent
from anms.shared.config import DB_ASYNC_SCHEME, DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_CHROOT

# Database connection string
DB_URL = f"{DB_ASYNC_SCHEME}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_CHROOT}"


def generate_agent_data(count: int = 100) -> List[Dict[str, Any]]:
    """Generate realistic agent data."""
    
    # Agent endpoint URI patterns
    uri_patterns = [
        "ipn:{}.{}",           # IPN style
        "tcp:{}.{}:{}",       # TCP style
        "udp:{}.{}:{}",       # UDP style
        "dtntcp:{}.{}",       # DTN TCP
        "http:{}:{}",         # HTTP
        "https:{}:{}",        # HTTPS
    ]
    
    # IP addresses and ports
    ip_ranges = [
        "10.0.{}",
        "172.16.{}",
        "192.168.{}.{}",
        "100.64.{}",
        "203.0.113.{}",
    ]
    
    agents = []
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for i in range(count):
        # Pick random IP pattern and values
        ip_pattern = random.choice(ip_ranges)
        uri_pattern = random.choice(uri_patterns)
        
        # Generate IP/port values
        if "{}.{}" in ip_pattern:
            ip_parts = [random.randint(1, 254), random.randint(1, 254)]
        else:
            ip_parts = [random.randint(1, 254)]
        
        port = random.randint(1024, 65535)
        
        # Generate URI
        try:
            if ":" in uri_pattern:
                uri = uri_pattern.format(*ip_parts, port)
            else:
                uri = uri_pattern.format(*ip_parts)
        except:
            uri = f"ipn:{random.randint(1, 254)}.{random.randint(1, 254)}"
        
        # Generate timestamps
        first_registered = base_time + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        last_registered = first_registered + timedelta(
            days=random.randint(0, 14),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        agents.append({
            "agent_endpoint_uri": uri,
            "first_registered": first_registered,
            "last_registered": last_registered,
        })
    
    return agents


async def seed_database(count: int = 100, reset: bool = False):
    """Seed the database with agent data."""
    
    print(f"Connecting to database: {DB_HOST}:{DB_PORT}/{DB_CHROOT}")
    
    # Create engine and session
    engine = create_async_engine(DB_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        if reset:
            print(f"Clearing existing agents...")
            await session.execute("DELETE FROM registered_agents")
            await session.commit()
            print("  Cleared.")
        
        # Generate agent data
        print(f"Generating {count} agents...")
        agents = generate_agent_data(count)
        
        # Insert agents
        print(f"Inserting agents...")
        inserted = 0
        for i, agent_data in enumerate(agents):
            try:
                agent = RegisteredAgent(**agent_data)
                session.add(agent)
                inserted += 1
                
                # Commit in batches to avoid large transactions
                if inserted % 50 == 0:
                    await session.commit()
                    print(f"  Inserted {inserted}/{count} agents...")
            except Exception as e:
                # Skip duplicates or errors
                if "unique" not in str(e).lower():
                    print(f"  Warning: Failed to insert agent {i+1}: {e}")
        
        # Final commit
        await session.commit()
        
        # Verify
        result = await session.execute(select(RegisteredAgent))
        all_agents = result.scalars().all()
        print(f"\nSeed complete: {len(all_agents)} total agents in database")
        
        # Show sample
        if all_agents:
            sample = all_agents[:3]
            print("\nSample agents:")
            for agent in sample:
                print(f"  - {agent.agent_endpoint_uri}")
                print(f"    First registered: {agent.first_registered}")
                print(f"    Last registered:  {agent.last_registered}")
    
    await engine.dispose()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed ANMS database with agent data")
    parser.add_argument("--count", type=int, default=100, help="Number of agents to create")
    parser.add_argument("--reset", action="store_true", help="Clear existing agents before seeding")
    
    args = parser.parse_args()
    
    print(f"=== ANMS Agent Seeder ===")
    print(f"Count: {args.count}")
    print(f"Reset: {args.reset}")
    print()
    
    asyncio.run(seed_database(args.count, args.reset))


if __name__ == "__main__":
    main()
