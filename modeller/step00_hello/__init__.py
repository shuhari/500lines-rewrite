from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


def render_func():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glRotate(0.1, 5, 5, 0)
    glutWireTeapot(0.5)
    glFlush()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowPosition(0, 0)
    glutInitWindowSize(400, 400)
    glutCreateWindow(b'OpenGL')
    glutDisplayFunc(render_func)
    glutIdleFunc(render_func)
    glutMainLoop()


if __name__ == '__main__':
    main()
