"""
Hermes API Server entry point — `hermes serve`

Starts GatewayRunner in api_only mode with only the APIServerAdapter.
"""
import argparse
import logging
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(prog="hermes serve", description="Start Hermes API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8642, help="Port to bind (default: 8642)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    from gateway.run import GatewayRunner
    from gateway.config import load_gateway_config

    config = load_gateway_config()
    runner = GatewayRunner(config, api_only=True)
    runner.run()

if __name__ == "__main__":
    main()