from django.test import TestCase

from .models import Device, InspectionTask


class InspectionApiTests(TestCase):
    def setUp(self):
        self.device = Device.objects.create(
            code="UAV-001",
            name="巡检一号",
            status="online",
            battery_level=88,
        )
        InspectionTask.objects.create(
            name="线路巡检",
            device=self.device,
            area="A 区",
            status="running",
            progress=45,
        )

    def test_overview(self):
        response = self.client.get("/api/overview/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["totalTasks"], 1)

    def test_device_list(self):
        response = self.client.get("/api/device/list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"][0]["code"], "UAV-001")

    def test_inspection_list(self):
        response = self.client.get("/api/inspection/list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"][0]["name"], "线路巡检")
