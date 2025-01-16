import unittest
from scripts.esxi import run_esxi_test

class TestESXiAutomation(unittest.TestCase):
    def test_esxi_automation(self):
        # Stelle sicher, dass keine Ausnahmen auftreten
        try:
            run_esxi_test()
        except Exception as e:
            self.fail(f"run_esxi_test() hat eine Ausnahme ausgelöst: {e}")

if __name__ == "__main__":
    unittest.main()
