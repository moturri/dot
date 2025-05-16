return {
  {
    "forest-nvim/sequoia.nvim",
    -- "liminalminds/icecream-neovim",
    -- "olimorris/onedarkpro.nvim",
    version = "*",
    priority = 1000,
    config = function()
      -- vim.cmd("colorscheme onedark_dark")
      vim.cmd("colorscheme sequoia-insomnia") -- (night, insomnia)
      -- vim.cmd("colorscheme icecream")

      -- Enable transparency
      vim.api.nvim_set_hl(0, "Normal", { bg = "none" })
      vim.api.nvim_set_hl(0, "NormalNC", { bg = "none" })
      vim.api.nvim_set_hl(0, "NormalFloat", { bg = "none" })
      vim.api.nvim_set_hl(0, "FloatBorder", { bg = "none" })
      vim.api.nvim_set_hl(0, "SignColumn", { bg = "none" })
      vim.api.nvim_set_hl(0, "VertSplit", { bg = "none" })
    end,
  },
}
