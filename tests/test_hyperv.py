import unittest
from scripts.hyperv import run_hyperv_test

class TestHyperVAutomation(unittest.TestCase):
    def test_hyperv_automation(self):
        try:
            run_hyperv_test()
        except Exception as e:
            self.fail(f"run_hyperv_test() hat eine Ausnahme ausgelöst: {e}")

if __name__ == "__main__":
    unittest.main()
