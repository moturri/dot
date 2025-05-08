return {
	{
		-- "forest-nvim/sequoia.nvim",
		-- "liminalminds/icecream-neovim",
		"olimorris/onedarkpro.nvim",
		version = "*",
		priority = 1000,
		config = function()
			vim.cmd("colorscheme onedark_dark")
			-- vim.cmd("colorscheme sequoia-insomnia") -- (night, insomnia)
			-- vim.cmd("colorscheme icecream")
		end,
	},
}
