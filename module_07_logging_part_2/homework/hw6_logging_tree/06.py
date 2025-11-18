import logging
import logging_tree

logger1 = logging.getLogger("main")
logger2 = logging.getLogger("main.module1")
logger3 = logging.getLogger("secondary")

tree_structure = logging_tree.format.build_description()

with open("logging_tree.txt", "w", encoding="utf-8") as file:
    file.write(tree_structure)

print("Структура логгеров записана в файл logging_tree.txt")
