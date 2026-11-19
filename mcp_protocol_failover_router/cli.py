"""CLI for Failover Router."""
import argparse
from .core import ProtocolFailoverRouter, UpstreamEndpoint

def main():
    parser = argparse.ArgumentParser(description="MCP Protocol Failover Router CLI")
    parser.add_argument("--demo", action="store_true", help="Run failover demo")
    args = parser.parse_args()

    router = ProtocolFailoverRouter()
    # Primary fails
    def fail(a): raise ConnectionError("Primary down")
    # Secondary succeeds
    def ok(a): return {"status": "ok_from_standby"}

    router.add_endpoint(UpstreamEndpoint("primary", fail))
    router.add_endpoint(UpstreamEndpoint("standby", ok))

    res = router.route({"ping": True})
    print(f"Failover successful! Result: {res}")

if __name__ == "__main__":
    main()
