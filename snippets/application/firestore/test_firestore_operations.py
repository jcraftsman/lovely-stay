import unittest
from testcontainers.firestore import FirestoreEmulatorContainer
from firestore_operations import get_data_from_firestore

class TestFirestoreOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.firestore_emulator = FirestoreEmulatorContainer()
        cls.firestore_emulator.start()
        # Set the Firestore emulator environment variables
        # Replace 'test-project-id' with the same project ID used to start the emulator
        cls.firestore_emulator_url = f"http://{cls.firestore_emulator.get_container_host_ip()}:{cls.firestore_emulator.get_exposed_port(8080)}"
        cls.firestore_emulator_url = f"{cls.firestore_emulator_url}/v1/projects/test-project-id/databases/(default)/documents"

        # Set the Firestore emulator environment variables
        import os
        os.environ["FIRESTORE_EMULATOR_HOST"] = cls.firestore_emulator.get_container_host_ip()
        os.environ["FIRESTORE_EMULATOR_PORT"] = str(cls.firestore_emulator.get_exposed_port(8080))

    @classmethod
    def tearDownClass(cls):
        cls.firestore_emulator.stop()

    def test_get_data_from_firestore(self):
        # Test your Firestore interactions here
        # Use self.firestore_emulator_url as the Firestore database URL
        data = get_data_from_firestore()
        self.assertIsNotNone(data)

if __name__ == '__main__':
    unittest.main()
