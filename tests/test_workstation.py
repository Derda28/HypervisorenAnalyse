import unittest
from scripts.workstation import run_workstation_test

class TestWorkstationAutomation(unittest.TestCase):
    def test_workstation_automation(self):
        try:
            run_workstation_test()
        except Exception as e:
            self.fail(f"run_workstation_test() hat eine Ausnahme ausgelöst: {e}")

if __name__ == "__main__":
    unittest.main()
