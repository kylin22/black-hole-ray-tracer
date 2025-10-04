#version 330

uniform sampler2D previousTexture;
uniform float decay;
in vec2 uv;
out vec4 color;

void main() {
    vec4 previousTrail = texture(previousTexture, uv);
    color = previousTrail * decay;
}