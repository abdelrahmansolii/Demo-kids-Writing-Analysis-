import pygame
import sys
from analyzer.stroke_analyzer import StrokeAnalyzer
from analyzer.feedback import FeedbackGenerator


class WritingApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.analyzer = StrokeAnalyzer()
        self.feedback = FeedbackGenerator()

        # App states
        self.mode = 'input'  # input/select/trace/write
        self.target_word = ""
        self.user_strokes = []
        self.current_stroke = []
        self.current_letter_idx = 0
        self.result = None

        # Fonts
        self.font_large = pygame.font.SysFont('Arial', 120)
        self.font_medium = pygame.font.SysFont('Arial', 60)

        # UI elements
        self.buttons = {
            'trace': pygame.Rect(200, 250, 400, 80),
            'write': pygame.Rect(200, 350, 400, 80)
        }

    def run(self):
        while True:
            self.handle_events()
            self.render()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.mode == 'input':
                self.handle_input_mode(event)
            elif self.mode == 'select':
                self.handle_select_mode(event)
            else:  # trace/write mode
                self.handle_drawing_mode(event)

    def handle_input_mode(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.target_word:
                self.mode = 'select'
            elif event.key == pygame.K_BACKSPACE:
                self.target_word = self.target_word[:-1]
            elif event.unicode.isalpha():
                self.target_word += event.unicode.upper()

    def handle_select_mode(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for mode, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    self.mode = mode
                    self.reset_drawing_state()

    def handle_drawing_mode(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.current_stroke = [[event.pos[0], event.pos[1], pygame.time.get_ticks()]]
        elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            self.current_stroke.append([event.pos[0], event.pos[1], pygame.time.get_ticks()])
        elif event.type == pygame.MOUSEBUTTONUP:
            if len(self.current_stroke) > 1:
                self.process_stroke()

    def process_stroke(self):
        self.user_strokes.append(self.current_stroke)
        self.result = self.analyzer.analyze(
            self.current_stroke,
            self.target_word,
            self.mode
        )
        self.current_stroke = []

        # Progress to next letter if good score
        if self.result['letter_results'][self.current_letter_idx]['score'] > 65:
            self.current_letter_idx = min(
                self.current_letter_idx + 1,
                len(self.target_word) - 1
            )

    def reset_drawing_state(self):
        self.user_strokes = []
        self.current_stroke = []
        self.current_letter_idx = 0
        self.result = None

    def render(self):
        self.screen.fill((255, 255, 255))

        if self.mode == 'input':
            self.render_input_mode()
        elif self.mode == 'select':
            self.render_select_mode()
        else:
            self.render_drawing_mode()

        pygame.display.flip()

    def render_input_mode(self):
        prompt = self.font_medium.render("Type a word to practice:", True, (0, 0, 0))
        word = self.font_large.render(self.target_word, True, (100, 100, 100))

        self.screen.blit(prompt, (100, 200))
        self.screen.blit(word, (100, 280))

    def render_select_mode(self):
        title = self.font_medium.render("Select practice mode:", True, (0, 0, 0))
        self.screen.blit(title, (200, 180))

        # Trace mode button
        pygame.draw.rect(self.screen, (100, 200, 100), self.buttons['trace'])
        trace_text = self.font_medium.render("TRACE", True, (0, 0, 0))
        self.screen.blit(trace_text, (350, 275))

        # Write mode button
        pygame.draw.rect(self.screen, (200, 100, 100), self.buttons['write'])
        write_text = self.font_medium.render("WRITE", True, (0, 0, 0))
        self.screen.blit(write_text, (350, 375))

    def render_drawing_mode(self):
        # Draw target word (trace mode only)
        if self.mode == 'trace':
            target = self.font_large.render(self.target_word, True, (220, 220, 220))
            self.screen.blit(target, (100, 250))

        # Draw all completed strokes
        for stroke in self.user_strokes:
            if len(stroke) > 1:
                pygame.draw.lines(self.screen, (0, 150, 200), False, [s[:2] for s in stroke], 4)

        # Draw current stroke
        if len(self.current_stroke) > 1:
            pygame.draw.lines(self.screen, (200, 50, 50), False, [s[:2] for s in self.current_stroke], 4)

        # Show feedback
        if self.result:
            self.feedback.render(self.screen, self.result, self.current_letter_idx)


if __name__ == "__main__":
    app = WritingApp()
    app.run()