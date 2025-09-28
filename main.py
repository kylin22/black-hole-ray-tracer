import glfw
import moderngl
import numpy as np
from pathlib import Path

LIGHT_SPEED = 299792458.0
GRAVITATIONAL_CONSTANT = 6.67430e-11

# physical dimensions for the simulation in meters
PHYSICAL_WIDTH = 1e11
PHYSICAL_HEIGHT = 7.5e10
PHYSICAL_CENTER = (0.0, 0.0)

class BlackHole:
    def __init__(self, position: tuple[float, float], mass: float):
        self.position = position
        self.radius = mass * 2 * GRAVITATIONAL_CONSTANT / (LIGHT_SPEED ** 2) # Schwarzschild radius

class Ray:
    def __init__(self, initial_position: tuple[float, float], initial_velocity: tuple[float, float], max_trail: int):
        self.position = initial_position
        self.velocity = initial_velocity
        self.trail = [initial_position] 

        # preallocate trail variables
        self.max_trail = max_trail
        self.trail = np.zeros((max_trail, 2), dtype='f4')  # preallocate
        self.trail_alpha = np.linspace(0, 1, max_trail, dtype='f4')
        self.trail_index = 0
        self.trail_full = False
        self.trail[self.trail_index] = initial_position

    def physical_to_normalized(self, physical_position: tuple[float, float]):
        x, y = physical_position
        normalised_x = (x - PHYSICAL_CENTER[0]) / PHYSICAL_WIDTH
        normalised_y = (y - PHYSICAL_CENTER[1]) / PHYSICAL_HEIGHT
        return (normalised_x, normalised_y)

    def step(self, dt: float):
        # update position
        x, y = self.position
        vx, vy = self.velocity
        x += vx * dt
        y += vy * dt
        self.position = (x, y)

        # update trail in circular buffer
        normalised_position = self.physical_to_normalized(self.position)
        self.trail_index = (self.trail_index + 1) % self.max_trail
        self.trail[self.trail_index] = normalised_position
        if self.trail_index == 0:
            self.trail_full = True

    def get_trail_data(self):
        if self.trail_full:
            # return oldest to newest
            return np.vstack((self.trail[self.trail_index + 1:], self.trail[:self.trail_index + 1]))
        else:
            # only return filled part
            return self.trail[:self.trail_index + 1]

def load_shader(path: str) -> str:
    shader_path = Path(path)
    if not shader_path.exists():
        raise FileNotFoundError(f"there aint no file at: {path}")
    return shader_path.read_text()

def main():
    # initialise window
    if not glfw.init():
        raise Exception("GLFW could not initialize")

    window = glfw.create_window(800, 600, "Black Hole Ray Tracer", None, None)
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

    vertices = np.array([
        -1.0, -1.0,
         3.0, -1.0,
        -1.0,  3.0
    ], dtype="f4")

    vertex_buffer = context.buffer(vertices.tobytes())
    vertex_array = context.vertex_array(main_program, vertex_buffer, "vertexPosition")

    trail_program = context.program(
        vertex_shader=load_shader("shaders/trail.vert"),
        fragment_shader=load_shader("shaders/trail.frag"),
    )

    # create photons along left edge
    PHOTON_NUMBER = 100
    MAX_TRAIL = 800
    y_positions = np.linspace(-1.0 * PHYSICAL_HEIGHT, 1.0 * PHYSICAL_HEIGHT, PHOTON_NUMBER)
    x_initial = -1.0 * PHYSICAL_WIDTH
    photons = []
    for y in y_positions:
        photons.append(Ray(
            initial_position=(x_initial, y),
            initial_velocity=(LIGHT_SPEED, 0.0),
            max_trail=MAX_TRAIL
        ))

    trail_buffer = context.buffer(reserve = PHOTON_NUMBER * MAX_TRAIL * 3 * 4)  # max_trail * (2 coordinates + 1 alpha) * 4 bytes per float
    trail_array = context.vertex_array(trail_program, trail_buffer, "vertexPosition", "inTrailAlpha")

    # create black hole
    sagittarius_a = BlackHole(position=(0.75, 0.5), mass=8.54e36) 

    while not glfw.window_should_close(window):
        context.clear(0.0, 0.0, 0.0)
        context.enable(moderngl.BLEND)
        context.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
        context.viewport = (0, 0, 800, 600)

        main_program["uResolution"].value = (800.0, 600.0)
        main_program["uCenter"].value = sagittarius_a.position
        main_program["uRadius"].value = sagittarius_a.radius / PHYSICAL_WIDTH

        vertex_array.render(moderngl.TRIANGLES)
        
        # update photons and photon trails once
        buffer_data = []
        for photon in photons:
            photon.step(0.5)
            positions = photon.get_trail_data()
            alphas = np.linspace(0.0, 1.0, len(positions), dtype='f4')[:, None]
            buffer_data = np.hstack([positions, alphas]).astype('f4').tobytes()
            trail_buffer.write(buffer_data)
            trail_array.render(moderngl.LINE_STRIP, vertices=len(positions))

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()