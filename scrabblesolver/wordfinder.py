

class WordFinder:

    def __init__(self, dictionary):
        self.dictionary = dictionary

    def highest_value_word(self, letters):
        return self.__highest_value(self.possible_words(letters))

    def possible_words(self, letters):
        letter_permutations = self.__permute("", letters, [])

        words = []
        for permutation in letter_permutations:
            if self.dictionary.is_word(permutation) and permutation not in words:
                words.append(permutation)
        words.sort()
        return words

    def __permute(self, so_far, left, permutations):
        if len(left) < 1:
            permutations.append(so_far)
            return permutations

        for i in range(len(left)):
            next = so_far + left[i]
            remaining = left[0:i] + left[i + 1:len(left)]

            if len(remaining) > 0:
                permutations.append(next)

            if self.dictionary.number_of_sub_words(next) > 0:
                permutations = self.__permute(next, remaining, permutations)

        return permutations

    def __highest_value(self, words):
        return words[0]
        '''
        highest_value = 0
        highest_word = None

        for word in words:
            word_value = WordValue.value(word)
            if word_value > highest_value:
                highest_value = word_value
                highest_word = word

        return highest_word
        '''


class Dictionary:
    root = None
    dictionary = None

    def __init__(self):
        self.root = LetterNode('', '', False)

    def add_word(self, word):
        index = self.root

        for (i, c) in enumerate(word):
            if c in index.sub_letters:
                index.sub_word_count += 1
                index = index.sub_letters[c]
            else:
                new_node = LetterNode(c, word[0:i+1], False if i < len(word)-1 else True)
                index.sub_letters[c] = new_node
                index = index.sub_letters[c]

    def is_word(self, letters):
        node = self.__find_node(letters)
        return True if node is not None and node.is_word else False

    def number_of_sub_words(self, letters):
        node = self.__find_node(letters)
        return node.sub_word_count if node is not None else 0

    def __find_node(self, letters):
        index = self.root

        for i in range(len(letters)):
            if index.sub_letters.get(letters[i]) is not None:
                index = index.sub_letters[letters[i]]
            else:
                return None

        return index if index.all_letters == letters else None


class LetterNode:
    def __init__(self, key_character, all_characters, is_word):
        self.key_letter = key_character
        self.all_letters = all_characters
        self.is_word = is_word
        self.sub_letters = dict()
        self.sub_word_count = 0

    def __repr__(self):
        return 'key: %s, all_letters: %s' % (self.key_letter, self.all_letters)
