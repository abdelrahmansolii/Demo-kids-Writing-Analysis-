import numpy as np
import cv2
from difflib import SequenceMatcher


class StrokeAnalyzer:
    def __init__(self):
        # Character stroke directions (simplified)
        self.letter_profiles = {
            'A': {'directions': 'DRURD', 'critical_points': [(0.5, 0)]},
            'B': {'directions': 'DRURDR', 'critical_points': [(0.3, 0.2)]},
            'C': {'directions': 'DRD', 'critical_points': []},
            'D': {'directions': 'DRUR', 'critical_points': []},
            'E': {'directions': 'DRURD', 'critical_points': [(0.3, 0.5)]},
            # Add other letters as needed...
        }

    def analyze(self, strokes, target_word, mode):
        if len(strokes) < 2:
            return self._empty_result(target_word)

        letter_segments = self._segment_letters(strokes, target_word)
        results = []

        for i, (segment, target_char) in enumerate(zip(letter_segments, target_word)):
            if len(segment) < 2:
                results.append(self._empty_letter(target_char))
                continue

            score, feedback = self._analyze_letter(segment, target_char, mode)
            results.append({
                'target': target_char,
                'score': score,
                'feedback': feedback,
                'directions': self._get_stroke_directions(segment)
            })

        return {
            'letter_results': results,
            'overall_score': np.mean([r['score'] for r in results]),
            'word_feedback': self._generate_word_feedback(results)
        }

    def _analyze_letter(self, strokes, target_char, mode):
        base_score = 80 if mode == 'trace' else 60
        shape_score = min(100, base_score + np.random.randint(-15, 15))
        dir_score = self._score_directions(strokes, target_char)
        return (
            int(shape_score * 0.6 + dir_score * 0.4),
            self._get_letter_feedback(shape_score, target_char)
        )

    def _get_stroke_directions(self, strokes):
        dirs = []
        for i in range(1, len(strokes)):
            dx = strokes[i][0] - strokes[i - 1][0]
            dy = strokes[i][1] - strokes[i - 1][1]
            if abs(dx) > abs(dy):
                dirs.append('R' if dx > 0 else 'L')
            else:
                dirs.append('D' if dy > 0 else 'U')
        return ''.join(dirs)

    def _score_directions(self, strokes, target_char):
        if target_char not in self.letter_profiles:
            return 70  # Default score if we don't have profile

        actual = self._get_stroke_directions(strokes)
        expected = self.letter_profiles[target_char]['directions']

        # Simple similarity scoring
        return min(100, 70 + (SequenceMatcher(None, actual, expected).ratio() * 30))

    def _segment_letters(self, strokes, target_word):
        segments = [[] for _ in target_word]
        if not strokes:
            return segments

        min_x = min(s[0] for s in strokes)
        max_x = max(s[0] for s in strokes)
        letter_width = (max_x - min_x) / len(target_word)

        for stroke in strokes:
            idx = min(int((stroke[0] - min_x) / letter_width), len(target_word) - 1)
            segments[idx].append(stroke)

        return segments

    def _get_letter_feedback(self, score, target_char):
        if score > 85:
            return f"Perfect {target_char}!"
        elif score > 70:
            return f"Good {target_char} - minor issues"
        elif score > 50:
            return f"{target_char} needs practice"
        elif score > 30:
            return f"Poor {target_char} - trace slowly"
        else:
            return f"Retry {target_char}"

    def _generate_word_feedback(self, results):
        avg_score = np.mean([r['score'] for r in results])
        if avg_score > 80:
            return "Excellent! Keep practicing!"
        elif avg_score > 65:
            return "Good job! Focus on problem letters"
        else:
            return "Try again - use tracing mode"

    def _empty_result(self, word):
        return {
            'letter_results': [self._empty_letter(c) for c in word],
            'overall_score': 0,
            'word_feedback': "Draw something!"
        }

    def _empty_letter(self, char):
        return {
            'target': char,
            'score': 0,
            'feedback': "No strokes",
            'directions': ""
        }