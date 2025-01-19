local wezterm = require("wezterm")

local config = wezterm.config_builder()

config.term = "wezterm"
config.color_scheme = "Windows NT (base16)"
config.font = wezterm.font("JetBrains Mono NL Medium")
config.harfbuzz_features = { "kern", "liga", "clig", "calt" }
config.font_size = 12.0
config.unicode_version = 14

config.enable_kitty_graphics = true
config.front_end = "OpenGL"
config.force_reverse_video_cursor = true
config.window_background_opacity = 0.9
config.max_fps = 120

config.hide_tab_bar_if_only_one_tab = true
config.tab_bar_at_bottom = true
config.use_fancy_tab_bar = false
config.window_decorations = "NONE"
config.tab_and_split_indices_are_zero_based = true
config.window_close_confirmation = "NeverPrompt"

config.leader = { key = "a", mods = "ALT", timeout_milliseconds = 2000 }
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

for i = 0, 9 do
	table.insert(config.keys, { key = tostring(i), mods = "LEADER", action = wezterm.action.ActivateTab(i) })
end

config.colors = {
	background = "#000000",
	foreground = "#FFFFFF",
	cursor_bg = "#FFFFFF",
	cursor_border = "#FFFFFF",
	cursor_fg = "#000000",
}

config.colors = {
	tab_bar = {
		background = "#000000",
		active_tab = {
			bg_color = "#000000",
			fg_color = "#d86304",
		},
		inactive_tab = {
			bg_color = "#000000",
			fg_color = "#A0A0A0",
		},
		new_tab = {
			bg_color = "#000000",
			fg_color = "#A0A0A0",
		},
		inactive_tab_edge = "#000000",
	},
}

wezterm.on("update-right-status", function(window, _)
	local prefix = window:leader_is_active() and " \u{1F409} " or ""

	window:set_left_status(wezterm.format({
		{ Background = { Color = "#000000" } },
		{ Text = prefix },
	}))
end)

return config
