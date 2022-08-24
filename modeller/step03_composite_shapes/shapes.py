import random

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


__all__ = ['Shape', 'Plane', 'Sphere', 'Cube', 'Snowball', 'define_shapes']


class Shape:
    COLORS = [
        (1.0, 1.0, 1.0),
        (0.05, 0.05, 0.9),
        (0.05, 0.9, 0.05),
        (0.9, 0.05, 0.05),
        (0.9, 0.9, 0.0),
        (0.1, 0.8, 0.7),
        (0.7, 0.2, 0.7),
        (0.7, 0.7, 0.7),
        (0.4, 0.4, 0.4),
        (0.0, 0.0, 0.0),
    ]

    def random_color_index(self):
        return random.randint(0, len(self.COLORS) - 1)

    def is_active(self):
        return isinstance(self, ActiveMixin)


class Plane(Shape):
    id = 1

    @classmethod
    def define(cls):

        def make_lines(color, points):
            glBegin(GL_LINES)
            glColor3f(color[0], color[1], color[2])
            for pt in points:
                glVertex3f(pt[0], pt[1], pt[2])
            glEnd()

        glNewList(cls.id, GL_COMPILE)
        glBegin(GL_LINES)
        glColor3f(0, 0, 0)
        for i in range(41):
            glVertex3f(-10.0 + 0.5 * i, 0, -10)
            glVertex3f(-10.0 + 0.5 * i, 0, 10)
            glVertex3f(-10.0, 0, -10 + 0.5 * i)
            glVertex3f(10.0, 0, -10 + 0.5 * i)

        # Axes
        glEnd()
        glLineWidth(5)
        green = (0.5, 0.7, 0.5)
        black = (0.0, 0.0, 0.0)

        make_lines(green, [(0.0, 0.0, 0.0), (5, 0.0, 0.0)])
        make_lines(green, [(0.0, 0.0, 0.0), (0.0, 5, 0.0)])
        make_lines(green, [(0.0, 0.0, 0.0), (0.0, 0.0, 5)])

        make_lines(black, [
            # Draw the Y.
            (0.0, 5.0, 0.0), (0.0, 5.5, 0.0), (0.0, 5.5, 0.0),
            (-0.5, 6.0, 0.0), (0.0, 5.5, 0.0), (0.5, 6.0, 0.0),

            # Draw the Z.
            (-0.5, 0.0, 5.0), (0.5, 0.0, 5.0), (0.5, 0.0, 5.0),
            (-0.5, 0.0, 6.0), (-0.5, 0.0, 6.0), (0.5, 0.0, 6.0),

            # Draw the X.
            (5.0, 0.0, 0.5), (6.0, 0.0, -0.5), (5.0, 0.0, -0.5), (6.0, 0.0, 0.5),
        ])
        glLineWidth(1)
        glEndList()

    def render(self):
        glCallList(self.id)


class ActiveMixin:
    def __init__(self):
        self.translation = np.identity(4)
        self.scaling = np.identity(4)

    def translate(self, x, y, z):
        self.translation = np.dot(self.translation, translation([x, y, z]))

    def scale(self, x, y, z):
        self.scaling = np.dot(self.scaling, scaling([x, y, z]))

    def render(self):
        glPushMatrix()
        glMultMatrixf(np.transpose(self.translation))
        glMultMatrixf(self.scaling)
        self.render_self()
        glPopMatrix()


class Primitive(Shape, ActiveMixin):
    def __init__(self, color_index=-1):
        super().__init__()
        if color_index >= 0:
            self.color_index = color_index
        else:
            self.color_index = self.random_color_index()

    def render_self(self):
        color = self.COLORS[self.color_index]
        glColor3f(color[0], color[1], color[2])
        glCallList(self.id)


class Sphere(Primitive):
    id = 2

    @classmethod
    def define(cls):
        glNewList(cls.id, GL_COMPILE)
        quad = gluNewQuadric()
        gluSphere(quad, 0.5, 30, 30)
        gluDeleteQuadric(quad)
        glEndList()


class Cube(Primitive):
    id = 3

    @classmethod
    def define(cls):
        glNewList(cls.id, GL_COMPILE)
        vertices = [((-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)),
                    ((-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5)),
                    ((0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5)),
                    ((-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)),
                    ((-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5)),
                    ((-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5))]
        normals = [(-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0),
                   (0.0, 1.0, 0.0)]

        glBegin(GL_QUADS)
        for i in range(6):
            glNormal3f(normals[i][0], normals[i][1], normals[i][2])
            for j in range(4):
                glVertex3f(vertices[i][j][0], vertices[i][j][1], vertices[i][j][2])
        glEnd()
        glEndList()


class CompositeShape(Shape, ActiveMixin):
    def __init__(self):
        super().__init__()
        self.children = []

    def render_self(self):
        for child in self.children:
            child.render()


class Snowball(CompositeShape):
    def __init__(self):
        super().__init__()
        self.add_sphere((0, -0.6, 0))
        self.add_sphere((0, 0.1, 0), (0.8, 0.8, 0.8))
        self.add_sphere((0, 0.75, 0), (0.7, 0.7, 0.7))

    def add_sphere(self, translate=None, scale=None):
        sphere = Sphere(color_index=0)
        if translate:
            sphere.translate(translate[0], translate[1], translate[2])
        if scale:
            sphere.scale(scale[0], scale[1], scale[2])
        self.children.append(sphere)


def define_shapes():
    """Create definitions for OpenGL shapes"""
    for cls_name, cls in globals().items():
        if isinstance(cls, type) and issubclass(cls, Shape):
            method = getattr(cls, 'define', None)
            if method is not None:
                method()


def translation(displacement):
    t = np.identity(4)
    t[0, 3] = displacement[0]
    t[1, 3] = displacement[1]
    t[2, 3] = displacement[2]
    return t


def scaling(scale):
    s = np.identity(4)
    s[0, 0] = scale[0]
    s[1, 1] = scale[1]
    s[2, 2] = scale[2]
    s[3, 3] = 1
    return s
