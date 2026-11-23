import os
import threading
from pathlib import Path


class Election:
    CANDIDATES = {
        1: "Chapa A",
        2: "Chapa B",
        3: "Chapa C",
    }
    BLANK_CANDIDATE = 0

    def __init__(self):
        self._lock = threading.Lock()
        self._voted_student_ids = set()
        self._candidate_votes = {candidate_id: 0 for candidate_id in self.CANDIDATES}
        self._blank_votes = 0

    def register_vote(self, student_id, candidate_id):
        with self._lock:
            if candidate_id not in self.CANDIDATES and candidate_id != self.BLANK_CANDIDATE:
                return False, "Candidato inválido", "invalid_candidate"
            if student_id in self._voted_student_ids:
                return False, "Matrícula já utilizada", "duplicate"

            self._voted_student_ids.add(student_id)
            if candidate_id == self.BLANK_CANDIDATE:
                self._blank_votes += 1
            else:
                self._candidate_votes[candidate_id] += 1
            return True, "[VOTO CONFIRMADO]", "success"

    def tally(self):
        with self._lock:
            candidate_votes = dict(self._candidate_votes)
            blank_votes = self._blank_votes
            valid_votes = sum(candidate_votes.values())
            total_votes = valid_votes + blank_votes
            return {
                "candidates": candidate_votes,
                "blank": blank_votes,
                "valid": valid_votes,
                "total": total_votes,
            }

    def format_tally(self):
        tally = self.tally()
        lines = ["=== APURAÇÃO ==="]
        for candidate_id, name in self.CANDIDATES.items():
            lines.append(f"{candidate_id} - {name}: {tally['candidates'][candidate_id]} voto(s)")
        lines.append(f"0 - Voto em branco: {tally['blank']} voto(s)")
        lines.append(f"Total de votos válidos: {tally['valid']}")
        lines.append(f"Total geral: {tally['total']}")
        return "\n".join(lines)

    def save_result(self, path="resultado.txt"):
        tally = self.tally()
        lines = ["Resultado da votação", ""]
        for candidate_id, name in self.CANDIDATES.items():
            lines.append(f"{candidate_id} - {name}: {tally['candidates'][candidate_id]} voto(s)")
        lines.append(f"0 - Voto em branco: {tally['blank']} voto(s)")
        lines.append(f"Total de votos válidos: {tally['valid']}")
        lines.append(f"Total geral: {tally['total']}")

        target = Path(path)
        temporary = target.with_name(target.name + ".tmp")
        temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.replace(temporary, target)
