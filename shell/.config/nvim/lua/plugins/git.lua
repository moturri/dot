---@diagnostic disable: undefined-global

return {
	-- Git integration (manual command usage)
	{
		"tpope/vim-fugitive",
		cmd = { "Git", "G" },
	},

	-- Git signs and inline diff indicators
	{
		"lewis6991/gitsigns.nvim",
		event = { "BufReadPre", "BufNewFile" },
		opts = {
			signs = {
				add = { text = " " },
				change = { text = " " },
				delete = { text = " " },
				topdelete = { text = " " },
				changedelete = { text = "󰐕 " },
				untracked = { text = " " },
			},
			signcolumn = true,
			numhl = false,
			linehl = false,
			word_diff = false,

			attach_to_untracked = true,
			max_file_length = 40000,
			update_debounce = 100,

			current_line_blame = false,
			current_line_blame_opts = {
				virt_text = true,
				virt_text_pos = "eol",
				delay = 500,
				ignore_whitespace = true,
			},
			current_line_blame_formatter = "<author>, <author_time:%R> - <summary>",

			preview_config = {
				border = "rounded",
				style = "minimal",
				relative = "cursor",
				row = 0,
				col = 1,
			},
		},
		config = function(_, opts)
			local ok, gitsigns = pcall(require, "gitsigns")
			if ok then
				gitsigns.setup(opts)
			else
				vim.notify("Failed to load gitsigns.nvim", vim.log.levels.ERROR)
			end
		end,
	},
}
