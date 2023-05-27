import unittest
from  app import geomath

class GeomathTests(unittest.TestCase):
    def assertTupleAlmostEqual(self, tuple1, tuple2, places=7):
        self.assertEqual(len(tuple1), len(tuple2), msg="Tuple lengths are different")

        for i in range(len(tuple1)):
            self.assertAlmostEqual(tuple1[i], tuple2[i], places=places)

    def assertCoordinatesAlmostEqual(self, coord1, coord2, places=7):
        self.assertAlmostEqual(coord1[0], coord2[0], places=places)
        self.assertAlmostEqual(coord1[1], coord2[1], places=places)

    def test_convert_to_cartesian(self):
        # Test case 1
        lat, lon = 89.8108633570, 45.0000000000
        expected_cartesian = (100, 100, 0)
        calculated_cartesian = geomath.convert_to_cartesian((lat, lon))
        self.assertTupleAlmostEqual(calculated_cartesian, expected_cartesian)

    def test_convert_to_latlon(self):
        cartesian = (123, 42, 0)
        expected_latlon = (89.8261743170, 18.8531587640)
        calculated_latlon = geomath.convert_to_latlon(cartesian)
        self.assertCoordinatesAlmostEqual(calculated_latlon, expected_latlon)

    def test_conversion_to_and_back(self):
        coord1 = (47.408732, 8.723168)
        cart = geomath.convert_to_cartesian(coord1)
        coord2 = geomath.convert_to_latlon(cart)
        self.assertCoordinatesAlmostEqual(coord1, coord2)
   