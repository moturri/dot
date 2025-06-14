local wezterm = require("wezterm")

local config = wezterm.config_builder()

--  Basic Configuration
config.term = "wezterm"
config.color_scheme = "Windows NT (base16)" -- Still used internally for some themes
config.font = wezterm.font("JetBrainsMonoNL Nerd Font", { weight = "Medium" })
config.font_size = 12.0
config.harfbuzz_features = { "kern", "liga", "clig", "calt" }

--  Performance / Rendering
config.front_end = "OpenGL" -- Use "WebGpu" for experimental WebGPU support
-- config.webgpu_power_preference = "HighPerformance" -- Uncomment for WebGPU tuning
-- config.max_fps = 120 -- Uncomment if you want to cap FPS

--  Appearance
config.window_background_opacity = 0.9
config.window_decorations = "NONE"
config.force_reverse_video_cursor = true
config.adjust_window_size_when_changing_font_size = false

--  Tabs & Panes
config.hide_tab_bar_if_only_one_tab = true
config.tab_bar_at_bottom = false
config.use_fancy_tab_bar = false
config.tab_and_split_indices_are_zero_based = true
config.window_close_confirmation = "NeverPrompt"

--  Scrollback
config.scrollback_lines = 10000

--  Cursor & Tab Color Customization
config.colors = {
  background = "#000000",
  foreground = "#FFFFFF",
  cursor_bg = "#FFFFFF",
  cursor_border = "#FFFFFF",
  cursor_fg = "#000000",
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

--  Leader Key & Keybindings
config.leader = { key = "a", mods = "ALT", timeout_milliseconds = 2000 }

config.keys = {
  -- Tabs
  { mods = "LEADER", key = "c",          action = wezterm.action.SpawnTab("CurrentPaneDomain") },
  { mods = "LEADER", key = "x",          action = wezterm.action.CloseCurrentPane({ confirm = true }) },
  { mods = "LEADER", key = "b",          action = wezterm.action.ActivateTabRelative(-1) },
  { mods = "LEADER", key = "n",          action = wezterm.action.ActivateTabRelative(1) },

  -- Splits
  { mods = "LEADER", key = "=",          action = wezterm.action.SplitHorizontal({ domain = "CurrentPaneDomain" }) },
  { mods = "LEADER", key = "-",          action = wezterm.action.SplitVertical({ domain = "CurrentPaneDomain" }) },

  -- Pane Navigation
  { mods = "LEADER", key = "h",          action = wezterm.action.ActivatePaneDirection("Left") },
  { mods = "LEADER", key = "j",          action = wezterm.action.ActivatePaneDirection("Down") },
  { mods = "LEADER", key = "k",          action = wezterm.action.ActivatePaneDirection("Up") },
  { mods = "LEADER", key = "l",          action = wezterm.action.ActivatePaneDirection("Right") },

  -- Resize Panes
  { mods = "ALT",    key = "LeftArrow",  action = wezterm.action.AdjustPaneSize({ "Left", 5 }) },
  { mods = "ALT",    key = "RightArrow", action = wezterm.action.AdjustPaneSize({ "Right", 5 }) },
  { mods = "ALT",    key = "i",          action = wezterm.action.AdjustPaneSize({ "Down", 5 }) },
  { mods = "ALT",    key = "m",          action = wezterm.action.AdjustPaneSize({ "Up", 5 }) },
}

-- Quick tab switching
for i = 0, 9 do
  table.insert(config.keys, {
    key = tostring(i),
    mods = "LEADER",
    action = wezterm.action.ActivateTab(i),
  })
end

--  Optional Features (Uncomment to Enable)

-- Launch Menu for Alternate Shells
-- config.launch_menu = {
--   { label = "Zsh", args = { "zsh", "-l" } },
--   { label = "Bash", args = { "bash", "-l" } },
-- }

-- Mouse support for selection/copy
-- config.mouse_bindings = {
--   {
--     event = { Up = { streak = 1, button = "Left" } },
--     mods = "NONE",
--     action = wezterm.action.CompleteSelection("Clipboard"),
--   },
-- }

-- Set a default workspace
-- config.default_workspace = "main"

-- Set a default working directory
-- config.default_cwd = "/home/your-user/Projects"

--  Leader Status Indicator (🐉)
wezterm.on("update-right-status", function(window, _)
  local prefix = window:leader_is_active() and " 🐉 " or ""

  window:set_left_status(wezterm.format({
    { Background = { Color = "#000000" } },
    { Text = prefix },
  }))
end)

return config
