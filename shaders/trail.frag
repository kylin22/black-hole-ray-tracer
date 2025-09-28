#version 330

in float vTrailAlpha;
out vec4 color;

void main() {
    color = vec4(1.0, 1.0, 1.0, vTrailAlpha);
}