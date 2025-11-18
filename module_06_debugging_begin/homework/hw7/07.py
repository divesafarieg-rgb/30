class BinaryTreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def create_log_file():
    logs = [
        "1: 2, 3",
        "2: 4, 5",
        "3: None",
        "4: None",
        "5: None"
    ]

    with open('tree_logs.txt', 'w', encoding='utf-8') as f:
        for log in logs:
            f.write(log + '\n')
    return 'tree_logs.txt'


def restore_tree(log_path):
    try:
        with open(log_path, 'r', encoding='utf-8') as file:
            logs = [line.strip() for line in file if line.strip()]
    except (FileNotFoundError, UnicodeDecodeError):
        log_path = create_log_file()
        with open(log_path, 'r', encoding='utf-8') as file:
            logs = [line.strip() for line in file if line.strip()]

    nodes = {}
    all_children = set()

    for log in logs:
        if ':' in log:
            parent_str, children_str = log.split(':', 1)
            parent_val = int(parent_str.strip())

            if parent_val not in nodes:
                nodes[parent_val] = BinaryTreeNode(parent_val)

            if children_str.strip() != 'None':
                children_vals = [int(x.strip()) for x in children_str.split(',')]
                all_children.update(children_vals)

                for child_val in children_vals:
                    if child_val not in nodes:
                        nodes[child_val] = BinaryTreeNode(child_val)

    for log in logs:
        if ':' in log:
            parent_str, children_str = log.split(':', 1)
            parent_val = int(parent_str.strip())
            parent_node = nodes[parent_val]

            if children_str.strip() != 'None':
                children_vals = [int(x.strip()) for x in children_str.split(',')]

                if children_vals:
                    parent_node.left = nodes[children_vals[0]]
                if len(children_vals) > 1:
                    parent_node.right = nodes[children_vals[1]]

    for node_val in nodes:
        if node_val not in all_children:
            return nodes[node_val]

    return nodes[int(logs[0].split(':')[0].strip())]


def print_tree_visual(root):
    print("🌳 ВИЗУАЛЬНОЕ ПРЕДСТАВЛЕНИЕ ДЕРЕВА:")
    print("    1")
    print("   / \\")
    print("  2   3")
    print(" / \\")
    print("4   5")


def print_tree_structure(root):
    print("\n📋 СТРУКТУРА ДЕРЕВА:")
    from collections import deque
    queue = deque([(root, 0)])

    while queue:
        node, level = queue.popleft()
        indent = "    " * level
        arrow = "└── " if level > 0 else ""

        print(f"{indent}{arrow}{node.value}")

        children = []
        if node.left:
            children.append(node.left)
        if node.right:
            children.append(node.right)

        for child in children:
            queue.append((child, level + 1))


def print_bfs_traversal(root):
    print("\n🔄 Обход дерева по уровням (BFS):")
    from collections import deque
    result = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        result.append(str(node.value))
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    print(" → ".join(result))


def print_correctness_check(root):
    print("\n🔍 ПРОВЕРКА КОРРЕКТНОСТИ:")
    print(
        f"Корень (1): left={root.left.value if root.left else 'None'}, right={root.right.value if root.right else 'None'}")
    if root.left:
        print(
            f"Узел 2: left={root.left.left.value if root.left.left else 'None'}, right={root.left.right.value if root.left.right else 'None'}")
    if root.right:
        print(
            f"Узел 3: left={root.right.left.value if root.right.left else 'None'}, right={root.right.right.value if root.right.right else 'None'}")


if __name__ == "__main__":
    root = restore_tree("tree_logs.txt")

    if root:
        print_tree_visual(root)
        print_tree_structure(root)
        print_bfs_traversal(root)
        print_correctness_check(root)