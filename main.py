from dataclasses import dataclass, field
from typing import Dict, Optional, List


@dataclass
class FileSystemNode:
    name: str
    is_file: bool = False
    children: Optional[Dict[str, "FileSystemNode"]] = field(default_factory=dict)
    permissions: Dict[str, str] = field(default_factory=dict)

    def add_child(self, child: "FileSystemNode") -> None:
        if self.is_file:
            raise ValueError(f"Cannot add child to a file: {self.name}")
        if child.name in self.children:
            raise ValueError(f"Child with name '{child.name}' already exists.")
        self.children[child.name] = child

    def remove_child(self, child_name: str) -> None:
        if not self.children or child_name not in self.children:
            raise ValueError(f"Child '{child_name}' not found.")
        del self.children[child_name]

    def get_child(self, child_name: str) -> Optional["FileSystemNode"]:
        return self.children.get(child_name)

    def set_permissions(self, user: str, permissions: str) -> None:
        self.permissions[user] = permissions

    def get_permissions(self, user: str) -> Optional[str]:
        return self.permissions.get(user)


class FileSystem:
    def __init__(self):
        self.root = FileSystemNode("/", is_file=False)

    def _traverse(self, path: List[str]) -> Optional[FileSystemNode]:
        current = self.root
        for part in path:
            if not current or current.is_file:
                return None
            current = current.get_child(part)
        return current

    def create(self, path: str, is_file: bool = False) -> None:
        parts = path.strip("/").split("/")
        current = self.root

        for i, part in enumerate(parts):
            if current.is_file:
                raise ValueError(f"Cannot create path inside a file: {current.name}")
            
            child = current.get_child(part)
            if not child:
                new_node = FileSystemNode(name=part, is_file=is_file if i == len(parts) - 1 else False)
                current.add_child(new_node)
                child = new_node
            current = child

        if current.is_file != is_file:
            raise ValueError(f"Path conflict: '{path}' already exists as a different type.")

    def delete(self, path: str) -> None:
        parts = path.strip("/").split("/")
        parent = self._traverse(parts[:-1])
        if not parent:
            raise ValueError("Path not found.")
        parent.remove_child(parts[-1])

    def list_directory(self, path: str = "/") -> List[str]:
        node = self._traverse(path.strip("/").split("/"))
        if not node or node.is_file:
            raise ValueError("Path is not a directory.")
        return list(node.children.keys())

    def search(self, name: str, node: Optional[FileSystemNode] = None, path: str = "") -> List[str]:
        if node is None:
            node = self.root

        results = []
        if node.name == name:
            results.append(path or "/")
        if not node.is_file:
            for child_name, child_node in node.children.items():
                results.extend(self.search(name, child_node, f"{path}/{child_name}".strip("//")))
        return results

    def set_permissions(self, path: str, user: str, permissions: str) -> None:
        node = self._traverse(path.strip("/").split("/"))
        if not node:
            raise ValueError("Path not found.")
        node.set_permissions(user, permissions)

    def get_permissions(self, path: str, user: str) -> Optional[str]:
        node = self._traverse(path.strip("/").split("/"))
        if not node:
            raise ValueError("Path not found.")
        return node.get_permissions(user)


def display_tree(node: FileSystemNode, indent: str = "") -> None:
    if node.is_file:
        print(f"{indent}- {node.name}")
    else:
        print(f"{indent}+ {node.name}")
        for child in node.children.values():
            display_tree(child, indent + "  ")


# Пример использования
fs = FileSystem()
fs.create("dir/subdir")
fs.create("dir/subdir/file1.txt", is_file=True)
fs.create("dir/subdir/file2.txt", is_file=True)
fs.create("dir/file3.txt", is_file=True)
fs.create("dir/subdir2")

# Отображение структуры файловой системы
display_tree(fs.root)

# Пример других операций
print(fs.list_directory("dir/subdir"))
fs.set_permissions("dir/subdir/file1.txt", "user1", "rwx")
print(fs.get_permissions("dir/subdir/file1.txt", "user1"))
print(fs.search("file1.txt"))
