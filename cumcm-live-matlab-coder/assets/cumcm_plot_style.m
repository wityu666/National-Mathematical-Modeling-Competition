function style = cumcm_plot_style(fig, ax, fontName, paletteSet)
%CUMCM_PLOT_STYLE Apply one explicitly selected CUMCM paper palette.
%   STYLE = CUMCM_PLOT_STYLE(FIG, AX, FONTNAME, PALETTESET) changes
%   presentation only. PALETTESET must be SET-A through SET-F.
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
        "palette_set is required; explicitly choose SET-A through SET-F");
end

paletteSet = upper(strtrim(string(paletteSet)));
switch paletteSet
    case "SET-A"
        style.colors = [ ...
            59 59 144;   ... % primary #3B3B90
            165 165 74;  ... % contrast #A5A54A
            217 183 217; ... % auxiliary #D9B7D9
            129 129 129; ... % neutral #818181
            184 46 46     ... % accent #B82E2E
            ] / 255;
        style.paletteBasis = "深蓝主色—红色重点—金黄对比—淡紫辅助；六组同角色色相距均≥60°，CIELAB L*≈29.59–78.24，相邻最小 ΔL*=12.09";
    case "SET-B"
        style.colors = [ ...
            108 44 108;  ... % primary #6C2C6C
            89 180 89;   ... % contrast #59B459
            218 186 186; ... % auxiliary #DABABA
            129 129 129; ... % neutral #818181
            102 102 25    ... % accent #666619
            ] / 255;
        style.paletteBasis = "深茄紫主色—橄榄重点—绿色对比—淡红辅助；六组同角色色相距均≥60°，CIELAB L*≈29.59–78.21，相邻最小 ΔL*=12.08";
    case "SET-C"
        style.colors = [ ...
            116 48 48;   ... % primary #743030
            79 175 175;  ... % contrast #4FAFAF
            197 197 146; ... % auxiliary #C5C592
            129 129 129; ... % neutral #818181
            28 114 28     ... % accent #1C721C
            ] / 255;
        style.paletteBasis = "深红棕主色—绿色重点—青色对比—淡黄辅助；六组同角色色相距均≥60°，CIELAB L*≈29.51–78.39，相邻最小 ΔL*=12.10";
    case "SET-D"
        style.colors = [ ...
            71 71 29;    ... % primary #47471D
            156 156 211; ... % contrast #9C9CD3
            161 205 161; ... % auxiliary #A1CDA1
            129 129 129; ... % neutral #818181
            27 109 109    ... % accent #1B6D6D
            ] / 255;
        style.paletteBasis = "深橄榄主色—青色重点—蓝色对比—淡绿辅助；六组同角色色相距均≥60°，CIELAB L*≈29.25–78.35，相邻最小 ΔL*=12.18";
    case "SET-E"
        style.colors = [ ...
            32 79 32;    ... % primary #204F20
            203 139 203; ... % contrast #CB8BCB
            157 202 202; ... % auxiliary #9DCACA
            129 129 129; ... % neutral #818181
            81 81 212     ... % accent #5151D4
            ] / 255;
        style.paletteBasis = "深森林绿主色—蓝色重点—品红对比—淡青辅助；六组同角色色相距均≥60°，CIELAB L*≈29.42–78.27，相邻最小 ΔL*=12.14";
    case "SET-F"
        style.colors = [ ...
            31 77 77;    ... % primary #1F4D4D
            206 145 145; ... % contrast #CE9191
            191 191 221; ... % auxiliary #BFBFDD
            129 129 129; ... % neutral #818181
            166 41 166    ... % accent #A629A6
            ] / 255;
        style.paletteBasis = "深青主色—品红重点—红色对比—淡蓝辅助；六组同角色色相距均≥60°，CIELAB L*≈29.75–78.20，相邻最小 ΔL*=12.06";
    otherwise
        error("cumcm_plot_style:UnknownPalette", ...
            "Unknown palette_set %s; choose SET-A through SET-F", paletteSet);
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
        "EdgeColor", [209 213 219] / 255);
end
end
