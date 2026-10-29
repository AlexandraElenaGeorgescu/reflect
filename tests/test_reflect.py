import unittest

from reflect import guard, safety
from reflect.dialogue import SAFE_FALLBACK, Session


class BadClient:
    def __init__(self, reply):
        self.reply = reply

    def complete(self, stage, entry, answers):
        return self.reply


class SafetyTests(unittest.TestCase):
    def test_english_crisis(self):
        self.assertTrue(safety.screen("Sometimes I want to die").crisis)

    def test_romanian_crisis_with_diacritics(self):
        self.assertTrue(safety.screen("Nu mai vreau să trăiesc așa").crisis)
        self.assertTrue(safety.screen("vreau sa mor").crisis)

    def test_ordinary_stress_is_not_crisis(self):
        self.assertFalse(safety.screen("Work is killing my motivation lately").crisis)
        self.assertFalse(safety.screen("Am avut o zi grea la serviciu").crisis)

    def test_crisis_message_has_emergency_number(self):
        self.assertIn("112", safety.screen("I want to end my life").message)


class GuardTests(unittest.TestCase):
    def test_blocks_diagnosis(self):
        self.assertFalse(guard.check("You have depression, it seems?").ok)
        self.assertFalse(guard.check("Ai depresie, nu crezi?").ok)

    def test_blocks_directive_advice(self):
        self.assertFalse(guard.check("You should leave your job. Agree?").ok)

    def test_requires_closing_question(self):
        self.assertFalse(guard.check("That sounds hard.").ok)

    def test_accepts_tentative_question(self):
        self.assertTrue(guard.check("One way to read this might be X. Does that fit?").ok)


class DialogueTests(unittest.TestCase):
    def test_asks_before_interpreting(self):
        s = Session()
        first = s.say("I keep putting off a hard email to my manager.")
        self.assertTrue(first.endswith("?"))
        self.assertNotIn("One way to read", first)

    def test_full_flow_ends_with_tentative_reflection(self):
        s = Session()
        s.say("I keep putting off a hard email.")
        s.say("The part about saying no.")
        final = s.say("Tight chest, a bit dread.")
        self.assertIn("One way to read this might be", final)
        self.assertTrue(final.endswith("?"))
        self.assertTrue(s.stopped)

    def test_crisis_stops_and_skips_model(self):
        s = Session(client=BadClient("should never be used?"))
        out = s.say("I want to kill myself")
        self.assertIn("112", out)
        self.assertTrue(s.stopped)
        self.assertTrue(any("model not called" in l for l in s.log))

    def test_crisis_mid_conversation(self):
        s = Session()
        s.say("Rough week.")
        out = s.say("honestly vreau sa mor")
        self.assertIn("112", out)

    def test_diagnostic_reply_is_replaced_by_safe_fallback(self):
        s = Session(client=BadClient("You have anxiety disorder, right?"))
        self.assertEqual(s.say("I can't sleep before meetings."), SAFE_FALLBACK)
        self.assertTrue(any("blocked" in l for l in s.log))


if __name__ == "__main__":
    unittest.main()
