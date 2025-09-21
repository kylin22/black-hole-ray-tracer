import glfw
import moderngl
import numpy as np
from pathlib import Path

c = 299792458.0
G = 6.67430e-11

# physical dimensions for the simulation in meters
physical_width = 1e11
physical_height = 7.5e10
physical_center = (0.0, 0.0)

class BlackHole:
    def __init__(self, position: tuple[float, float], mass: float):
        self.position = position
        self.radius = mass * 2 * G / c**2  # Schwarzschild radius

class Particle:
    def __init__(self, initial_position: tuple[float, float], initial_velocity: tuple[float, float], steps: int, dt: float):
        self.velocity = initial_velocity
        self.path = [initial_position] 

        position = initial_position

        for _ in range(steps):
            x, y = position
            vx, vy = self.velocity
            x += vx * dt
            y += vy * dt
            position = (x, y)
            self.path.append(position)

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
        vertex_shader=load_shader("shaders/test.vert"),
        fragment_shader=load_shader("shaders/test.frag"),
    )

    vertices = np.array([
        -1.0, -1.0,
         3.0, -1.0,
        -1.0,  3.0
    ], dtype="f4")

    vertex_buffer = context.buffer(vertices.tobytes())
    vertex_array = context.simple_vertex_array(program, vertex_buffer, "vertex")

    sagittarius_a = BlackHole(position=(0.75, 0.5), mass=8.54e36) 
    test_particle = Particle(initial_position=(-0.5 * physical_width, 0.0), initial_velocity=(c, 0.0), steps=500, dt=1)

    def physical_to_normalized(position):
        x, y = position
        normalised_x = 0.5 + (x - physical_center[0]) / physical_width
        normalised_y = 0.5 + (y - physical_center[1]) / physical_height
        return (normalised_x, normalised_y)

    particle_screen_path = [
        physical_to_normalized(point)
        for point in test_particle.path
    ]

    index = 0

    while not glfw.window_should_close(window):
        context.clear(0.0, 0.0, 0.0)
        context.viewport = (0, 0, 800, 600)

        program["u_resolution"].value = (800.0, 600.0)
        program["u_center"].value = sagittarius_a.position
        program["u_radius"].value = sagittarius_a.radius / physical_width
        program["u_particle_position"].value = particle_screen_path[index]
        program["u_particle_radius"].value = 0.01
        
        vertex_array.render(moderngl.TRIANGLES)

        glfw.swap_buffers(window)
        glfw.poll_events()

        index += 1
        if index >= len(test_particle.path):
            index = 0


    glfw.terminate()

if __name__ == "__main__":
    main()