function style = cumcm_plot_style(fig, ax, fontName, paletteSet)
%CUMCM_PLOT_STYLE Apply one explicitly selected CUMCM paper palette.
%   STYLE = CUMCM_PLOT_STYLE(FIG, AX, FONTNAME, PALETTESET) changes
%   presentation only. PALETTESET must be SET-A, SET-B, SET-C, or SET-D.
%   FONTNAME must be an installed font verified on the current machine.

if nargin < 1 || isempty(fig)
    fig = gcf;
end
if nargin < 2 || isempty(ax)
    ax = findall(fig, "Type", "axes");
end
if nargin < 3 || isempty(fontName)
    fontName = get(groot, "FactoryAxesFontName");
end
if nargin < 4 || isempty(paletteSet)
    error("cumcm_plot_style:PaletteRequired", ...
        "palette_set is required; explicitly choose SET-A, SET-B, SET-C, or SET-D");
end

paletteSet = upper(strtrim(string(paletteSet)));
switch paletteSet
    case "SET-A"
        style.colors = [ ...
            47 107 154;  ... % primary #2F6B9A
            224 122 95;  ... % contrast #E07A5F
            61 153 112;  ... % auxiliary #3D9970
            107 114 128; ... % neutral #6B7280
            196 78 82     ... % accent #C44E52
            ] / 255;
        style.paletteBasis = "大色相间距，主色、对比色和重点色具有明显明度差";
    case "SET-B"
        style.colors = [ ...
            111 143 175; ... % primary #6F8FAF
            196 154 122; ... % contrast #C49A7A
            143 166 142; ... % auxiliary #8FA68E
            139 141 143; ... % neutral #8B8D8F
            183 123 130  ... % accent #B77B82
            ] / 255;
        style.paletteBasis = "低饱和冷暖分离，并由线型和标记补足相近灰度层级";
    case "SET-C"
        style.colors = [ ...
            76 120 168;  ... % primary #4C78A8
            242 166 90;  ... % contrast #F2A65A
            114 169 143; ... % auxiliary #72A98F
            122 127 135; ... % neutral #7A7F87
            181 101 118  ... % accent #B56576
            ] / 255;
        style.paletteBasis = "主蓝、赭橙和重点玫红具有较大的色相与明度跨度";
    case "SET-D"
        style.colors = [ ...
            91 108 143;  ... % primary #5B6C8F
            192 138 101; ... % contrast #C08A65
            120 154 159; ... % auxiliary #789A9F
            119 117 122; ... % neutral #77757A
            164 111 145  ... % accent #A46F91
            ] / 255;
        style.paletteBasis = "蓝灰、陶棕和灰紫分处不同色相区，重点色与中性灰明度可分";
    otherwise
        error("cumcm_plot_style:UnknownPalette", ...
            "Unknown palette_set %s; choose SET-A, SET-B, SET-C, or SET-D", paletteSet);
end

style.paletteSet = paletteSet;
style.light = [245 245 242] / 255;
style.sequential = interp1( ...
    linspace(0, 1, 4), ...
    [style.light; style.colors(3,:); style.colors(1,:); style.colors(4,:)], ...
    linspace(0, 1, 256));
style.diverging = interp1( ...
    linspace(0, 1, 5), ...
    [style.colors(1,:); [220 228 232] / 255; style.light; ...
     [232 218 215] / 255; style.colors(5,:)], ...
    linspace(0, 1, 256));
style.fontName = fontName;
style.lineWidth = 1.5;
style.markerSize = 5;
textColor = [79 85 90] / 255;

if exist("theme", "file") == 2
    try
        theme(fig, "light");
    catch
        % Older releases do not expose per-figure themes.
    end
end

set(fig, ...
    "Color", "w", ...
    "Renderer", "painters", ...
    "DefaultTextColor", textColor);

for k = 1:numel(ax)
    current = ax(k);
    colororder(current, style.colors);
    set(current, ...
        "FontName", fontName, ...
        "FontSize", 9, ...
        "LineWidth", 0.8, ...
        "Color", "w", ...
        "XColor", textColor, ...
        "YColor", textColor, ...
        "Box", "off", ...
        "TickDir", "out", ...
        "XGrid", "on", ...
        "YGrid", "on", ...
        "GridColor", [209 213 219] / 255, ...
        "GridAlpha", 0.65, ...
        "Layer", "top");
end

legends = findall(fig, "Type", "legend");
if ~isempty(legends)
    set(legends, ...
        "Color", "w", ...
        "TextColor", textColor, ...
        "EdgeColor", [168 155 140] / 255);
end
end
