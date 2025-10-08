import glfw
import moderngl
import numpy as np
from pathlib import Path
from time import time
from PIL import Image
from pyquaternion import Quaternion

# Window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

def load_shader(path: str) -> str:
    shader_path = Path(path)
    if not shader_path.exists():
        raise FileNotFoundError(f"there aint no file at: {path}")
    return shader_path.read_text(encoding="utf-8")

# small math function for splitting work in compute shaders
def ceil_div(a, b):
    return (a + b - 1) // b

def main():
    # initialise window
    if not glfw.init():
        raise Exception("GLFW could not initialize")
    

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Null Geodesics Ray Tracer", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create window")
    
    # initialise context
    glfw.make_context_current(window)
    context = moderngl.create_context()

    # load shaders
    program = context.program(
        vertex_shader=load_shader("shaders/blit.vert"),
        fragment_shader=load_shader("shaders/blit.frag"),
    )

    ray_compute = context.compute_shader(load_shader("shaders/ray.comp"))

    # fullscreen triangle setup
    fullscreen_triangle = np.array([-1.0, -1.0,   3.0, -1.0,  -1.0, 3.0], dtype="f4")
    vbo = context.buffer(fullscreen_triangle.tobytes())
    vao = context.vertex_array(program, vbo, "vertexPosition")

    # the texture for the compute shader
    compute_texture = context.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4, dtype="f4")
    compute_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

    compute_texture.bind_to_image(0, read=False, write=True)

    #load background image
    BG_IMAGE = Image.open("assets/starmap_8k.jpg").convert("RGBA")
    BG_IMAGE_width, BG_IMAGE_height = BG_IMAGE.size
    bg_transposed = BG_IMAGE.transpose(Image.FLIP_TOP_BOTTOM)
    bg_tex = context.texture((BG_IMAGE_width, BG_IMAGE_height), 4, bg_transposed.tobytes())
    bg_tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
    bg_tex.repeat_x = True
    bg_tex.repeat_y = True
    bg_tex.use(location=1)

    # compute shader uniforms
    ray_compute["uResolution"].value = (WINDOW_WIDTH, WINDOW_HEIGHT)
    ray_compute["uBackground"].value = 1

    ray_compute["uCameraPosition"].value = (0.0, 0.0, -3.0)
    ray_compute["uFOV"].value = 60.0  # degrees

    ray_compute["uSpherePosition"].value = (0.0, 0.0, 0.0)
    ray_compute["uSphereRadius"].value = 1.0

    ray_compute["uLightDir"].value = (0.577, 0.577, -0.577)  # normalized approx

    ray_compute["uAmbient"].value = 0.12

    while not glfw.window_should_close(window):
        # we run compute shader with groups of 16x16 threads
        groups_x = ceil_div(WINDOW_WIDTH, 16)
        groups_y = ceil_div(WINDOW_HEIGHT, 16)
        ray_compute.run(groups_x, groups_y, 1)

        # blit the finished texture to the display
        context.clear(0.0, 0.0, 0.0, 1.0)
        program["uTexture"].value = 0
        compute_texture.use(location=0)
        vao.render(moderngl.TRIANGLES)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
