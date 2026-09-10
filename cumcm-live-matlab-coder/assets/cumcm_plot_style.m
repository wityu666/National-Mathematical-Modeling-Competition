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
            65 65 109; ... % primary #41416D
            164 164 107; ... % contrast #A4A46B
            212 186 212; ... % auxiliary #D4BAD4
            129 129 129; ... % neutral #818181
            152 76 76 ... % accent #984C4C
            ] / 255;
        style.tones = [ ...
            106 106 162; ... % primary_mid #6A6AA2
            142 142 91; ... % contrast_mid #8E8E5B
            196 163 163; ... % accent_soft #C4A3A3
            235 235 239 ... % surface_tint #EBEBEF
            ] / 255;
        style.paletteBasis = "莫兰迪灰蓝与陶红；彩色核心 HLS 饱和度约 0.22–0.34，L*≈29.43–78.38，最小相邻 ΔL*=12.16";
    case "SET-B"
        style.colors = [ ...
            94 56 94; ... % primary #5E385E
            122 173 122; ... % contrast #7AAD7A
            213 188 188; ... % auxiliary #D5BCBC
            129 129 129; ... % neutral #818181
            101 101 51 ... % accent #656533
            ] / 255;
        style.tones = [ ...
            147 92 147; ... % primary_mid #935C93
            97 152 97; ... % contrast_mid #619861
            174 174 128; ... % accent_soft #AEAE80
            238 234 238 ... % surface_tint #EEEAEE
            ] / 255;
        style.paletteBasis = "莫兰迪灰紫与橄榄；彩色核心 HLS 饱和度约 0.22–0.34，L*≈29.45–78.31，最小相邻 ΔL*=12.11";
    case "SET-C"
        style.colors = [ ...
            98 59 59; ... % primary #623B3B
            117 170 170; ... % contrast #75AAAA
            196 196 161; ... % auxiliary #C4C4A1
            129 129 129; ... % neutral #818181
            56 110 56 ... % accent #386E38
            ] / 255;
        style.tones = [ ...
            153 96 96; ... % primary_mid #996060
            95 149 149; ... % contrast_mid #5F9595
            140 182 140; ... % accent_soft #8CB68C
            238 234 234 ... % surface_tint #EEEAEA
            ] / 255;
        style.paletteBasis = "莫兰迪陶土与鼠尾草；彩色核心 HLS 饱和度约 0.22–0.34，L*≈29.51–78.34，最小相邻 ΔL*=12.11";
    case "SET-D"
        style.colors = [ ...
            71 71 43; ... % primary #47472B
            158 158 195; ... % contrast #9E9EC3
            170 202 170; ... % auxiliary #AACAAA
            129 129 129; ... % neutral #818181
            54 107 107 ... % accent #366B6B
            ] / 255;
        style.tones = [ ...
            114 114 71; ... % primary_mid #727247
            136 136 179; ... % contrast_mid #8888B3
            136 179 179; ... % accent_soft #88B3B3
            235 235 230 ... % surface_tint #EBEBE6
            ] / 255;
        style.paletteBasis = "莫兰迪橄榄与灰青；彩色核心 HLS 饱和度约 0.22–0.34，L*≈29.46–78.28，最小相邻 ΔL*=12.02";
    case "SET-E"
        style.colors = [ ...
            46 77 46; ... % primary #2E4D2E
            189 148 189; ... % contrast #BD94BD
            167 200 200; ... % auxiliary #A7C8C8
            129 129 129; ... % neutral #818181
            90 90 172 ... % accent #5A5AAC
            ] / 255;
        style.tones = [ ...
            76 122 76; ... % primary_mid #4C7A4C
            171 124 171; ... % contrast_mid #AB7CAB
            169 169 200; ... % accent_soft #A9A9C8
            231 236 231 ... % surface_tint #E7ECE7
            ] / 255;
        style.paletteBasis = "莫兰迪森林灰绿与雾蓝；彩色核心 HLS 饱和度约 0.22–0.34，L*≈29.63–78.28，最小相邻 ΔL*=12.01";
    case "SET-F"
        style.colors = [ ...
            45 75 75; ... % primary #2D4B4B
            191 151 151; ... % contrast #BF9797
            192 192 215; ... % auxiliary #C0C0D7
            129 129 129; ... % neutral #818181
            143 72 143 ... % accent #8F488F
            ] / 255;
        style.tones = [ ...
            75 119 119; ... % primary_mid #4B7777
            174 128 128; ... % contrast_mid #AE8080
            195 160 195; ... % accent_soft #C3A0C3
            231 236 236 ... % surface_tint #E7ECEC
            ] / 255;
        style.paletteBasis = "莫兰迪灰青与灰玫瑰；彩色核心 HLS 饱和度约 0.22–0.34，L*≈29.66–78.35，最小相邻 ΔL*=12.04";
    otherwise
        error("cumcm_plot_style:UnknownPalette", ...
            "Unknown palette_set %s; choose SET-A through SET-F", paletteSet);
end

style.paletteSet = paletteSet;
style.paletteFamily = "MORANDI";
style.paletteRevision = "MORANDI-2026-09";
style.toneRoles = ["primary_mid", "contrast_mid", "accent_soft", "surface_tint"];
style.extendedColors = [style.colors; style.tones(1:3,:)];
style.surfaceTint = style.tones(4,:);
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
