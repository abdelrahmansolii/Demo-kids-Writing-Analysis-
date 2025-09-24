import pygame


class FeedbackGenerator:
    def __init__(self):
        pygame.font.init()
        self.fonts = {
            'small': pygame.font.SysFont('Arial', 20),
            'medium': pygame.font.SysFont('Arial', 30),
            'large': pygame.font.SysFont('Arial', 40)
        }
        self.colors = {
            'excellent': (0, 180, 0),
            'good': (0, 120, 200),
            'okay': (200, 200, 0),
            'poor': (200, 0, 0),
            'text': (40, 40, 40),
            'highlight': (255, 255, 0)
        }

    def render(self, screen, result, current_letter_idx):
        # Background panel
        pygame.draw.rect(screen, (240, 240, 240), (0, 0, 800, 150))

        # Overall score
        score_color = self._get_score_color(result['overall_score'])
        score_text = self.fonts['large'].render(
            f"Overall: {result['overall_score']:.0f}%",
            True,
            score_color
        )
        screen.blit(score_text, (20, 20))

        # Word feedback
        feedback_text = self.fonts['medium'].render(
            result['word_feedback'],
            True,
            self.colors['text']
        )
        screen.blit(feedback_text, (20, 70))

        # Letter grid
        for i, letter in enumerate(result['letter_results']):
            x_pos = 20 + (i * 70)

            # Highlight current letter
            if i == current_letter_idx:
                pygame.draw.rect(screen, self.colors['highlight'], (x_pos - 5, 115, 60, 60), 3)

            # Letter box
            pygame.draw.rect(screen, (255, 255, 255), (x_pos, 120, 50, 50))
            letter_surface = self.fonts['large'].render(letter['target'], True, (80, 80, 80))
            screen.blit(letter_surface, (x_pos + 15, 125))

            # Score indicator
            score_color = self._get_score_color(letter['score'])
            pygame.draw.circle(screen, score_color, (x_pos + 25, 200), 15)
            score_text = self.fonts['small'].render(f"{letter['score']}%", True, (255, 255, 255))
            screen.blit(score_text, (x_pos + 15, 190))

            # Direction arrows (visual hint)
            if letter['directions']:
                dir_text = self.fonts['small'].render(letter['directions'][:3], True, (150, 150, 150))
                screen.blit(dir_text, (x_pos + 10, 220))

    def _get_score_color(self, score):
        if score >= 85: return self.colors['excellent']
        if score >= 70: return self.colors['good']
        if score >= 50: return self.colors['okay']
        return self.colors['poor']