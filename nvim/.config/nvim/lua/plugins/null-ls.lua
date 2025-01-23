return {
  "nvimtools/none-ls.nvim",
  config = function()
    local null_ls = require("null-ls")

    null_ls.setup({
      sources = {
        -- Formatting
        null_ls.builtins.formatting.stylua,
        null_ls.builtins.formatting.prettier,
        null_ls.builtins.formatting.black,
        null_ls.builtins.formatting.isort,
        null_ls.builtins.formatting.clang_format, -- Added for C/C++
        null_ls.builtins.formatting.shfmt,    -- Added for Shell scripts

        -- Diagnostics
        null_ls.builtins.diagnostics.mypy,
        null_ls.builtins.diagnostics.codespell,
      },
    })

    -- Keymap for formatting
    vim.keymap.set("n", "<leader>gf", function()
      vim.lsp.buf.format({ async = true })
    end, { desc = "Format with LSP" })
  end,
}
