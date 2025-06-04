return {
  "nvimtools/none-ls.nvim",
  event = { "BufReadPre", "BufNewFile" },
  config = function()
    local ok, null_ls = pcall(require, "null-ls")
    if not ok then
      vim.notify("none-ls failed to load", vim.log.levels.ERROR)
      return
    end

    local formatting = null_ls.builtins.formatting
    local diagnostics = null_ls.builtins.diagnostics

    null_ls.setup({
      sources = {
        -- Formatters
        formatting.isort,        -- Python
        formatting.prettier,     -- JS, TS, HTML, CSS, JSON, etc.
        formatting.clang_format, -- C/C++/Java
        formatting.shfmt,        -- Shell scripts

        -- Diagnostics
        diagnostics.codespell, -- Spell checking
      },
      root_dir = require("null-ls.utils").root_pattern(".git", "pyproject.toml"),
    })

    -- Format current buffer via none-ls
    vim.keymap.set("n", "<leader>gf", function()
      vim.lsp.buf.format({ async = true })
    end, { desc = "Format file with LSP (none-ls)" })
  end,
}
