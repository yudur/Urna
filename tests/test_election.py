import tempfile
import threading
import unittest
from pathlib import Path

from server.election import Election
from server.protocol import decode_message, encode_message, validate_vote_request


class ElectionTests(unittest.TestCase):
    def test_duplicate_is_rejected_atomically(self):
        election = Election()
        barrier = threading.Barrier(20)
        results = []

        def vote(index):
            barrier.wait()
            results.append(election.register_vote("2026001", 1 if index % 2 == 0 else 2))

        threads = [threading.Thread(target=vote, args=(i,)) for i in range(20)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        confirmed = [result for result in results if result[0]]
        duplicate = [result for result in results if result[2] == "duplicate"]
        self.assertEqual(len(confirmed), 1)
        self.assertEqual(len(duplicate), 19)
        self.assertEqual(election.tally()["candidates"][1] + election.tally()["candidates"][2], 1)

    def test_blank_and_candidates_are_counted(self):
        election = Election()
        election.register_vote("A", 1)
        election.register_vote("B", 2)
        election.register_vote("C", 0)
        tally = election.tally()
        self.assertEqual(tally["valid"], 2)
        self.assertEqual(tally["blank"], 1)
        self.assertEqual(tally["total"], 3)

    def test_invalid_candidate_is_rejected(self):
        election = Election()
        success, message, code = election.register_vote("A", 99)
        self.assertFalse(success)
        self.assertEqual(message, "Candidato inválido")
        self.assertEqual(code, "invalid_candidate")

    def test_save_result_creates_complete_file(self):
        election = Election()
        election.register_vote("A", 3)
        election.register_vote("B", 0)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resultado.txt"
            election.save_result(path)
            text = path.read_text(encoding="utf-8")
        self.assertIn("Chapa C: 1 voto(s)", text)
        self.assertIn("Voto em branco: 1 voto(s)", text)
        self.assertIn("Total geral: 2", text)

    def test_protocol_encodes_and_validates_json(self):
        message = {"action": "vote", "student_id": "2026001", "candidate_id": 2}
        decoded = decode_message(encode_message(message).rstrip(b"\n"))
        self.assertEqual(validate_vote_request(decoded)[0], ("2026001", 2))
        self.assertIsNotNone(validate_vote_request({"action": "vote"})[1])


if __name__ == "__main__":
    unittest.main()
