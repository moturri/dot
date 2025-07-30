return {
	-- Git wrapper (no keymaps, use :Git manually)
	{
		"tpope/vim-fugitive",
		cmd = { "Git", "G" },
	},

	-- Git diff and blame signs in the gutter
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

			preview_config = {
				border = "rounded",
				style = "minimal",
				relative = "cursor",
				row = 0,
				col = 1,
			},
		},
	},
}
