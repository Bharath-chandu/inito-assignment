class Node:
    def __init__(self, name, is_dir=True, data=None):
        self.name = name
        self.is_dir = is_dir
        self.data = data
        self.children = {}

class FileSystem:
    def __init__(self, save_path=None, load_path=None):
        self.root = Node("/")
        self.current_dir = self.root
        self.save_path = save_path
        self.load_path = load_path
        if load_path:
            self._load_state()

    def _load_state(self):
        with open(self.load_path, "r") as f:
            state = json.load(f)
            self.root = Node.from_json(state)

    def _save_state(self):
        if self.save_path:
            with open(self.save_path, "w") as f:
                json.dump(self.root.to_json(), f)

    def cd(self, path):
        if path == "..":
            if self.current_dir.parent:
                self.current_dir = self.current_dir.parent
            else:
                print("Error: Already at root directory")
        elif path == "/":
            self.current_dir = self.root
        elif "/" in path:
            # Absolute path
            self.current_dir = self.root
            for dir_name in path.split("/")[1:]:
                if dir_name not in self.current_dir.children:
                    print(f"Error: Directory '{dir_name}' does not exist")
                    return
                self.current_dir = self.current_dir.children[dir_name]
        else:
            # Relative path
            if path not in self.current_dir.children:
                print(f"Error: Directory '{path}' does not exist")
                return
            self.current_dir = self.current_dir.children[path]

    def mv(self, source, destination):
        # Separate source and destination paths
        src_dir, src_file = os.path.split(source)
        dst_dir, dst_file = os.path.split(destination)

        # Find source file/directory
        if src_dir == ".":
            src_dir = self.current_dir.name
        src_node = self._find_node(src_dir, src_file)
        if not src_node:
            print(f"Error: '{source}' does not exist")
            return

        # Find destination directory
        dst_node = self._find_node(dst_dir)
        if not dst_node or not dst_node.is_dir:
            print(f"Error: Destination '{dst_dir}' is not a directory")
            return

        # Check if destination file already exists
        if dst_file in dst_node.children:
            print(f"Error: File '{dst_file}' already exists")
            return

        # Move the node
        src_node.parent.children.pop(src_file)
        dst_node.children[dst_file] = src_node
        src_node.parent = dst_node

    def cp(self, source, destination):
        # Separate source and destination paths
        src_dir, src_file = os.path.split(source)
        dst_dir, dst_file = os.path.split(destination)

        # Find source file
        if src_dir == ".":
            src_dir = self.current_dir.name
        src_node = self._find_node(src_dir, src_file)
        if not src_node or not src_node.is_dir:
            print(f"Error: '{source}' does not exist")
            return

        # Find destination directory
        dst_node = self._find_node(dst_dir)
        if not dst_node or not dst_node.is_dir:
            print(f"Error: Destination '{dst_dir}' is not a directory")
            return

        # Create a copy of the source node
        new_node = Node(src_file)
        new_node.is_dir = src_node
