"""Tests for Failover Router."""
import unittest
from mcp_protocol_failover_router.core import ProtocolFailoverRouter, UpstreamEndpoint, CircuitState

class TestProtocolFailoverRouter(unittest.TestCase):
    def test_failover_to_standby(self):
        r = ProtocolFailoverRouter()
        r.add_endpoint(UpstreamEndpoint("ep1", lambda a: (_ for _ in ()).throw(ValueError("ep1 fail"))))
        r.add_endpoint(UpstreamEndpoint("ep2", lambda a: 42))

        res = r.route({})
        self.assertEqual(res, 42)
        self.assertEqual(r.endpoints[0].consecutive_failures, 1)
        self.assertEqual(r.endpoints[1].state, CircuitState.CLOSED)
