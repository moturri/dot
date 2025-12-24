local wezterm = require("wezterm")

local config = wezterm.config_builder()

-- Font
config.font = wezterm.font_with_fallback({
	"JetBrainsMonoNL Nerd Font",
	"Symbols Nerd Font",
	"Noto Color Emoji",
}, {
	weight = "Medium",
})

config.font_size = 12.0
config.harfbuzz_features = { "kern", "liga", "clig", "calt" }

-- Window
config.window_background_opacity = 0.9
config.window_decorations = "NONE"
config.force_reverse_video_cursor = true
config.scrollback_lines = 10000
config.max_fps = 60
config.window_close_confirmation = "NeverPrompt"

-- NOTE: front_end is deprecated in newer WezTerm versions
-- config.front_end = "OpenGL"

-- Tab bar
config.hide_tab_bar_if_only_one_tab = false
config.tab_bar_at_bottom = false
config.use_fancy_tab_bar = false

-- Colors
config.colors = {
	background = "#000000",
	foreground = "#FFFFFF",
	cursor_bg = "#FFFFFF",
	cursor_border = "#FFFFFF",
	cursor_fg = "#000000",

	tab_bar = {
		background = "#000000",

		active_tab = {
			bg_color = "#bd93f9",
			fg_color = "#282a36",
			intensity = "Bold",
		},

		inactive_tab = {
			bg_color = "#000000",
			fg_color = "#6272a4",
		},

		inactive_tab_hover = {
			bg_color = "#44475a",
			fg_color = "#f8f8f2",
			italic = true,
		},

		new_tab = {
			bg_color = "#000000",
			fg_color = "#6272a4",
		},

		new_tab_hover = {
			bg_color = "#000000",
			fg_color = "#282a36",
		},
	},
}

-- Leader key
config.leader = {
	key = "a",
	mods = "ALT",
	timeout_milliseconds = 2000,
}

-- Key bindings
config.keys = {
	{ mods = "LEADER", key = "c", action = wezterm.action.SpawnTab("CurrentPaneDomain") },
	{ mods = "LEADER", key = "x", action = wezterm.action.CloseCurrentPane({ confirm = true }) },
	{ mods = "LEADER", key = "b", action = wezterm.action.ActivateTabRelative(-1) },
	{ mods = "LEADER", key = "n", action = wezterm.action.ActivateTabRelative(1) },

	{ mods = "LEADER", key = "=", action = wezterm.action.SplitHorizontal({ domain = "CurrentPaneDomain" }) },
	{ mods = "LEADER", key = "-", action = wezterm.action.SplitVertical({ domain = "CurrentPaneDomain" }) },

	{ mods = "LEADER", key = "h", action = wezterm.action.ActivatePaneDirection("Left") },
	{ mods = "LEADER", key = "j", action = wezterm.action.ActivatePaneDirection("Down") },
	{ mods = "LEADER", key = "k", action = wezterm.action.ActivatePaneDirection("Up") },
	{ mods = "LEADER", key = "l", action = wezterm.action.ActivatePaneDirection("Right") },

	{ mods = "ALT", key = "LeftArrow", action = wezterm.action.AdjustPaneSize({ "Left", 5 }) },
	{ mods = "ALT", key = "RightArrow", action = wezterm.action.AdjustPaneSize({ "Right", 5 }) },
	{ mods = "ALT", key = "i", action = wezterm.action.AdjustPaneSize({ "Down", 5 }) },
	{ mods = "ALT", key = "m", action = wezterm.action.AdjustPaneSize({ "Up", 5 }) },
}

-- Leader + number = tab switch
for i = 0, 9 do
	table.insert(config.keys, {
		key = tostring(i),
		mods = "LEADER",
		action = wezterm.action.ActivateTab(i),
	})
end

-- Fancy tab title
wezterm.on("format-tab-title", function(tab)
	local title = tab.active_pane.title or ""
	local is_active = tab.is_active

	if #title > 20 then
		title = title:sub(1, 17) .. "..."
	end

	local left_sep = ""
	local right_sep = ""
	local bg = is_active and "#bd93f9" or "#000000"
	local fg = is_active and "#282a36" or "#6272a4"

	return {
		{ Background = { Color = "#000000" } },
		{ Foreground = { Color = bg } },
		{ Text = left_sep },
		{ Background = { Color = bg } },
		{ Foreground = { Color = fg } },
		{ Text = " " .. title .. " " },
		{ Background = { Color = "#000000" } },
		{ Foreground = { Color = bg } },
		{ Text = right_sep },
	}
end)

-- Right status (leader indicator)
wezterm.on("update-right-status", function(window)
	local leader_active = window:leader_is_active()
	local left_sep = ""
	local right_sep = ""

	local bg = leader_active and "#d45498" or "#bd93f9"
	local fg = "#282a36"
	local text = leader_active and "" or ""

	window:set_right_status(wezterm.format({
		{ Background = { Color = "#000000" } },
		{ Foreground = { Color = bg } },
		{ Text = left_sep },
		{ Background = { Color = bg } },
		{ Foreground = { Color = fg } },
		{ Text = " " .. text .. " " },
		{ Background = { Color = "#000000" } },
		{ Foreground = { Color = bg } },
		{ Text = right_sep },
	}))
end)

return config
