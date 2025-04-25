return {
	"nvimtools/none-ls.nvim",
	version = "*",
	config = function()
		local null_ls = require("null-ls")

		null_ls.setup({
			sources = {
				-- 🔧 Formatting
				null_ls.builtins.formatting.stylua,
				null_ls.builtins.formatting.prettier,
				null_ls.builtins.formatting.black,
				null_ls.builtins.formatting.isort,
				null_ls.builtins.formatting.clang_format,
				null_ls.builtins.formatting.shfmt,

				-- 🧪 Diagnostics
				null_ls.builtins.diagnostics.mypy,
				null_ls.builtins.diagnostics.codespell,
			},
			-- on_attach = function(client, bufnr)
			-- 		-- Optional: Autoformat on save
			-- if client.supports_method("textDocument/formatting") then
			-- 	vim.api.nvim_create_autocmd("BufWritePre", {
			-- 		buffer = bufnr,
			-- 		callback = function()
			-- 			vim.lsp.buf.format({ bufnr = bufnr, async = true })
			-- 		end,
			-- 	})
			-- end
			-- end,
		})

		-- 🗝️ Keymap for manual formatting
		vim.keymap.set("n", "<leader>gf", function()
			vim.lsp.buf.format({ async = true })
		end, { desc = "Format with LSP (null-ls)" })
	end,
}
