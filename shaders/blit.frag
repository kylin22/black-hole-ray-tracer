#version 330

in vec2 uv;
out vec4 fragColor;
uniform sampler2D uTexture;

void main() {
    fragColor = texture(uTexture, uv);
}
