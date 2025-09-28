#version 330

in vec2 vertexPosition;
in float inTrailAlpha;

out float vTrailAlpha;

void main() {
    gl_Position = vec4(vertexPosition, 0.0, 1.0);
    vTrailAlpha = inTrailAlpha;
}
