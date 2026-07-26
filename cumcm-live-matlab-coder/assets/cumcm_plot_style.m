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
            32 73 104;   ... % primary #204968
            228 137 113; ... % contrast #E48971
            138 208 177; ... % auxiliary #8AD0B1
            122 129 144; ... % neutral #7A8190
            191 34 40     ... % accent #BF2228
            ] / 255;
        style.paletteBasis = "深海蓝—暖珊瑚—薄荷绿与强调红；CIELAB L*≈29.6–78.3，相邻最小 ΔL*=12.07";
    case "SET-B"
        style.colors = [ ...
            51 72 92;    ... % primary #33485C
            195 153 120; ... % contrast #C39978
            183 198 183; ... % auxiliary #B7C6B7
            127 129 132; ... % neutral #7F8184
            162 68 79     ... % accent #A2444F
            ] / 255;
        style.paletteBasis = "低饱和蓝灰—陶土棕—鼠尾草绿与灰豆沙红；CIELAB L*≈29.7–78.4，相邻最小 ΔL*=12.07";
    case "SET-C"
        style.colors = [ ...
            45 72 100;   ... % primary #2D4864
            238 135 33;  ... % contrast #EE8721
            167 202 185; ... % auxiliary #A7CAB9
            125 129 137; ... % neutral #7D8189
            197 13 52     ... % accent #C50D34
            ] / 255;
        style.paletteBasis = "清晰蓝—赭橙—柔绿与饱和玫红；CIELAB L*≈29.7–78.4，相邻最小 ΔL*=12.03";
    case "SET-D"
        style.colors = [ ...
            59 70 92;    ... % primary #3B465C
            199 151 118; ... % contrast #C79776
            178 198 200; ... % auxiliary #B2C6C8
            131 128 134; ... % neutral #838086
            160 62 125    ... % accent #A03E7D
            ] / 255;
        style.paletteBasis = "蓝紫灰—陶棕—青灰与梅紫；CIELAB L*≈29.6–78.5，相邻最小 ΔL*=12.17";
    otherwise
        error("cumcm_plot_style:UnknownPalette", ...
            "Unknown palette_set %s; choose SET-A, SET-B, SET-C, or SET-D", paletteSet);
end

style.paletteSet = paletteSet;
style.light = [245 245 242] / 255;
style.sequential = interp1( ...
    linspace(0, 1, 6), ...
    [style.light; style.colors(3,:); style.colors(2,:); ...
     style.colors(4,:); style.colors(5,:); style.colors(1,:)], ...
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
