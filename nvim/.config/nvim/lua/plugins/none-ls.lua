return {
  "nvimtools/none-ls.nvim",
  version = "*",
  config = function()
    local null_ls = require("null-ls")

    -- Define formatting + diagnostic sources
    local sources = {
      -- Formatting tools
      -- null_ls.builtins.formatting.stylua,       -- Lua
      null_ls.builtins.formatting.isort,        -- Python import sorter
      null_ls.builtins.formatting.prettier,     -- JS, TS, CSS, JSON, etc.
      null_ls.builtins.formatting.clang_format, -- C/C++/Java
      null_ls.builtins.formatting.shfmt,        -- Shell scripts

      -- Diagnostics tools
      null_ls.builtins.diagnostics.codespell, -- Spell checking
    }

    null_ls.setup({
      sources = sources,
      -- You can add on_attach here if you want buffer-specific setups later
      -- on_attach = function(client, bufnr)
      --   -- e.g., custom keymaps or capabilities per buffer
      -- end,
    })

    -- Global keymap for formatting
    vim.keymap.set("n", "<leader>gf", function()
      vim.lsp.buf.format({ async = true })
    end, { desc = "Format with LSP (null-ls)" })
  end,
}
