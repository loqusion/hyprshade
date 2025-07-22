/*
 * Grayscale
 */

#version 300 es
precision highp float;

in vec2 v_texcoord;
uniform sampler2D tex;
out vec4 fragColor;

// Enum for type of grayscale conversion
const int LUMINOSITY = 0;
const int LIGHTNESS = 1;
const int AVERAGE = 2;

/**
 * Type of grayscale conversion.
 */
const int Type = {{#nc}}{{type}} ? LUMINOSITY{{/nc}};

// Enum for selecting luma coefficients
const int PAL = 0;
const int HDTV = 1;
const int HDR = 2;

/**
 * Formula used to calculate relative luminance.
 * (Only applies when type = "luminosity".)
 */
const int LuminosityType = {{#nc}}{{luminosity_type}} ? HDR{{/nc}};

void main() {
    vec4 pixColor = texture(tex, v_texcoord);
    float gray = 0.0;

    if (Type == LUMINOSITY) {
        // https://en.wikipedia.org/wiki/Grayscale#Luma_coding_in_video_systems
        if (LuminosityType == PAL) {
            gray = dot(pixColor.rgb, vec3(0.299, 0.587, 0.114));
        } else if (LuminosityType == HDTV) {
            gray = dot(pixColor.rgb, vec3(0.2126, 0.7152, 0.0722));
        } else if (LuminosityType == HDR) {
            gray = dot(pixColor.rgb, vec3(0.2627, 0.6780, 0.0593));
        }
    } else if (Type == LIGHTNESS) {
        float maxColor = max(pixColor.r, max(pixColor.g, pixColor.b));
        float minColor = min(pixColor.r, min(pixColor.g, pixColor.b));
        gray = (maxColor + minColor) / 2.0;
    } else if (Type == AVERAGE) {
        gray = (pixColor.r + pixColor.g + pixColor.b) / 3.0;
    }

    fragColor = vec4(vec3(gray), pixColor.a);
}

// vim: ft=glsl
