from cooc import Cooc, BookType

def main() -> None:
    cooc: Cooc = Cooc("res/test/entities.json", "res/test/text.txt", BookType.PAF, 0)
    cooc.find()

if __name__ == "__main__":
    main()
