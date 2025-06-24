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

		local root_dir
		local ok_utils, utils = pcall(require, "null-ls.utils")
		if ok_utils then
			root_dir = utils.root_pattern(".git", "pyproject.toml")
		end

		null_ls.setup({
			root_dir = root_dir,
			sources = {
				-- Formatters
				formatting.stylua,
				formatting.isort,
				formatting.prettier,
				formatting.clang_format,
				formatting.shfmt,

				-- Diagnostics
				diagnostics.codespell,
			},
		})

		-- Format buffer using LSP (none-ls or others)
		vim.keymap.set("n", "<leader>gf", function()
			local clients = vim.lsp.get_clients({ bufnr = 0 })
			if #clients == 0 then
				vim.notify("No LSP client available for formatting", vim.log.levels.WARN)
				return
			end
			vim.lsp.buf.format({ async = true })
		end, { desc = "Format buffer with LSP (none-ls)" })
	end,
}
