return {
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    version = "*", -- You could specify a stable version here
    dependencies = {
      "nvim-treesitter/nvim-treesitter-textobjects",
      "windwp/nvim-ts-autotag",
      "JoosepAlviste/nvim-ts-context-commentstring",
    },
    config = function()
      require("nvim-treesitter.configs").setup({
        ensure_installed = {
          "javascript",
          "lua",
          "typescript",
          "python",           -- Limit this to what you need
        },
        sync_install = false, -- Already in place for faster startup
        highlight = {
          enable = true,
          additional_vim_regex_highlighting = false, -- Disabling regex highlighting
          disable = { "markdown", "html" },          -- Disable for unnecessary languages
        },
        indent = { enable = true },
        incremental_selection = {
          enable = false, -- Disable if not using it
        },
        autotag = { enable = true },
        textobjects = {
          select = {
            enable = false, -- Disable if not using it
          },
        },
      })

      -- Context commentstring module
      vim.g.skip_ts_context_commentstring_module = true
      require("ts_context_commentstring").setup({})
    end,
  },
}
