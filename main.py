import ctypes, math, numpy as np
from pathlib import Path
import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

def translation(tx: float, ty: float, tz: float = 0.0) -> np.ndarray:
    return np.array([
        [1.0, 0.0, 0.0, tx],
        [0.0, 1.0, 0.0, ty],
        [0.0, 0.0, 1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)

def rot_z(theta: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    return np.array([
        [ c, -s, 0.0, 0.0],
        [ s,  c, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)

if not glfw.init():
    raise SystemExit("Falha ao iniciar GLFW")
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)  

win = glfw.create_window(800, 600, "OpenGL 3.3 - Triângulo 2D (A/D gira, setas movem)", None, None)
if not win:
    glfw.terminate()
    raise SystemExit("OpenGL 3.3 Core requerido")
glfw.make_context_current(win)
glfw.swap_interval(1)  

def framebuffer_size_cb(window, w, h):
    glViewport(0, 0, w, h)
glfw.set_framebuffer_size_callback(win, framebuffer_size_cb)
w, h = glfw.get_framebuffer_size(win)
glViewport(0, 0, w, h)

# Shaders
base = Path(__file__).parent if "__file__" in globals() else Path.cwd()
vs_src = (base / "shaders" / "triangle.vert").read_text(encoding="utf-8")
fs_src = (base / "shaders" / "triangle.frag").read_text(encoding="utf-8")
prog = compileProgram(
    compileShader(vs_src, GL_VERTEX_SHADER),
    compileShader(fs_src, GL_FRAGMENT_SHADER)
)
glUseProgram(prog)
uModel = glGetUniformLocation(prog, "uModel")
if uModel == -1:
    print("[Aviso] uModel não encontrado (otimizado fora ou nome incorreto).")

# Geometria: xyz + rgb
vertices = np.array([
    -0.20, -0.20,  0.00,   1., 0., 0.,
     0.20, -0.20,  0.00,   0., 1., 0.,
     0.00,  0.25,  0.00,   0., 0., 1.,
], dtype=np.float32)

vao = glGenVertexArrays(1)
vbo = glGenBuffers(1)
glBindVertexArray(vao)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

stride = 6 * vertices.itemsize  # 6 floats por vértice
pos_offset = ctypes.c_void_p(0)
col_offset = ctypes.c_void_p(3 * vertices.itemsize)

glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, pos_offset)
glEnableVertexAttribArray(0)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, col_offset)
glEnableVertexAttribArray(1)

glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)

# Estado 
x_pos = y_pos = 0.0
angle = 0.0
move_speed = 0.6                # unidades/seg
rot_speed = math.radians(60.0)  # graus/seg -> rad/seg

# Margem baseada no maior alcance do triângulo
v2 = vertices.reshape(-1, 6)[:, :2]
max_extent = float(np.max(np.linalg.norm(v2, axis=1)))  # ~0.25
MARGIN = 1.0 - max_extent

def clamp(v, lo, hi): return lo if v < lo else hi if v > hi else v

glClearColor(0.1, 0.1, 0.1, 1.0)
last = glfw.get_time()

while not glfw.window_should_close(win):
    now = glfw.get_time()
    dt = float(now - last)
    last = now

    glfw.poll_events()

    # Setas: translação
    if glfw.get_key(win, glfw.KEY_LEFT)  == glfw.PRESS: x_pos -= move_speed * dt
    if glfw.get_key(win, glfw.KEY_RIGHT) == glfw.PRESS: x_pos += move_speed * dt
    if glfw.get_key(win, glfw.KEY_UP)    == glfw.PRESS: y_pos += move_speed * dt
    if glfw.get_key(win, glfw.KEY_DOWN)  == glfw.PRESS: y_pos -= move_speed * dt

    # A/D: rotação no próprio eixo (Z)
    if glfw.get_key(win, glfw.KEY_A) == glfw.PRESS: angle += rot_speed * dt
    if glfw.get_key(win, glfw.KEY_D) == glfw.PRESS: angle -= rot_speed * dt

    # Mantém dentro da tela calculando pela extensão máxima
    x_pos = clamp(x_pos, -MARGIN, MARGIN)
    y_pos = clamp(y_pos, -MARGIN, MARGIN)

    if glfw.get_key(win, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(win, True)

    glClear(GL_COLOR_BUFFER_BIT)

    # model = T * Rz  (gira no próprio centro e depois translada)
    T = translation(x_pos, y_pos, 0.0)
    Rz = rot_z(angle)
    model = T @ Rz

    glUseProgram(prog)
    glUniformMatrix4fv(uModel, 1, GL_FALSE, model.T)  # envia coluna-maior explicitamente

    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glBindVertexArray(0)

    glfw.swap_buffers(win)

glUseProgram(0)
glDeleteVertexArrays(1, [vao])
glDeleteBuffers(1, [vbo])
glDeleteProgram(prog)
glfw.terminate()