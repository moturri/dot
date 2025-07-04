return {
	"stevearc/conform.nvim",
	event = { "BufReadPre", "BufNewFile" },
	config = function()
		local conform = require("conform")

		conform.setup({
			formatters_by_ft = {
				lua = { "stylua" },
				python = { "isort", "black" },
				javascript = { "prettier" },
				typescript = { "prettier" },
				c = { "clang_format" },
				cpp = { "clang_format" },
				sh = { "shfmt" },
				json = { "prettier" },
				yaml = { "prettier" },
				markdown = { "prettier" },
			},
		})

		vim.keymap.set("n", "<leader>gf", function()
			conform.format({ async = true, lsp_fallback = true })
		end, { desc = "Format buffer" })
	end,
}
