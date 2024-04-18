import sys  # 导入 sys 模块，用于处理命令行参数

class Node():  # 定义节点类，用于表示搜索算法中的节点
    def __init__(self, state, parent, action):  # 初始化方法，state表示节点的状态，parent表示父节点，action表示从父节点到该节点的动作
        self.state = state  # 当前节点的状态
        self.parent = parent  # 父节点
        self.action = action  # 到达当前节点的动作

class StackFrontier():  # 定义堆栈型前沿类
    def __init__(self):  # 初始化方法，创建一个空的前沿列表
        self.frontier = []

    def add(self, node):  # 添加节点到前沿
        self.frontier.append(node)

    def contains_state(self, state):  # 检查前沿中是否包含指定状态的节点
        return any(node.state == state for node in self.frontier)

    def empty(self):  # 检查前沿是否为空
        return len(self.frontier) == 0

    def remove(self):  # 从前沿中移除并返回最后一个添加的节点
        if self.empty():  # 如果前沿为空，则抛出异常
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]  # 获取前沿中的最后一个节点
            self.frontier = self.frontier[:-1]  # 移除最后一个节点
            return node  # 返回被移除的节点

class QueueFrontier(StackFrontier):  # 定义队列型前沿类，继承自堆栈型前沿类
    def remove(self):  # 重写移除方法，实现队列的先进先出逻辑
        if self.empty():  # 如果前沿为空，则抛出异常
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]  # 获取前沿中的第一个节点
            self.frontier = self.frontier[1:]  # 移除第一个节点
            return node  # 返回被移除的节点

class Maze():  # 定义迷宫类
    def __init__(self, filename):  # 初始化方法，读取迷宫文件并初始化迷宫
        with open(filename) as f:  # 打开迷宫文件
            contents = f.read()  # 读取文件内容

        # 验证迷宫是否包含一个起点和一个终点
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # 确定迷宫的高度和宽度
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # 记录迷宫的墙壁
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None  # 存储迷宫的解

    def print(self):  # 打印迷宫的方法
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    def neighbors(self, state):  # 获取当前位置的邻居节点
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def solve(self):  # 解决迷宫的方法
        self.num_explored = 0  # 记录探索的状态数量

        # 初始化前沿，将起点添加到前沿中
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)

        # 初始化已探索集合为空集合
        self.explored = set()

        # 循环直到找到解或探索完所有状态
        while True:
            if frontier.empty():  # 如果前沿为空，则抛出异常，表示没有解
                raise Exception("no solution")

            # 选择一个节点从前沿中移除，并增加探索状态数量
            node = frontier.remove()
            self.num_explored += 1

            if node.state == self.goal:  # 如果当前节点是终点，则找到了解，返回解
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # 标记当前节点为已探索状态
            self.explored.add(node.state)

            # 将当前节点的邻居节点添加到前沿中
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    def output_image(self, filename, show_solution=True, show_explored=False):  # 生成迷宫图像的方法
        from PIL import Image, ImageDraw
        cell_size = 50  # 每个单元格的大小
        cell_border = 2  # 单元格边界的宽度

        # 创建空白画布
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        # 获取解（如果存在）
        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # 绘制墙壁
                if col:
                    fill = (40, 40, 40)

                # 绘制起点
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # 绘制终点
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # 绘制解路径
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # 绘制已探索状态
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # 绘制空白单元格
                else:
                    fill = (237, 240, 252)

                # 绘制单元格
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)  # 保存图片文件


if len(sys.argv) != 2:  # 检查命令行参数是否正确
    sys.exit("Usage: python maze.py maze.txt")  # 如果参数不正确，则退出并显示用法提示

m = Maze(sys.argv[1])  # 创建迷宫对象
print("Maze:")
m.print()  # 打印迷宫
print("Solving...")
m.solve()  # 解决迷宫
print("States Explored:", m.num_explored)  # 打印探索状态数量
print("Solution:")
m.print()  # 打印解
m.output_image("maze.png", show_explored=True)  # 生成迷宫图像，并显示已探索状态
#12