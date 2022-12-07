import logging
import time
import math
import sys
import tkinter as tk
from PIL import ImageTk, Image

class Point:
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y
    
    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)

class Ray:
    def __init__(self, start_x:float, start_y:float, end_x:float, end_y:float):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.distance = math.dist([start_x, start_y], [end_x, end_y])
        self.direction_x = (end_x - start_x) / self.distance
        self.direction_y = (end_y - start_y) / self.distance
    

class Circle:
    def __init__(self, x:float, y:float, radius:float) -> None:
        self.x = x
        self.y = y
        self.radius = radius

def circle_collision(x:float, y:float, x_pos:float, y_pos:float, radius: float) -> bool:
    distance = math.sqrt((x_pos-x)*(x_pos-x) + (y_pos-y)*(y_pos-y))
    return distance <= radius


class Camera:
    def __init__(self, position: Point, points_to: Point):
        self.position = position
        self.view_vector = Ray(position.x, position.y, points_to.x, points_to.y)
        self.viewport_width = 50
        logging.info("Camera vector = %f, %f", self.view_vector.direction_x, self.view_vector.direction_y)

class Scene:
    def __init__(self, camera: Camera, width=100, height=100):
        self.__entities = []
        self.__rays = []
        self.__width = width
        self.__height = height
        self.__camera = camera
        self.__scene = [0 for i in range(width*height)]

    def add_entity(self, entity:Circle):
        self.__entities.append(entity)
    
    def add_ray(self, entity:Ray):
        self.__rays.append(entity)


    
    def calculate_rays(self):
        viewport_a = Point(45.0, 5.0)
        viewport_b = Point(5.0, 45.0)
        
        viewport_vector = Ray(viewport_a.x, viewport_a.y, viewport_b.x, viewport_b.y)
        
        number_of_rays = 400.0
        pixel_incremental = viewport_vector.distance / number_of_rays
        pixel_number = 0.0
        for iteration in range(int(number_of_rays)):
            view_point = Point((pixel_number*viewport_vector.direction_x) + viewport_vector.start_x, 
                (pixel_number*viewport_vector.direction_y) + viewport_vector.start_y)
            new_ray = Ray(self.__camera.position.x, self.__camera.position.y, view_point.x, view_point.y)
            self.add_ray(new_ray)
            pixel_number = pixel_number + pixel_incremental
    
    def calculate_collisions(self, start_x:float, start_y:float, direction_x:float, direction_y:float):
        already_collided = False
        iterations = 640
        t = 1.0
        # TODO: Can this be redone using ray/circle colission so
        # we dont have to iterate?
        for iteration in range(iterations):
            x = start_x + (t*direction_x)
            y = start_y + (t*direction_y)
                    
            if y < self.__height and x < self.__width:
                index = int((self.__width * int(y)) + int(x))
                if not already_collided:
                    for possible_circle in self.__entities:
                        if circle_collision(x, y, possible_circle.x, possible_circle.y, possible_circle.radius):
                            #logging.info("Collision in: %f, %f. Index: %i", x, y, index)
                            self.__scene[index] = 1
                            already_collided = True
                else:
                    self.__scene[index] = 1

            t = t + 1.0
             

    def render(self):
        self.calculate_rays()
        
        [self.calculate_collisions(ray.start_x, ray.start_y, ray.direction_x, ray.direction_y) for ray in self.__rays]


    def export_to_pgm_file(self, filename):
        with open(filename, "w") as file:
            file.write("P1\n")
            file.write(str(self.__width) + " " + str(self.__height) + "\n")
            
            for i in range(self.__height):
                for j in range(self.__width):
                    if j == 0:
                        file.write(str(self.__scene[(i*self.__width)+j]))
                    elif j == self.__width-1:
                        file.write(" " + str(self.__scene[(i*self.__width)+j]) + "\n")
                    else:
                        file.write(" " + str(self.__scene[(i*self.__width)+j]))


if __name__ ==  "__main__":

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.info("Running raypy...")
    camera_pos = Point(1.0, 1.0)
    camera_view = Point(50.0, 50.0)
    camera = Camera(camera_pos, camera_view)
    scene = Scene(camera, 640, 480)
    scene.add_entity(Circle(50.0, 50.0, 10.0))
    scene.add_entity(Circle(155.0, 255.0, 20.0))
    scene.add_entity(Circle(45.0, 45.0, 15.0))
    scene.add_entity(Circle(30.0, 80.0, 5.0))
    scene.add_entity(Circle(450.0, 140.0, 50.0))
    
    start_time  = time.perf_counter()
    scene.render()

    end_time = time.perf_counter()

    total_time = end_time - start_time

    logging.info("Total rendering time: %f seconds", total_time)

    scene.export_to_pgm_file("out.pgm")

    
    root = tk.Tk()
    my_image = ImageTk.PhotoImage(Image.open("out.pgm"))
    my_label = tk.Label(root, image=my_image)
    my_label.pack()
    
    root.mainloop()
    