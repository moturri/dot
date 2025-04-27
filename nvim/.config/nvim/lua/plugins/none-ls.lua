return {
	"nvimtools/none-ls.nvim",
	version = "*",
	config = function()
		local null_ls = require("null-ls")

		null_ls.setup({
			sources = {
				null_ls.builtins.formatting.stylua,
				null_ls.builtins.formatting.prettier,
				null_ls.builtins.formatting.clang_format,
				null_ls.builtins.formatting.shfmt,
				null_ls.builtins.diagnostics.codespell,
			},
		})

		vim.keymap.set("n", "<leader>gf", vim.lsp.buf.format, { desc = "Format with LSP (null-ls)" })
	end,
}
