return {
  {
    "forest-nvim/sequoia.nvim",
    version = "*",
    priority = 1000,
    config = function()
      -- Define your preferred variant here
      local variant = "sequoia-insomnia" -- or "sequoia-night"

      -- Apply colorscheme
      vim.cmd.colorscheme(variant)

      -- Set transparent backgrounds on key groups
      local transparent_groups = {
        "Normal",
        "NormalNC",
        "NormalFloat",
        "FloatBorder",
        "SignColumn",
        "VertSplit",
      }

      for _, group in ipairs(transparent_groups) do
        vim.api.nvim_set_hl(0, group, { bg = "none", ctermbg = "none" })
      end

      -- Optional: Popup menu look
      vim.api.nvim_set_hl(0, "Pmenu", { blend = 0 })
      vim.api.nvim_set_hl(0, "PmenuSel", { blend = 0 })
    end,
  },
}
