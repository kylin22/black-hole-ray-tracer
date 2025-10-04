import glfw
import moderngl
import numpy as np
from pathlib import Path

LIGHT_SPEED = 299792458.0
GRAVITATIONAL_CONSTANT = 6.67430e-11

# physical dimensions for the simulation in meters
PHYSICAL_WIDTH = 2e11
PHYSICAL_HEIGHT = 1.5e11
PHYSICAL_CENTER = (0.0, 0.0)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

def physical_to_normalised(physical_position: tuple[float, float]) -> tuple[float, float]:
    x, y = physical_position
    normalised_x = (x - PHYSICAL_CENTER[0]) / (PHYSICAL_WIDTH / 2)
    normalised_y = (y - PHYSICAL_CENTER[1]) / (PHYSICAL_HEIGHT / 2)
    return normalised_x, normalised_y

class BlackHole:
    def __init__(self, position: tuple[float, float], mass: float):
        self.position = position
        self.radius = mass * 2 * GRAVITATIONAL_CONSTANT / (LIGHT_SPEED ** 2) # Schwarzschild radius

class Ray:
    def __init__(self, initial_position: tuple[float, float], initial_velocity: tuple[float, float], max_age: int):
        self.position = initial_position
        self.velocity = initial_velocity
        self.age = 0
        self.max_age = max_age
        self.alive = True
      
    def check_collision(self, black_hole: BlackHole) -> bool:
        x, y = self.position
        bh_x, bh_y = black_hole.position
        distance = np.hypot(x - bh_x, y - bh_y)
        return distance <= black_hole.radius

    def step(self, black_hole: BlackHole, dt: float):
        if self.alive:
            x, y = self.position
            vx, vy = self.velocity
            self.position = (x + vx * dt, y + vy * dt)
            
            if self.check_collision(black_hole):
                self.alive = False
                self.age = 0
        else:
            self.age += 1
            if self.age > self.max_age:
                self.age = self.max_age

    def get_trail_data(self) -> tuple[float, float]:
        return physical_to_normalised(self.position)

def load_shader(path: str) -> str:
    shader_path = Path(path)
    if not shader_path.exists():
        raise FileNotFoundError(f"there aint no file at: {path}")
    return shader_path.read_text()

def main():
    # initialise window
    if not glfw.init():
        raise Exception("GLFW could not initialize")

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Unfinished Test Black Hole Sim", None, None)
    if not window:
        glfw.terminate()
        return

    # initialise context
    glfw.make_context_current(window)
    context = moderngl.create_context()

    # setup shader programs
    main_program = context.program(
        vertex_shader=load_shader("shaders/main.vert"),
        fragment_shader=load_shader("shaders/main.frag"),
    )

    fullscreen_triangle = np.array([
        -1.0, -1.0,
         3.0, -1.0,
        -1.0,  3.0
    ], dtype="f4")

    main_buffer = context.buffer(fullscreen_triangle.tobytes())
    main_array = context.vertex_array(main_program, main_buffer, "vertexPosition")

    photon_program = context.program(
        vertex_shader=load_shader("shaders/photon.vert"),
        fragment_shader=load_shader("shaders/photon.frag"),
    )

    # create photons along left edge
    PHOTON_NUMBER = 100
    MAX_AGE = 500
    y_positions = np.linspace(-0.5 * PHYSICAL_HEIGHT, 0.5 * PHYSICAL_HEIGHT, PHOTON_NUMBER)
    x_initial = -0.5 * PHYSICAL_WIDTH
    photons = []
    for y in y_positions:
        photons.append(Ray(
            initial_position=(x_initial, y),
            initial_velocity=(LIGHT_SPEED, 0.0),
            max_age=MAX_AGE
        ))

    
    photon_buffer = context.buffer(reserve=PHOTON_NUMBER * 2 * 4)
    photon_array = context.vertex_array(photon_program, photon_buffer, "vertexPosition" )

    # ping pong framebuffers for trail fading

    accumulation_texture_1 = context.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4)
    accumulation_texture_2 = context.texture((WINDOW_WIDTH, WINDOW_HEIGHT), 4)
    accumulation_texture_1.filter = (moderngl.LINEAR, moderngl.LINEAR)
    accumulation_texture_2.filter = (moderngl.LINEAR, moderngl.LINEAR)
    framebuffer_1 = context.framebuffer(color_attachments=[accumulation_texture_1])
    framebuffer_2 = context.framebuffer(color_attachments=[accumulation_texture_2])

    # remove initial accumulation texture contents
    framebuffer_1.use()
    context.clear(0.0, 0.0, 0.0)

    # load trail shaders
    fade_program = context.program(
        vertex_shader=load_shader("shaders/fade.vert"),
        fragment_shader=load_shader("shaders/fade.frag"),
    )
    fade_array = context.vertex_array(fade_program, main_buffer, "vertexPosition")

    blit_program = context.program(
        vertex_shader=load_shader("shaders/fade.vert"),
        fragment_shader=load_shader("shaders/blit.frag"),
    )
    blit_array = context.vertex_array(blit_program, main_buffer, "vertexPosition")


    # create black hole
    sagittarius_a = BlackHole(position=(0.25 * PHYSICAL_WIDTH, 0.0 * PHYSICAL_HEIGHT), mass=8.54e36) 

    ping = True
    while not glfw.window_should_close(window):
        context.clear(0.0, 0.0, 0.0)
        context.enable(moderngl.BLEND)
        context.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
        context.viewport = (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

        if ping:
            previous_trail_texture = accumulation_texture_1
            current_trail_buffer = framebuffer_2
        else:
            previous_trail_texture = accumulation_texture_2
            current_trail_buffer = framebuffer_1
        ping = not ping

        # fade previous trails
        current_trail_buffer.use()
        context.disable(moderngl.BLEND)
        previous_trail_texture.use(location=0)
        fade_program["previousTexture"].value = 0
        fade_program["decay"].value = 0.95
        fade_array.render(moderngl.TRIANGLES)

        # render black hole

        main_program["uResolution"].value = (WINDOW_WIDTH, WINDOW_HEIGHT)
        main_program["uCenter"].value = physical_to_normalised(sagittarius_a.position)
        main_program["uRadius"].value = sagittarius_a.radius / (PHYSICAL_HEIGHT / 2)  # normalised radius
        main_array.render(moderngl.TRIANGLES)

        # render current photons

        trail_data = np.zeros((PHOTON_NUMBER, 2), dtype='f4')
        for i, photon in enumerate(photons):
            photon.step(sagittarius_a, 0.5)
            x, y = photon.get_trail_data()
            trail_data[i] = [x, y]

        photon_buffer.write(trail_data.tobytes())
        photon_array.render(mode=moderngl.POINTS, vertices=PHOTON_NUMBER)

        # blit to screen
        context.screen.use()
        context.disable(moderngl.BLEND)
        current_trail_buffer.color_attachments[0].use(location=0)
        blit_program['previousTexture'].value = 0
        blit_array.render(moderngl.TRIANGLES)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()