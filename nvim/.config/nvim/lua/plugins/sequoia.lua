return {
  {
    "forest-nvim/sequoia.nvim",
    priority = 1000,
    lazy = false,
    config = function()
      local colorscheme = "sequoia-insomnia" -- alternatives: "sequoia-night"

      -- Safely apply colorscheme
      local success, _ = pcall(vim.cmd.colorscheme, colorscheme)
      if not success then
        vim.notify("Sequoia colorscheme not found: " .. colorscheme, vim.log.levels.ERROR)
        return
      end

      local transparent_groups = {
        "Normal", "NormalNC", "NormalFloat", "FloatBorder",
        "SignColumn", "VertSplit", "StatusLine", "StatusLineNC",
        "WinBar", "WinBarNC",
      }

      for _, group in ipairs(transparent_groups) do
        vim.api.nvim_set_hl(0, group, { bg = "none", ctermbg = "none" })
      end

      vim.api.nvim_set_hl(0, "Pmenu", { blend = 0 })
      vim.api.nvim_set_hl(0, "PmenuSel", { blend = 0 })
    end,
  },
}
