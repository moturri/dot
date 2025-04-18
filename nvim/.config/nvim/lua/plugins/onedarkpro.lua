return {
	{
		"olimorris/onedarkpro.nvim",
    version = "*",
		priority = 1000, -- Ensure it loads first
		config = function()
			vim.cmd("colorscheme onedark_dark") -- Set the colorscheme
		end,
	},
}
