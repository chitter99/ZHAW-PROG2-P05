import unittest
from unittest import mock

from app.models import Route
from app.services import TransportService, RoutingService

class RoutingTest(unittest.TestCase):
    def setUp(self):
        # Create a mock instance of the TransportService
        self.transport_service_mock = mock.Mock(spec=TransportService)
        self.steps = 5
        self.nearness = 10
        self.routing_service = RoutingService(self.transport_service_mock, self.steps, self.nearness)

    def test_route_direct_route_available(self):
        # Prepare the mock return value for direct route
        direct_connections = {
            "connections": [
                {"start": "A", "dest": "B"},
                {"start": "B", "dest": "C"},
            ],
            "from": {"coordinate": {"x": "0", "y": "0"}},
            "to": {"coordinate": {"x": "10", "y": "10"}},
        }
        self.transport_service_mock.get_connections.return_value = direct_connections

        # Call the route method
        start = "A"
        dest = "C"
        result = self.routing_service.route(start, dest)

        # Check the result
        self.assertTrue(isinstance(result, Route))
        self.assertTrue(result.direct_route)
        self.assertTrue(result.found_connection)
        self.assertEqual(result.start, start)
        self.assertEqual(result.dest, dest)
        self.assertEqual(result.coverage, 1)
        self.assertEqual(result.connections, direct_connections["connections"])

        # Ensure that get_connections was called with the correct arguments
        self.transport_service_mock.get_connections.assert_called_once_with(start, dest)

    def test_route_no_direct_route(self):
        # Prepare the mock return values for no direct route
        self.transport_service_mock.get_connections.return_value = {
            "connections": None,
            "from": {"coordinate": {"x": "0", "y": "0"}},
            "to": {"coordinate": {"x": "10", "y": "10"}},
        }
        self.transport_service_mock.search_locations.return_value = {"stations": [{"name": "B", "distance": 15}]}

        intermediate_cords = [(2, 2), (4, 4), (6, 6), (8, 8)]
        geomath_mock = mock.Mock()
        geomath_mock.calculate_intermediate_coordinates.return_value = intermediate_cords

        with mock.patch("app.geomath", geomath_mock):
            # Call the route method
            start = "A"
            dest = "C"
            result = self.routing_service.route(start, dest)

        # Check the result
        self.assertTrue(isinstance(result, Route))
        self.assertFalse(result.direct_route)
        self.assertTrue(result.found_connection)
        self.assertEqual(result.start, start)
        self.assertEqual(result.dest, dest)
        self.assertEqual(result.coverage, 0.5)
        self.assertEqual(result.nearest_startion, "B")
        self.assertEqual(result.connections, [])

        # Ensure that the mock methods were called with the correct arguments
        self.transport_service_mock.get_connections.assert_called_once_with(start, "B")
        self.transport_service_mock.search_locations.assert_called_once_with(x=6, y=6, location_type="station")
        geomath_mock.calculate_intermediate_coordinates.assert_called_once_with((10, 10), (0, 0), self.steps)

    def test_route_no_connection_found(self):
        # Prepare the mock return values for no connection found
        self.transport_service_mock.get_connections.return_value = {"connections": None}
        self.transport_service_mock.search_locations.return_value = {"stations": []}

        # Call the route method
        start = "A"
        dest = "C"
        result = self.routing_service.route(start, dest)

        # Check the result
        self.assertTrue(isinstance(result, Route))
        self.assertFalse(result.direct_route)
        self.assertFalse(result.found_connection)
        self.assertEqual(result.start, start)
        self.assertEqual(result.dest, dest)

        # Ensure that the mock methods were called with the correct arguments
        self.transport_service_mock.get_connections.assert_called_once_with(start, dest)
        self.transport_service_mock.search_locations.assert_not_called()