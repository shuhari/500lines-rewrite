from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from . import shapes
from .scene import Scene


class GLWindow:
    def __init__(self, pos, size, title):
        self.init_opengl()
        self.create_window(pos, size, title)
        self.init_viewport()

        self.scene = Scene()
        self.scene.add_samle_shapes()

    def init_opengl(self):
        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)

    def create_window(self, pos, size, title):
        glutInitWindowPosition(pos[0], pos[1])
        glutInitWindowSize(size[0], size[1])
        glutCreateWindow(title.encode())
        glutDisplayFunc(self.render)
        glutIdleFunc(self.render)

    def main_loop(self):
        glutMainLoop()

    def init_viewport(self):
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(0, 0, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, GLfloat_3(0, 0, -1))

        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.4, 0.4, 0.4, 0.0)

    def render(self):
        self.scene.render()


def main():
    win = GLWindow((0, 0), (1024, 768), '3D Modeller')
    win.main_loop()


if __name__ == '__main__':
    main()
