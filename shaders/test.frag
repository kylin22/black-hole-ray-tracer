#version 330

out vec4 color;

uniform float u_radius;
uniform vec2 u_center;
uniform vec2 u_resolution;

uniform vec2 u_particle_position;
uniform float u_particle_radius;

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;

    float aspect = u_resolution.x / u_resolution.y;
    vec2 adjusted_uv = vec2((uv.x - u_center.x) * aspect, uv.y - u_center.y);

    float radius = u_radius;

    if (length(adjusted_uv) < radius) {
        color = vec4(1.0, 0.0, 0.0, 1.0);
    } else {
        color = vec4(0.0, 0.0, 0.0, 1.0);
    }

    vec2 particle_uv = vec2((uv.x - u_particle_position.x) * aspect, uv.y - u_particle_position.y);
    if (length(particle_uv) < u_particle_radius) {
        color = vec4(1.0);
        return;
    }
}