return {
	{
		"stevearc/oil.nvim",
		version = "*",
		config = function()
			local oil = require("oil")

			oil.setup({
				-- Optional configuration settings
				columns = {
					"icon",
					"size",
					"mtime",
				},
				view_options = {
					show_hidden = true,
				},
				float = {
					border = "rounded",
					max_width = 0.8,
					max_height = 0.8,
				},
			})

			-- Key mapping to toggle the file explorer
			vim.keymap.set("n", "-", oil.toggle_float, { desc = "Toggle Oil file explorer" })
		end,
	},
}
