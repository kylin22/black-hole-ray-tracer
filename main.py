import glfw
import moderngl
import numpy as np
from pathlib import Path

def load_shader(path: str) -> str:
    shader_path = Path(path)
    if not shader_path.exists():
        raise FileNotFoundError(f"Shader file not found: {path}")
    return shader_path.read_text()


def main():
    if not glfw.init():
        raise Exception("GLFW could not initialize.")

    window = glfw.create_window(800, 600, "Black Hole Ray Tracer", None, None)
    if not window:
        glfw.terminate()
        return
    
    # initialise context
    glfw.make_context_current(window)
    context = moderngl.create_context()

    # compile
    program = context.program(
        vertex_shader=load_shader("render/shaders/test.vert"),
        fragment_shader=load_shader("render/shaders/test.frag"),
    )

    vertices = np.array([
        -1.0, -1.0,
         3.0, -1.0,
        -1.0,  3.0
    ], dtype="f4")

    vertex_buffer = context.buffer(vertices.tobytes())
    vertex_array = context.simple_vertex_array(program, vertex_buffer, "vertex")

    # render loop
    while not glfw.window_should_close(window):
        context.clear(0.0, 0.0, 0.0)
        context.viewport = (0, 0, 800, 600)
        program['u_resolution'].value = (800.0, 600.0)
        
        vertex_array.render(moderngl.TRIANGLES)

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()

if __name__ == "__main__":
    main()