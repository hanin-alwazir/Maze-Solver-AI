# maze_ai.py
from collections import deque

# 0 = طريق مفتوح, 1 = جدار
MAZE = [
    [0,0,0,0,1,0,0,0,0,0],
    [1,1,0,0,1,0,1,1,1,0],
    [0,0,0,1,0,0,0,0,1,0],
    [0,1,0,1,0,1,1,0,1,0],
    [0,1,0,0,0,0,0,0,1,0],
    [0,1,1,1,1,1,0,1,1,0],
    [0,0,0,0,0,0,0,1,0,0],
    [0,1,1,1,1,0,1,1,0,1],
    [0,0,0,0,1,0,0,0,0,0],
    [0,1,1,0,0,0,1,1,1,0],
]
START = (0, 0)
GOAL  = (9, 9)

def draw_maze(path=None):
    path_set = set(path) if path else set()

    for r in range(len(MAZE)):
        line = ""
        for c in range(len(MAZE[0])):
            if (r, c) == START:
                line += "S"
            elif (r, c) == GOAL:
                line += "G"
            elif MAZE[r][c] == 1:
                line += "#"
            elif (r, c) in path_set:
                line += "·"   # المسار
            else:
                line += " "
        print(line)

def in_bounds(r, c):
    return 0 <= r < len(MAZE) and 0 <= c < len(MAZE[0])

def neighbors(pos):
    r, c = pos
    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    result = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc) and MAZE[nr][nc] == 0:
            result.append((nr, nc))
    return result

def bfs(start, goal):
    queue = deque([start])
    parent = {start: None}
    visited_count = 0

    while queue:
        current = queue.popleft()
        visited_count += 1

        if current == goal:
            break

        for nb in neighbors(current):
            if nb not in parent:
                parent[nb] = current
                queue.append(nb)

    if goal not in parent:
        return None, visited_count

    # إعادة بناء المسار
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()

    return path, visited_count
import heapq

def manhattan(a, b):
    # تقدير المسافة للهدف (Heuristic)
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(start, goal):
    # (f, g, node)
    pq = []
    heapq.heappush(pq, (manhattan(start, goal), 0, start))

    parent = {start: None}
    gscore = {start: 0}
    visited_count = 0

    while pq:
        f, g, current = heapq.heappop(pq)
        visited_count += 1

        if current == goal:
            break

        for nb in neighbors(current):
            tentative_g = g + 1
            if nb not in gscore or tentative_g < gscore[nb]:
                gscore[nb] = tentative_g
                parent[nb] = current
                fscore = tentative_g + manhattan(nb, goal)
                heapq.heappush(pq, (fscore, tentative_g, nb))

    if goal not in parent:
        return None, visited_count

    # إعادة بناء المسار
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()

    return path, visited_count




def main():
    import time
    print("This is the maze:\n")

    # BFS
    t0 = time.perf_counter()
    path_bfs, visited_bfs = bfs(START, GOAL)
    t1 = time.perf_counter()

    # A*
    t2 = time.perf_counter()
    path_astar, visited_astar = astar(START, GOAL)
    t3 = time.perf_counter()

    print("BFS visited nodes:", visited_bfs)
    print("BFS path length:", (len(path_bfs) - 1) if path_bfs else None)
    print("BFS time (ms):", round((t1 - t0) * 1000, 3), "\n")

    print("A* visited nodes:", visited_astar)
    print("A* path length:", (len(path_astar) - 1) if path_astar else None)
    print("A* time (ms):", round((t3 - t2) * 1000, 3), "\n")

    if path_astar:
        draw_maze(path_astar)
    else:
        draw_maze()

if __name__ == "__main__":
    main()