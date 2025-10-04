#version 330

in vec2 vertexPosition;
out vec2 uv;

void main() {
    gl_Position = vec4(vertexPosition, 0.0, 1.0);
    uv = vertexPosition * 0.5 + 0.5;
}
