/*
 * Color Filter
 *
 * Adjust colors for color vision deficiencies.
 * Supports protanopia (red-green), deuteranopia (green-red), and tritanopia (blue-yellow).
 *
 * Source: https://godotshaders.com/shader/colorblindness-correction-shader/
 */

precision highp float;
varying vec2 v_texcoord;
uniform sampler2D tex;

/**
 * Strength of filter.
 *
 * @min 0.0
 * @max 1.0
 */
const float Strength = float({{#nc}}{{strength}} ? 0.2{{/nc}});

// Enum for color correction type
const int PROTANOPIA = 0;
const int PROTAN = PROTANOPIA;
const int REDGREEN = PROTANOPIA;
const int DEUTERANOPIA = 1;
const int DEUTAN = DEUTERANOPIA;
const int GREENRED = DEUTERANOPIA;
const int TRITANOPIA = 2;
const int TRITAN = TRITANOPIA;
const int BLUEYELLOW = TRITANOPIA;

/**
 * Type of color correction.
 */
const int Type = {{#nc}}{{type}} ? PROTANOPIA{{/nc}};

void main() {
    vec4 pixColor = texture2D(tex, v_texcoord);

    float L = (17.8824 * pixColor.r) + (43.5161 * pixColor.g) + (4.11935 * pixColor.b);
    float M = (3.45565 * pixColor.r) + (27.1554 * pixColor.g) + (3.86714 * pixColor.b);
    float S = (0.0299566 * pixColor.r) + (0.184309 * pixColor.g) + (1.46709 * pixColor.b);

    float l, m, s;
    if (Type == PROTANOPIA) {
        l = 0.0 * L + 2.02344 * M + -2.52581 * S;
        m = 0.0 * L + 1.0 * M + 0.0 * S;
        s = 0.0 * L + 0.0 * M + 1.0 * S;
    } else if (Type == DEUTERANOPIA) {
        l = 1.0 * L + 0.0 * M + 0.0 * S;
        m = 0.494207 * L + 0.0 * M + 1.24827 * S;
        s = 0.0 * L + 0.0 * M + 1.0 * S;
    } else if (Type == TRITANOPIA) {
        l = 1.0 * L + 0.0 * M + 0.0 * S;
        m = 0.0 * L + 1.0 * M + 0.0 * S;
        s = -0.395913 * L + 0.801109 * M + 0.0 * S;
    }

    vec4 error;
    error.r = (0.0809444479 * l) + (-0.130504409 * m) + (0.116721066 * s);
    error.g = (-0.0102485335 * l) + (0.0540193266 * m) + (-0.113614708 * s);
    error.b = (-0.000365296938 * l) + (-0.00412161469 * m) + (0.693511405 * s);
    error.a = 1.0;
    vec4 diff = pixColor - error;
    vec4 correction;
    correction.r = 0.0;
    correction.g = (diff.r * 0.7) + (diff.g * 1.0);
    correction.b = (diff.r * 0.7) + (diff.b * 1.0);
    correction = mix(pixColor, pixColor + correction, Strength);

    gl_FragColor = vec4(correction);
}

// vim: ft=glsl
