#version 330

out vec4 color;

uniform float uRadius;
uniform vec2 uCenter;
uniform vec2 uResolution;

void main() {
    vec2 uv = gl_FragCoord.xy / uResolution.xy;

    float aspect = uResolution.x / uResolution.y;

    // black hole
    vec2 black_hole_uv = vec2((uv.x - uCenter.x) * aspect, uv.y - uCenter.y);

    if (length(black_hole_uv) < uRadius) {
        color = vec4(1.0, 0.0, 0.0, 1.0);
    } else {
        color = vec4(0.0, 0.0, 0.0, 1.0);
    }
}