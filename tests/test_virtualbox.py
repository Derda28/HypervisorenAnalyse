import unittest
from scripts.virtualbox import run_virtualbox_test

class TestVirtualBoxAutomation(unittest.TestCase):
    def test_virtualbox_automation(self):
        try:
            run_virtualbox_test()
        except Exception as e:
            self.fail(f"run_virtualbox_test() hat eine Ausnahme ausgelöst: {e}")

if __name__ == "__main__":
    unittest.main()
