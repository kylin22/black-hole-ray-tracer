#version 330

uniform sampler2D previousTexture;
in vec2 uv;
out vec4 color;

void main() {
    color = texture(previousTexture, uv);
}