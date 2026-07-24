function style = cumcm_plot_style(fig, ax, fontName)
%CUMCM_PLOT_STYLE Apply a restrained paper style to figure axes.
%   STYLE = CUMCM_PLOT_STYLE(FIG, AX, FONTNAME) changes presentation only.
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

style.colors = [ ...
     47 107 154; ... % blue
    224 122  95; ... % orange
     61 153 112; ... % green
    107 114 128; ... % gray
    196  78  82  ... % red
    ] / 255;
style.light = [243 244 246] / 255;
style.fontName = fontName;
style.lineWidth = 1.5;
style.markerSize = 5;
textColor = [55 65 81] / 255;

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
        "EdgeColor", [156 163 175] / 255);
end
end
