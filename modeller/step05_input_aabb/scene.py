import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from .shapes import *
from ..common.trackball import Trackball


class Scene:
    def __init__(self):
        define_shapes()
        self.shapes = [Plane()]
        self.trackball = Trackball(theta=-25, distance=15)
        self.translation = [0, 0, 0, 0]
        self.inverseModelView = np.identity(4)
        self.modelView = np.identity(4)
        self.selected_shape = None

    def add_samle_shapes(self):
        cube = Cube(color_index=1)
        cube.translate(2, 0, 2)
        self.shapes.append(cube)

        sphere = Sphere(color_index=3)
        sphere.translate(-2, 0, 2)
        self.shapes.append(sphere)

        snowball = Snowball()
        snowball.translate(-2, 0, -2)
        self.shapes.append(snowball)

    def get_shapes(self, active):
        return [x for x in self.shapes if x.is_active() == active]

    def translate(self, x, y, z):
        self.translation[0] += x
        self.translation[1] += y
        self.translation[2] += z

    def init_view(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        aspect_ratio = float(xSize) / float(ySize)
        glViewport(0, 0, xSize, ySize)
        gluPerspective(70, aspect_ratio, 0.1, 1000.0)
        glTranslated(0, 0, -15)

    def render(self):
        self.init_view()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslate(self.translation[0], self.translation[1], self.translation[2])
        tb_mat = self.trackball.matrix
        glMultMatrixf(tb_mat)
        currentModelView = np.array(glGetFloatv(GL_MODELVIEW_MATRIX))
        self.modelView = np.transpose(currentModelView)
        self.inverseModelView = np.linalg.inv(np.transpose(currentModelView))

        glDisable(GL_LIGHTING)
        for shape in self.get_shapes(False):
            shape.render()

        glEnable(GL_LIGHTING)
        for shape in self.get_shapes(True):
            shape.render()

        glPopMatrix()
        glFlush()

    def drag(self, pos, delta):
        self.trackball.drag_to(pos[0], pos[1], delta[0], delta[1])

    def get_ray(self, pos):
        """ Generate a ray beginning at the near plane, in the direction that the x, y coordinates are facing
            Consumes: x, y coordinates of mouse on screen
            Return: start, direction of the ray """
        self.init_view()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        start = np.array(gluUnProject(pos[0], pos[1], 0.001))
        end = np.array(gluUnProject(pos[0], pos[1], 0.999))
        direction = end - start
        direction = direction / np.linalg.norm(direction)
        return start, direction

    def pick(self, pos):
        start, direction = self.get_ray(pos)
        nearest_shape, nearest_distance = None, 2147483647  # sys.maxint
        for shape in self.get_shapes(True):
            hit, distance = shape.pick(start, direction, self.modelView)
            if hit and distance < nearest_distance:
                nearest_distance, nearest_shape = distance, shape

        for child in self.get_shapes(True):
            child.selected = (child is nearest_shape)
        self.selected_shape = nearest_shape
