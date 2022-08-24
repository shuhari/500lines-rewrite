from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from ..common.trackball import Trackball


class ObjectId:
    plane = 1
    sphere = 2
    cube = 3


def make_plane():
    def make_lines(color, points):
        glBegin(GL_LINES)
        glColor3f(color[0], color[1], color[2])
        for pt in points:
            glVertex3f(pt[0], pt[1], pt[2])
        glEnd()

    glNewList(ObjectId.plane, GL_COMPILE)
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


class GLWindow:
    def __init__(self, pos, size, title):
        self.init_opengl()
        self.create_window(pos, size, title)
        self.init_viewport()

        make_plane()
        self.trackball = Trackball(theta=-25, distance=15)

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
        # << init_view
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        aspect_ratio = float(xSize) / float(ySize)
        glViewport(0, 0, xSize, ySize)
        gluPerspective(70, aspect_ratio, 0.1, 1000.0)
        glTranslated(0, 0, -15)
        # >> init_view

        glEnable(GL_LIGHTING)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslate(0, 0, 0)
        tb_mat = self.trackball.matrix
        glMultMatrixf(tb_mat)
        glCallList(ObjectId.plane)
        glPopMatrix()
        glFlush()


def main():
    win = GLWindow((0, 0), (1024, 768), '3D Modeller')
    win.main_loop()


if __name__ == '__main__':
    main()
