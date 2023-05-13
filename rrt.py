import random
import math
import pygame
from enum import IntEnum
from skspatial.objects import Line, Circle

class Point(IntEnum):
    ID = 0
    COORDINATES = 1
    NODE_ID = 2
    DISTANCE = 1
    X = 0
    Y = 1


class RRT():
    def __init__(self, obstacle_board, start_point=None, end_point=None, maximum_branch_length=10):
        self.obstacle_board = obstacle_board

        if start_point is None:
            self.start_point = (random.randint(0, 400), random.randint(0, 400))
        else:
            self.start_point = start_point
        if end_point is None:
            self.end_point = (random.randint(0, 400), random.randint(0, 400))
        else:
            self.end_point = end_point

        self.total_steps = 0
        self.maximum_branch_length = maximum_branch_length
        self.tree_points = [[0, self.start_point, None]]

    def expand_tree(self, n_steps):
        i = len(self.tree_points)
        limit = i + n_steps
        
        while i < limit:            
            pygame.event.get()
            random_point = (random.randint(0, 400), random.randint(0, 400))
            distance_list = self.calculate_distance_with_other_points(random_point)
            closest_point_id, closest_point_distance = distance_list[0][Point.ID], distance_list[0][Point.DISTANCE]

            if closest_point_distance > self.maximum_branch_length:
                try:
                    tree_point = self.set_point_coordinates_after_limiting_branch_length(random_point, closest_point_id)
                except Exception:
                    continue
            else:
                tree_point = random_point

            if self.check_obstacle_colision(tree_point):
                continue

            self.tree_points.append([i, tree_point, closest_point_id])
            i += 1

        rrt.total_steps += n_steps

    def calculate_distance_with_other_points(self, random_point):
        distance_list = []
        for tree_point in self.tree_points:
            point_id, point_coordinates = tree_point[Point.ID], tree_point[Point.COORDINATES]
            distance = math.dist(random_point, point_coordinates)
            distance_list.append([point_id, distance])
        distance_list.sort(key=self.sorting_distance_function)
        return distance_list

    def sorting_distance_function(self, element):
        return element[1]

    def set_point_coordinates_after_limiting_branch_length(self, random_point, point_id):
        line = Line.from_points(random_point, self.tree_points[point_id][Point.COORDINATES])
        circle = Circle(self.tree_points[point_id][Point.COORDINATES], self.maximum_branch_length)
        result = circle.intersect_line(line)

        point_1 = (result[0][0], result[0][1])
        point_2 = (result[1][0], result[1][1])
        
        distance1 = math.dist(random_point, point_1)
        distance2 = math.dist(random_point, point_2)
        
        if distance1 < distance2:
            return point_1
        else:
            return point_2

    def calculate_distance_to_start(self, point):
        point_id = point[Point.ID]
        point_node_id = self.tree_points[point_id][Point.NODE_ID]
        distance = 0
        while point_node_id is not None:
            distance += math.dist(self.tree_points[point_id][Point.COORDINATES], self.tree_points[point_node_id][Point.COORDINATES])
            point_id = point_node_id
            point_node_id = self.tree_points[point_node_id][Point.NODE_ID]
        return distance

    def goal_reached(self):
        self.goal_points = [point for point in self.tree_points if math.dist(point[Point.COORDINATES], self.end_point) <= 20]
        return True if len(self.goal_points) > 0 else False

    def calculate_optimal_path(self):
        if self.goal_reached():
            distance_list = []
            for goal_point in self.goal_points:
                goal_point_id = goal_point[Point.ID]
                distance = self.calculate_distance_to_start(goal_point)
                distance_list.append([goal_point_id, distance])
            distance_list.sort(key=self.sorting_distance_function)
            return distance_list[0][Point.ID], distance_list[0][Point.DISTANCE]
        else:
            return None, 0

    def check_obstacle_colision(self, point):
        for obstacle in self.obstacle_board:
            if (point[Point.X] > obstacle[0][Point.X] and point[Point.X] < obstacle[1][Point.X] and point[Point.Y] > obstacle[0][Point.Y] and point[Point.Y] < obstacle[1][Point.Y]) :
                return True
        return False

    def get_midpoint(self, point1, point2):
        return ((point1[Point.X] + point2[Point.X]) / 2, (point1[Point.Y] + point2[Point.Y]) / 2)


class GUI:
    def __init__(self, screen_size, background_color):
        pygame.init()
        self.background_color = background_color
        self.screen = pygame.display.set_mode(screen_size)
        self.screen.fill(self.background_color)
        pygame.display.flip()

    def draw_start_end_points(self, start_point, end_point):
        pygame.draw.circle(self.screen, pygame.Color(255, 0, 0), start_point, 10, 2)
        pygame.draw.circle(self.screen, pygame.Color(0, 255, 0), end_point, 20, 2)
        pygame.display.update()

    def draw_tree(self, start_point, end_point, obstacle_board, tree_points):
        self.screen.fill(self.background_color)
        self.draw_start_end_points(start_point, end_point)
        self.draw_obstacles(obstacle_board)
        for point in tree_points:
            if point[Point.NODE_ID] is not None:
                pygame.draw.line(self.screen, pygame.Color(0, 0, 255), tree_points[point[Point.ID]][Point.COORDINATES], tree_points[point[Point.NODE_ID]][Point.COORDINATES])
        pygame.display.update()

    def draw_optimal_path(self, goal_point_id, tree_points):
        point = tree_points[goal_point_id]
        while point[Point.NODE_ID] is not None:
            pygame.draw.line(self.screen, pygame.Color(102, 0, 102), tree_points[point[Point.ID]][Point.COORDINATES], tree_points[point[Point.NODE_ID]][Point.COORDINATES], 3)
            point = tree_points[point[Point.NODE_ID]]
        pygame.display.update()

    def draw_obstacles(self, obstacle_board):
        for obstacle in obstacle_board:
            pygame.draw.rect(self.screen, pygame.Color(0, 0, 0), pygame.Rect(obstacle[0][Point.X], obstacle[0][Point.Y], obstacle[1][Point.X] - obstacle[0][Point.X], obstacle[1][Point.Y] - obstacle [0][Point.Y]))
        pygame.display.update()

if __name__ == "__main__":
    obstacle_boards = {
        "1": [[(75, 0), (125, 175)], [(275, 0), (325, 175)], [(275, 225), (325, 400)], [(75, 225), (125, 400)]],
        "2": [[(50, 100), (110, 400)], [(170, 0), (230, 300)], [(290, 100), (350, 400)]],
        "3": [[(175, 0), (225, 120)], [(280, 175), (400, 225)], [(175, 280), (225, 400)], [(0, 175), (120, 225)]],
        "4": [[(50, 50), (175, 175)], [(225, 50), (350, 175)], [(50, 225), (175, 350)], [(225, 225), (350, 350)]]
    }

    print("\nAlgorytm RRT\n")
    while True:
        board_id = input("Wybierz planszę przeszkód (1-4): ")
        if obstacle_boards.get(board_id) is None:
            print("Wprowadzono niepoprawną wartość!")
        else:
            obstacle_board = obstacle_boards.get(board_id)
            break

    rrt = RRT(obstacle_board, (25, 25), (375, 375))
    gui = GUI((400, 400), (255, 255, 255))
    gui.draw_start_end_points(rrt.start_point, rrt.end_point)
    gui.draw_obstacles(rrt.obstacle_board)
    while True:
        pygame.event.get()
        step = input("Podaj ilość kroków: ")
        if step == "0":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            break
        else:
            rrt.expand_tree(int(step))
            print(f"\n=====================\n\nWykonano {rrt.total_steps} kroków")
            print
            gui.draw_tree(rrt.start_point, rrt.end_point, rrt.obstacle_board, rrt.tree_points)
            goal_point_id, distance_to_goal = rrt.calculate_optimal_path()
            if distance_to_goal > 0:
                print("Dystans do celu: " + str(distance_to_goal) + "\n=====================\n")
                gui.draw_optimal_path(goal_point_id, rrt.tree_points)
            else:
                print("Nie osiągnięto celu\n\n=====================\n")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break