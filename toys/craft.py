from toys.gen_letters import gen_scramble
from toys.gen_target import gen_target
from toys.gen_words import gen_words


def main():
    while True:
        input("Press any key to generate a new game...")
        target = gen_target()
        print("Generated target:", target)
        words = gen_words(target)
        print("Generated components:", words)
        scrambled, other = (
            (words[0], words[1])
            if len(words[0]) > len(words[1])
            else (words[1], words[0])
        )
        letters = gen_scramble(scrambled)
        print(f"Target word: {target}\nOther word: {other}\nLetters: {letters}")


if __name__ == "__main__":
    main()
