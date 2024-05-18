/*
 * Vibrance
 *
 * Enhance color saturation.
 * Also supports per-channel multipliers.
 *
 * Source: https://github.com/hyprwm/Hyprland/issues/1140#issuecomment-1614863627
 */

precision highp float;
varying vec2 v_texcoord;
uniform sampler2D tex;

// see https://github.com/CeeJayDK/SweetFX/blob/a792aee788c6203385a858ebdea82a77f81c67f0/Shaders/Vibrance.fx#L20-L30

/**
 * Per-channel multiplier to vibrance strength.
 *
 * @min 0.0
 * @max 10.0
 */
const vec3 Balance = vec3(
    float({{#nc}}{{balance.red}} ? 1.0{{/nc}}),
    float({{#nc}}{{balance.green}} ? 1.0{{/nc}}),
    float({{#nc}}{{balance.blue}} ? 1.0{{/nc}})
);

/**
 * Strength of filter.
 * (Negative values will reduce vibrance.)
 *
 * @min -1.0
 * @max 1.0
 */
const float Strength = float({{#nc}}{{strength}} ? 0.15{{/nc}});

const vec3 VIB_coeffVibrance = Balance * -Strength;

void main() {
    vec4 pixColor = texture2D(tex, v_texcoord);
    vec3 color = vec3(pixColor[0], pixColor[1], pixColor[2]);

    // vec3 VIB_coefLuma = vec3(0.333333, 0.333334, 0.333333); // was for `if VIB_LUMA == 1`
    vec3 VIB_coefLuma = vec3(0.212656, 0.715158, 0.072186); // try both and see which one looks nicer.

    float luma = dot(VIB_coefLuma, color);

    float max_color = max(color[0], max(color[1], color[2]));
    float min_color = min(color[0], min(color[1], color[2]));

    float color_saturation = max_color - min_color;

    vec3 p_col = vec3(vec3(vec3(vec3(sign(VIB_coeffVibrance) * color_saturation) - 1.0) * VIB_coeffVibrance) + 1.0);

    pixColor[0] = mix(luma, color[0], p_col[0]);
    pixColor[1] = mix(luma, color[1], p_col[1]);
    pixColor[2] = mix(luma, color[2], p_col[2]);

    gl_FragColor = pixColor;
}

// vim: ft=glsl
