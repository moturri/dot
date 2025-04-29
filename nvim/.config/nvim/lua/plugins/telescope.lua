return {
	-- UI Select extension
	{
		"nvim-telescope/telescope-ui-select.nvim",
	},

	-- Main Telescope plugin
	{
		"nvim-telescope/telescope.nvim",
		version = "*",
		dependencies = { "nvim-lua/plenary.nvim" },
		opts = function()
			local actions = require("telescope.actions")
			local themes = require("telescope.themes")

			return {
				defaults = {
					prompt_prefix = "󰱼 ",
					selection_caret = "➜ ",
					entry_prefix = "  ",
					initial_mode = "insert",
					sorting_strategy = "ascending",
					layout_strategy = "flex",
					layout_config = {
						horizontal = { prompt_position = "top" },
						vertical = { prompt_position = "top" },
						flex = { flip_columns = 150 },
					},
					mappings = {
						i = {
							["<C-n>"] = actions.move_selection_next,
							["<C-p>"] = actions.move_selection_previous,
							["<C-c>"] = actions.close,
							["<C-u>"] = actions.preview_scrolling_up,
							["<C-d>"] = actions.preview_scrolling_down,
						},
						n = {
							["<C-c>"] = actions.close,
							["<C-j>"] = actions.move_selection_next,
							["<C-k>"] = actions.move_selection_previous,
						},
					},
				},
				extensions = {
					["ui-select"] = themes.get_dropdown({}),
				},
			}
		end,
		config = function(_, opts)
			local telescope = require("telescope")
			telescope.setup(opts)
			telescope.load_extension("ui-select")
		end,
		keys = {
			{
				"<leader>ff",
				function()
					require("telescope.builtin").find_files()
				end,
				desc = "Find Files",
			},
			{
				"<leader>fh",
				function()
					require("telescope.builtin").help_tags()
				end,
				desc = "Help Tags",
			},
			{
				"<leader>fc",
				function()
					require("telescope.builtin").commands()
				end,
				desc = "Commands",
			},
			{
				"<leader>fm",
				function()
					require("telescope.builtin").man_pages()
				end,
				desc = "Man Pages",
			},
			{
				"<leader>fr",
				function()
					require("telescope.builtin").registers()
				end,
				desc = "Registers",
			},
			{
				"<leader>fs",
				function()
					require("telescope.builtin").search_history()
				end,
				desc = "Search History",
			},
			{
				"<leader>f/",
				function()
					require("telescope.builtin").current_buffer_fuzzy_find()
				end,
				desc = "Fuzzy Find in Current Buffer",
			},
		},
	},
}
