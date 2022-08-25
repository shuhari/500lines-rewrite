from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from . import shapes
from .scene import Scene


class GLWindow:
    def __init__(self, pos, size, title):
        self.mouse_btn = None
        self.mouse_pos = None

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

        glutMouseFunc(self.handle_mouse_button)
        glutMotionFunc(self.handle_mouse_move)
        glutKeyboardFunc(self.handle_keystroke)
        glutSpecialFunc(self.handle_keystroke)

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

    def normalize_pos(self, x, y):
        width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        return x, height - y

    def handle_mouse_button(self, btn, mode, x, y):
        # print('mouse button:', btn, mode, x, y)
        self.mouse_pos = self.normalize_pos(x, y)
        if mode == GLUT_DOWN:
            self.mouse_btn = btn
            if btn == 3:  # scroll up
                self.scene.translate(0, 0, 1.0)
            elif btn == 4:  # scroll down
                self.scene.translate(0, 0, -1.0)
        else:  # mouse button up
            self.mouse_btn = None
        glutPostRedisplay()

    def handle_mouse_move(self, x, y):
        # print('mouse move:', x, y)
        curr_pos = self.normalize_pos(x, y)
        changed = False
        if self.mouse_btn is not None:
            dx = curr_pos[0] - self.mouse_pos[0]
            dy = curr_pos[1] - self.mouse_pos[1]
            if self.mouse_btn == GLUT_RIGHT_BUTTON:
                self.scene.drag(curr_pos, (dx, dy))
            elif self.mouse_btn == GLUT_MIDDLE_BUTTON:
                self.scene.translate(dx / 60.0, dy / 60.0, 0)
                changed = True
        self.mouse_pos = curr_pos
        if changed:
            glutPostRedisplay()

    def handle_keystroke(self, key, x, y):
        # print('key stroke:', key, x, y)
        pass


def main():
    win = GLWindow((0, 0), (1024, 768), '3D Modeller')
    win.main_loop()


if __name__ == '__main__':
    main()
