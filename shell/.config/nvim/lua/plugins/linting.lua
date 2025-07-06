return {
	"mfussenegger/nvim-lint",
	config = function()
		local lint = require("lint")

		lint.linters_by_ft = {
			sh = { "shellcheck" },
			python = { "flake8" },
			markdown = { "markdownlint" },
		}

		-- Create an autocmd group to prevent duplicate autocmds
		local lint_augroup = vim.api.nvim_create_augroup("lint", { clear = true })

		vim.api.nvim_create_autocmd({ "BufEnter", "BufWritePost", "InsertLeave" }, {
			group = lint_augroup,
			callback = function(args)
				-- Only run nvim-lint if there's no active LSP that provides diagnostics.
				local has_lsp_diagnostics = false
				for _, client in ipairs(vim.lsp.get_clients({ bufnr = args.buf })) do
					if client.supports_method("textDocument/publishDiagnostics") then
						has_lsp_diagnostics = true
						break
					end
				end

				if not has_lsp_diagnostics then
					lint.try_lint()
				end
			end,
		})

		vim.keymap.set("n", "<leader>ge", vim.diagnostic.open_float, { desc = "Show line diagnostics" })
		vim.keymap.set("n", "<leader>gl", function()
			lint.try_lint()
		end, { desc = "Manually lint current buffer" })
	end,
}
