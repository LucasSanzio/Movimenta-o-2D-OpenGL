# Triângulo 2D (OpenGL 3.3 Core) — A/D gira, setas movem

## Requisitos
- Python 3.10+
- Pip packages: `glfw`, `PyOpenGL`, `numpy`

```bash
pip install -r requirements.txt
```

## Executar
```bash
python main.py
```

> Obs.: Execute a partir da pasta do projeto (onde está `main.py`) para que o caminho relativo de `shaders/` funcione.

## Controles
- **A / D**: girar no próprio eixo (Z)
- **← / → / ↑ / ↓**: mover na tela
- **ESC**: sair

## Estrutura
```
opengl_triangle_2d/
├─ main.py
├─ requirements.txt
└─ shaders/
   ├─ triangle.vert
   └─ triangle.frag
```

## Notas técnicas
- GLSL **330 core** com `layout(location=0/1)`.
- `uModel` é uma `mat4`; a matriz é enviada como **coluna-maior** (`transpose = GL_FALSE` + `model.T`).
- `glfw.swap_interval(1)` habilita VSync para evitar uso alto de CPU.
- `framebuffer_size_callback` atualiza `glViewport` em resize.
- A margem de movimento (`MARGIN`) é calculada pelo maior raio do triângulo para mantê-lo **inteiro** visível.
```