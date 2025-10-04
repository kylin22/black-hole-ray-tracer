#version 330

out vec4 color;

uniform float uRadius;
uniform vec2 uCenter;
uniform vec2 uResolution;

void main() {
    vec2 ndc = 2.0 * gl_FragCoord.xy / uResolution - 1.0;

    float aspectRatio = uResolution.x / uResolution.y;
    vec2 centerOffset = vec2((ndc.x - uCenter.x) * aspectRatio, ndc.y - uCenter.y);

    if (length(centerOffset) < uRadius) {
        color = vec4(1.0, 0.0, 0.0, 1.0);
    } else {
        color = vec4(0.0, 0.0, 0.0, 1.0);
    }
}