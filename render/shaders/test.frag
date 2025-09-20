#version 330
out vec4 color;

uniform vec2 u_resolution;

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec2 center = vec2(0.5, 0.5);

    float aspect = u_resolution.x / u_resolution.y;
    vec2 adjusted_uv = vec2((uv.x - center.x) * aspect, uv.y - center.y);
    float distance = length(adjusted_uv);

    float radius = 0.25;

    if (distance < radius) {
        color = vec4(1.0, 0.0, 0.0, 1.0);
    } else {
        color = vec4(0.0, 0.0, 0.0, 1.0);
    }
}