return {
	{
		"nvim-telescope/telescope.nvim",
		dependencies = {
			"nvim-lua/plenary.nvim",
			"nvim-tree/nvim-web-devicons",
			"nvim-telescope/telescope-ui-select.nvim",
		},
		cmd = "Telescope",
		keys = {
			{
				"<leader>tf",
				function()
					require("telescope.builtin").find_files()
				end,
				desc = "Find Files",
			},
			{
				"<leader>tb",
				function()
					require("telescope.builtin").buffers()
				end,
				desc = "Buffers",
			},
			{
				"<leader>to",
				function()
					require("telescope.builtin").oldfiles()
				end,
				desc = "Recent Files",
			},
			{
				"<leader>t/",
				function()
					require("telescope.builtin").current_buffer_fuzzy_find()
				end,
				desc = "Search in Current Buffer",
			},
			{
				"<leader>th",
				function()
					require("telescope.builtin").help_tags()
				end,
				desc = "Help Tags",
			},
			{
				"<leader>tc",
				function()
					require("telescope.builtin").commands()
				end,
				desc = "Commands",
			},
			{
				"<leader>tr",
				function()
					require("telescope.builtin").registers()
				end,
				desc = "Registers (Yank + Macros)",
			},
			{
				"<leader>tw",
				function()
					require("telescope.builtin").search_history()
				end,
				desc = "Search History",
			},
			{
				"<leader>tg",
				function()
					require("telescope.builtin").grep_string()
				end,
				desc = "Grep Word Under Cursor",
			},
			{
				"<leader>tB",
				function()
					require("telescope.builtin").git_branches()
				end,
				desc = "Git Branches",
			},
			{
				"<leader>tC",
				function()
					require("telescope.builtin").git_commits()
				end,
				desc = "Git Commits",
			},
			{
				"<leader>td",
				function()
					require("telescope.builtin").diagnostics()
				end,
				desc = "Diagnostics",
			},
		},
		config = function()
			local telescope = require("telescope")
			local actions = require("telescope.actions")

			telescope.setup({
				defaults = {
					prompt_prefix = "󰡦 ",
					selection_caret = " ",
					entry_prefix = "  ",
					initial_mode = "insert",
					sorting_strategy = "ascending",
					layout_strategy = "horizontal",
					layout_config = {
						horizontal = {
							prompt_position = "top",
							width = 0.8,
							height = 0.8,
							preview_width = 0.5,
						},
					},
					path_display = { "truncate" },
					file_ignore_patterns = {
						"node_modules",
						"%.git/",
						"%.cache",
						"venv",
						"target",
						"%.class",
						"%.o",
						"%.out",
					},
					mappings = {
						i = {
							["<C-n>"] = actions.move_selection_next,
							["<C-p>"] = actions.move_selection_previous,
							["<C-c>"] = actions.close,
							["<C-u>"] = actions.preview_scrolling_up,
							["<C-d>"] = actions.preview_scrolling_down,
							["<C-q>"] = actions.send_to_qflist,
						},
						n = {
							["<C-c>"] = actions.close,
							["<C-j>"] = actions.move_selection_next,
							["<C-k>"] = actions.move_selection_previous,
						},
					},
				},
				pickers = {
					find_files = { theme = "dropdown", previewer = true, hidden = true },
					buffers = { theme = "dropdown", previewer = true, sort_lastused = true },
					help_tags = { theme = "dropdown" },
					oldfiles = { theme = "dropdown", previewer = true },
					search_history = { theme = "dropdown", previewer = true },
				},
				extensions = {
					["ui-select"] = require("telescope.themes").get_dropdown({}),
				},
			})

			telescope.load_extension("ui-select")
		end,
	},
}
