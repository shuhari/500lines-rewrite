import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from .shapes import *
from ..common.trackball import Trackball


class Scene:
    PLACE_DEPTH = 15.0

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

        selected_loc = start + direction * nearest_distance
        for child in self.get_shapes(True):
            if child is nearest_shape:
                child.select(nearest_distance, selected_loc)
            else:
                child.deselect()
        self.selected_shape = nearest_shape

    def move(self, pos):
        shape = self.selected_shape
        if shape is None or not shape.selected:
            return
        start, direction = self.get_ray(pos)
        depth, oldloc = shape.get_select_loc()
        newloc = (start + direction * depth)

        translation = newloc - oldloc
        pre_tran = np.array([translation[0], translation[1], translation[2], 0])
        translation = self.inverseModelView.dot(pre_tran)

        shape.translate(translation[0], translation[1], translation[2])
        shape.select(depth, newloc)

    def scale_selected(self, up):
        shape = self.selected_shape
        if shape is None or not shape.selected:
            return
        s = 1.1 if up else 0.9
        shape.scale(s, s, s)

    def rotate_color(self, forward):
        shape = self.selected_shape
        if shape is None or not shape.selected:
            return
        shape.rotate_color(forward)

    def place(self, type_name, pos):
        start, direction = self.get_ray(pos)
        # self.scene.place(shape, start, direction, self.inverseModelView)
        new_shape = None
        if type_name == 'sphere':
            new_shape = Sphere()
        elif type_name == 'cube':
            new_shape = Cube()
        elif type_name == 'snowball':
            new_shape = Snowball()

        if new_shape is not None:
            translation = (start + direction * self.PLACE_DEPTH)
            pre_tran = np.array([translation[0], translation[1], translation[2], 1])
            translation = self.inverseModelView.dot(pre_tran)
            new_shape.translate(translation[0], translation[1], translation[2])
            self.shapes.append(new_shape)
