import pygame
import random
import math
import heapq
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from threading import Thread

galpha = int(input("G__alpha..... 0/1? : "))

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
MIN_DOTS = 1
MAX_DOTS = 50
MIN_SPEED = 1
MAX_SPEED = 15
DISTANCE_THRESHOLD = WINDOW_WIDTH/7
FPS = 60

class Dot:
    _id_counter = 0
    def __init__(self, x, y, speed_x=0, speed_y=0, is_fixed=False):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.is_fixed = is_fixed
        self.id = Dot._id_counter
        Dot._id_counter += 1

    def move(self):
        if not self.is_fixed:
            self.x += self.speed_x
            self.y += self.speed_y

            if self.x <= 0 or self.x >= WINDOW_WIDTH:
                self.speed_x *= -1
            if self.y <= 0 or self.y >= WINDOW_HEIGHT:
                self.speed_y *= -1

    def __eq__(self, other):
        if isinstance(other, Dot):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)


def distance(dot1, dot2):
    return math.sqrt((dot1.x - dot2.x) ** 2 + (dot1.y - dot2.y) ** 2)

def update_value1(val):
    global DISTANCE_THRESHOLD
    DISTANCE_THRESHOLD = float(val)

def update_value2(val):
    global MAX_DOTS, dots
    MAX_DOTS = int(val)
    initialize_dots()

def update_value3(val):
    global MAX_SPEED
    MAX_SPEED = int(val)
    for dot in dots:
        dot.speed_x = random.uniform(-MAX_SPEED, MAX_SPEED)
        dot.speed_y = random.uniform(-MAX_SPEED, MAX_SPEED)

    
def run_tkinter():
    root = tk.Tk()
    root.title("Control Panel")
    root.geometry("600x300")
    
    font = ("Arial", 6)
    tk.Label(root, text="THRESHOLD", font=font).pack(pady=5)
    slider1 = tk.Scale(root, from_=0, to=500, orient="horizontal", command=update_value1, length=300)
    slider1.pack(pady=5)
    
    tk.Label(root, text="PARTICLES", font=font).pack(pady=5)
    slider2 = tk.Scale(root, from_=1, to=200, orient="horizontal", command=update_value2, length=300)
    slider2.pack(pady=5)
    
    tk.Label(root, text="MAX SPEED", font=font).pack(pady=5)
    slider3 = tk.Scale(root, from_=1, to=50, orient="horizontal", command=update_value3, length=300)
    slider3.pack(pady=5)
    
    root.mainloop()

Thread(target=run_tkinter, daemon=True).start()


def find_shortest_path_dijkstra(dots, start, end, threshold):
    graph = {}
    for dot in dots:
        graph[(dot.x, dot.y)] = []

    if (start.x, start.y) not in graph:
        graph[(start.x, start.y)] = []
    if (end.x, end.y) not in graph:
        graph[(end.x, end.y)] = []

    for i in range(len(dots)):
        for j in range(i + 1, len(dots)):
            if distance(dots[i], dots[j]) < threshold:
                graph[(dots[i].x, dots[i].y)].append((distance(dots[i], dots[j]), (dots[j].x, dots[j].y)))
                graph[(dots[j].x, dots[j].y)].append((distance(dots[j], dots[i]), (dots[i].x, dots[i].y)))

    for dot in dots:
        if distance(dot, start) < threshold:
            graph[(start.x, start.y)].append((distance(dot, start), (dot.x, dot.y)))
            graph[(dot.x, dot.y)].append((distance(start, dot), (start.x, start.y)))

        if distance(dot, end) < threshold:
            graph[(end.x, end.y)].append((distance(dot, end), (dot.x, dot.y)))
            graph[(dot.x, dot.y)].append((distance(end, dot), (end.x, end.y)))

    pq = [(0, (start.x, start.y), [])]
    visited = set()

    while pq:
        current_distance, current_dot, path = heapq.heappop(pq)

        if current_dot in visited:
            continue
        visited.add(current_dot)

        path = path + [current_dot]

        if current_dot == (end.x, end.y):
            return path, current_distance

        for neighbor_distance, neighbor in graph[current_dot]:
            if neighbor not in visited:
                heapq.heappush(pq, (current_distance + neighbor_distance, neighbor, path))


    return [], float('inf')


pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Traffic Simulation")

clock = pygame.time.Clock()
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 175, 0)
PURPLE = (255, 0, 255)
BLACK = (0, 0, 0)

distance_threshold = DISTANCE_THRESHOLD
fixed_points = [
    Dot(0, WINDOW_HEIGHT // 2, is_fixed=True),
    Dot(WINDOW_WIDTH, WINDOW_HEIGHT // 2, is_fixed=True)
]

dots = []
def initialize_dots():
    global dots
    dots = [Dot(random.randint(100, WINDOW_WIDTH - 100),
                random.randint(50, WINDOW_HEIGHT - 50),
                random.uniform(-MAX_SPEED, MAX_SPEED),
                random.uniform(-MAX_SPEED, MAX_SPEED))
            for _ in range(MAX_DOTS)]
    dots.extend(fixed_points)
initialize_dots()


cycle = 0
signal_strengths = []
fig, ax = plt.subplots()
x_data, y_data = [], []
line, = ax.plot([], [], color='purple')

def init_plot():
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    return line,

def update_plot(frame):
    global cycle, signal_strengths
    
    x_data.append(cycle)
    y_data.append(signal_strengths[-1]) if signal_strengths else y_data.append(0)
    
    line.set_data(x_data, y_data)

    if cycle > ax.get_xlim()[1]:
        ax.set_xlim(0, cycle + 20)
    
    return line,

ani = FuncAnimation(fig, update_plot, init_func=init_plot, blit=True, interval=100, cache_frame_data=False)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    distance_threshold = DISTANCE_THRESHOLD
    fixed_points = [
        Dot(0, WINDOW_HEIGHT // 2, is_fixed=True),
        Dot(WINDOW_WIDTH, WINDOW_HEIGHT // 2, is_fixed=True)
    ]

    for dot in dots:
        dot.move()

    screen.fill(BLACK)

    for point in fixed_points:
        pygame.draw.circle(screen, RED, (int(point.x), int(point.y)), 3)

    for dot in dots:
        pygame.draw.circle(screen, GREEN, (int(dot.x), int(dot.y)), 3)

    for i in range(len(dots)):
        for j in range(i + 1, len(dots)):
            dist = distance(dots[i], dots[j])
            if dist < distance_threshold:
                if galpha == 1:
                    glevel = round(255 * (1 - (dist/distance_threshold)**2))
                else:
                    glevel = 255
                pygame.draw.line(screen, (0,glevel,0), (int(dots[i].x), int(dots[i].y)),
                                 (int(dots[j].x), int(dots[j].y)), 1)

    shortest_path, shortest_distance = find_shortest_path_dijkstra(dots, fixed_points[0], fixed_points[1], distance_threshold)

    if shortest_path:
        pygame.draw.lines(screen, (0, 255, 255), False, shortest_path, 5)
        for dot in shortest_path:
            pygame.draw.circle(screen, (0, 255, 255), dot, 5)


    if shortest_distance != float('inf'):
        signal_strength = 100 * ((1400 / shortest_distance)**2) * 0.8
    else:
        signal_strength = 0

    signal_strengths.append(signal_strength)
    cycle += 1
    print(f"Signal strength: {signal_strength:.2f}%")


    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()

# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script
# Fake active script