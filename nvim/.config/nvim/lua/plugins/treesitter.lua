return {
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    version = "*",
    config = function()
      require("nvim-treesitter.configs").setup({
        -- List of parsers to install
        ensure_installed = {
          "c",
          "cpp",
          "xml",
          "go",
          "lua",
          "bash",
          "javascript",
          "python",
          "typescript",
          "html",
          "ruby",
          "json",
          "vue",
          "rust",
          "markdown",
          "sql",
          "css",
          "yaml",
          "toml",
          "terraform",
          "gitignore",
          "markdown_inline",
        },
        sync_install = false, -- Install parsers synchronously (only applied to `ensure_installed`)
        auto_install = true, -- Automatically install missing parsers
        ignore_install = {}, -- Specify parsers to ignore installing

        highlight = {
          enable = true,                        -- Enable highlighting
          additional_vim_regex_highlighting = false, -- Disable additional Vim regex highlighting
        },
        indent = {
          enable = true, -- Enable tree-sitter based indentation
        },
        incremental_selection = {
          enable = true,
          keymaps = {
            init_selection = "<C-space>", -- Start incremental selection
            node_incremental = "<C-space>", -- Increment selection
            scope_incremental = "<C-s>",  -- Increment to the scope
            node_decremental = "<C-backspace>", -- Decrement selection
          },
        },
        autotag = {
          enable = true, -- Enable autotagging for HTML, XML, etc.
        },
        textobjects = {
          select = {
            enable = true,
            lookahead = true,      -- Automatically jump forward to textobj
            keymaps = {
              ["af"] = "@function.outer", -- Select outer function
              ["if"] = "@function.inner", -- Select inner function
              ["ac"] = "@class.outer", -- Select outer class
              ["ic"] = "@class.inner", -- Select inner class
            },
          },
        },
        context_commentstring = {
          enable = true,     -- Enable integration with 'JoosepAlviste/nvim-ts-context-commentstring'
          enable_autocmd = false, -- Disable autocmd for context commentstring
        },
        modules = {},        -- Specify any additional modules if needed
      })
    end,
  },
}

