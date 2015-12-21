import sys
import pygame
from graphs.graph import *


class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)
    DARK_RED = (128, 0, 0)


class ScrabbleGame:
    def __init__(self):
        pygame.init()
        self.windowSize = (600, 800)
        self.screen = pygame.display.set_mode(self.windowSize)
        self.clock = pygame.time.Clock()
        self.game_board = SquareBoard(self.screen, x=0, y=0, length=self.windowSize[0])
        self.hand = Board(self.screen,
                          (0, self.windowSize[0] + 50,
                           self.windowSize[0], int(self.windowSize[0] / 10)),
                          1, 10)
        self.word_list = WordList(self.screen,
                                  (self.hand.pos[0], self.hand.pos[1] + self.hand.size[1] + 10,
                                   self.windowSize[0], 80))
        self.selected_board = None

        # Load dictionary file
        file = open('ospd.txt', mode='rt', encoding='utf-8')

        # Build character tree
        character_tree = CharacterTree()
        for line in file:
            character_tree.add_word(line.rstrip('\n'))

        self.word_finder = WordFinder(character_tree)

    def start(self):
        while True:
            self.clock.tick(100)

            self.screen.fill(Colors.BLACK)
            self.handle_events(pygame.event.get())
            self.game_board.draw()
            self.hand.draw()
            self.word_list.draw()

            pygame.display.update()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                print("mouse clicked")
                print(pygame.mouse.get_pos())
                print(event.button)

                if self.selected_board is not None:
                    self.selected_board.deselect()

                mouse_pos = pygame.mouse.get_pos()
                if (mouse_pos[0] in range(self.game_board.pos[0], self.game_board.pos[0] + self.game_board.size[0] + 1) and
                        mouse_pos[1] in range(self.game_board.pos[1], self.game_board.pos[1] + self.game_board.size[1] + 1)):
                    self.game_board.select_tile(self.game_board.get_tile_on_screen(mouse_pos))
                    self.selected_board = self.game_board
                elif (mouse_pos[0] in range(self.hand.pos[0], self.hand.pos[0] + self.hand.size[0] + 1) and
                        mouse_pos[1] in range(self.hand.pos[1], self.hand.pos[1] + self.hand.size[1] + 1)):
                    self.hand.select_tile(self.hand.get_tile_on_screen(mouse_pos))
                    self.selected_board = self.hand
            elif event.type == pygame.KEYUP:
                if self.selected_board is not None and self.selected_board.current_selected_tile is not None:
                    if event.key == pygame.K_BACKSPACE:
                        self.selected_board.current_selected_tile.letter = ""
                    elif event.key == pygame.K_LEFT:
                        self.selected_board.move_left()
                    elif event.key == pygame.K_RIGHT:
                        self.selected_board.move_right()
                    elif event.key == pygame.K_UP:
                        self.selected_board.move_up()
                    elif event.key == pygame.K_DOWN:
                        self.selected_board.move_down()
                    else:
                        self.selected_board.current_selected_tile.letter = pygame.key.name(event.key)


class Board:
    def __init__(self, surface, rect, rows, cols):
        self.surface = surface
        self.pos = rect[0:2]
        self.size = rect[2:4]
        self.tile_size = (self.size[0] / cols, self.size[1] / rows)
        self.rows = rows
        self.cols = cols
        self.font = pygame.font.SysFont("Myriad Pro", 48)  # TODO: base font on tile size
        self.tile_boarder_size = 2
        self.current_selected_tile = None
        self._init_tiles()

    def _init_tiles(self):
        self.tiles = [None] * self.rows
        for i in range(self.rows):
            self.tiles[i] = [None] * self.cols

        for r in range(self.rows):
            for c in range(self.cols):
                self.tiles[r][c] = Tile("", r, c)

    def draw(self):
        # Draw tiles
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.tiles[r][c]
                top_left_corner = (c * self.tile_size[0] + self.pos[0],
                                   r * self.tile_size[1] + self.pos[1])

                # Draw tile bg
                pygame.draw.rect(self.surface,
                                 Colors.YELLOW if tile.is_selected else Colors.WHITE,
                                 (top_left_corner[0] + self.tile_boarder_size, top_left_corner[1] + self.tile_boarder_size,
                                  self.tile_size[0] - self.tile_boarder_size, self.tile_size[1] - self.tile_boarder_size))

                # draw tile letter
                tile_text = self.font.render(tile.letter, 1, Colors.DARK_RED)
                text_size = tile_text.get_size()
                text_offset = (text_size[0] / 2, text_size[1] / 2)
                center = (top_left_corner[0] + self.tile_size[0] / 2,
                          top_left_corner[1] + self.tile_size[1] / 2)
                self.surface.blit(tile_text, (center[0] - text_offset[0], center[1] - text_offset[1]))

    def get_tile_on_screen(self, pos):
        x = pos[0]
        y = pos[1]

        if x > self.size[0] + self.pos[0] or x < self.pos[0] or y > self.size[1] + self.pos[1] or y < self.pos[1]:
            return None

        row_coords = []
        col_coords = []
        for i in range(self.rows + 1):
            row_coords.append(int(i * self.tile_size[1] + self.pos[1]))
        for i in range(self.cols + 1):
            col_coords.append(int(i * self.tile_size[0] + self.pos[0]))

        # find row
        row = 0
        for i, r in enumerate(row_coords):
            if y >= r and (i < len(row_coords) - 1 and y < row_coords[i + 1]):
                row = i
                break

        # find the column
        col = 0
        for i, c in enumerate(col_coords):
            if x >= c and (i < len(col_coords) - 1 and x < col_coords[i + 1]):
                col = i
                break

        return self.tiles[row][col]

    def select_tile(self, tile):
        if tile is None:
            return

        if self.current_selected_tile is not None:
            self.current_selected_tile.is_selected = False

        tile.is_selected = True
        self.current_selected_tile = tile

    def deselect(self):
        if self.current_selected_tile is not None:
            self.current_selected_tile.is_selected = False
            self.current_selected_tile = None

    def move_left(self):
        if self.current_selected_tile is not None and self.current_selected_tile.col > 0:
            self.select_tile(self.tiles[self.current_selected_tile.row][self.current_selected_tile.col - 1])

    def move_right(self):
        if self.current_selected_tile is not None and self.current_selected_tile.col < self.cols - 1:
            self.select_tile(self.tiles[self.current_selected_tile.row][self.current_selected_tile.col + 1])

    def move_up(self):
        if self.current_selected_tile is not None and self.current_selected_tile.row > 0:
            self.select_tile(self.tiles[self.current_selected_tile.row - 1][self.current_selected_tile.col])

    def move_down(self):
        if self.current_selected_tile is not None and self.current_selected_tile.row < self.rows - 1:
            self.select_tile(self.tiles[self.current_selected_tile.row + 1][self.current_selected_tile.col])


class SquareBoard(Board):
    rows_and_columns = 15
    tiles = None
    tile_boarder_size = 2
    current_selected_tile = None

    def __init__(self, surface, x, y, length):
        super().__init__(surface, (x, y, length, length), self.rows_and_columns, self.rows_and_columns)


class Hand:
    letters = []

    def add_letters(self, letters):
        pass

    def remove_letters(self, letters):
        pass


class Tile:
    letter = ""
    is_selected = False

    def __init__(self, letter, row, col):
        self.letter = letter
        self.row = row
        self.col = col


class WordList:
    words = ["apple", "ape", "ale", "pale", "pal", "leap", "plea", "lep", "pep"]

    def __init__(self, surface, rect):
        self.surface = surface
        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2]
        self.h = rect[3]
        self.font = pygame.font.SysFont("Myriad Pro", 24)

    def draw(self):
        row = 0
        x_offset = 0
        longest_word_width = 0

        for (i, word) in enumerate(self.words):
            text = self.font.render(word, 1, Colors.WHITE)
            text_size = text.get_size()
            text_pos = (self.x + x_offset, self.y + (row * text_size[1]))

            if text_size[1] > longest_word_width:
                longest_word_width = text_size[0]

            if (text_pos[1] + text_size[1]) > (self.y + self.h):
                # go to next row
                x_offset += longest_word_width + 10
                longest_word_width = 0
                row = 0
                text_pos = (self.x + x_offset, self.y + (row * text_size[1]))

            self.surface.blit(text, text_pos)

            row += 1


class WordFinder:

    def __init__(self, word_tree):
        self.word_tree = word_tree

    def find_words(self, characters):
        """Takes a character string and permutes it to find all possible words."""
        pass


class CharacterTree:
    root = None
    dictionary = None

    def __init__(self):
        pass

    def add_word(self, word):
        index = self.root

        for c in word:
            if c in index.sub_characters:
                index = index.sub_characters[c]
            else:
                new_node = CharacterNode(c, "", False)
                index.sub_characters[c] = new_node

    #def add_character(self, character, base_node):
    #    pass

    def get_node(self, characters, starting_from=root):
        pass


class CharacterNode:
    key_character = ''
    all_characters = ''
    is_word = False
    sub_characters = dict()
    sub_word_count = 0

    def __init__(self, key_character, all_characters, is_word):
        self.key_character = key_character
        self.all_characters = all_characters
        self.is_word = is_word

scrabble = ScrabbleGame()
scrabble.start()
