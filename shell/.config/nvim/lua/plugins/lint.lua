---@diagnostic disable: undefined-global

return {
	"mfussenegger/nvim-lint",
	event = { "BufReadPre", "BufNewFile" },
	config = function()
		local lint = require("lint")

		lint.linters_by_ft = {
			sh = { "shellcheck" },
			javascript = { "eslint_d" },
			json = { "jsonlint" },
		}

		vim.keymap.set("n", "<leader>be", vim.diagnostic.open_float, { desc = "Show line diagnostics" })
		vim.keymap.set("n", "<leader>bL", function()
			lint.try_lint()
		end, { desc = "Lint current buffer" })
	end,
}
