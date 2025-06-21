return {
	{
		"nvim-telescope/telescope-ui-select.nvim",
	},
	{
		"nvim-telescope/telescope.nvim",
		dependencies = {
			"nvim-lua/plenary.nvim",
			"nvim-tree/nvim-web-devicons",
		},
		config = function()
			local telescope = require("telescope")
			local actions = require("telescope.actions")
			local builtin = require("telescope.builtin")

			telescope.setup({
				defaults = {
					prompt_prefix = "󰡦 ",
					selection_caret = "󰧚 ",
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
					find_files = {
						theme = "dropdown",
						previewer = false,
						hidden = true,
					},
					buffers = {
						theme = "dropdown",
						previewer = false,
						sort_lastused = true,
					},
					help_tags = { theme = "dropdown" },
					oldfiles = {
						theme = "dropdown",
						previewer = false,
					},
					search_history = {
						theme = "dropdown",
						previewer = false,
					},
				},
				extensions = {
					["ui-select"] = require("telescope.themes").get_dropdown({}),
				},
			})

			telescope.load_extension("ui-select")

			-- Core Keymaps
			local keymap = vim.keymap.set

			keymap("n", "<leader>ff", builtin.find_files, { desc = "Find Files" })
			keymap("n", "<leader>fb", builtin.buffers, { desc = "Buffers" })
			keymap("n", "<leader>fl", builtin.oldfiles, { desc = "Recent Files" })
			keymap("n", "<leader>f/", builtin.current_buffer_fuzzy_find, { desc = "Search in Current Buffer" })

			-- Reference
			keymap("n", "<leader>fh", builtin.help_tags, { desc = "Help Tags" })
			keymap("n", "<leader>fc", builtin.commands, { desc = "Commands" })
			keymap("n", "<leader>fr", builtin.registers, { desc = "Registers" })
			keymap("n", "<leader>fw", builtin.search_history, { desc = "Search History" })

			-- Git
			keymap("n", "<leader>gb", builtin.git_branches, { desc = "Git Branches" })
			keymap("n", "<leader>gc", builtin.git_commits, { desc = "Git Commits" })

			-- Dev tools
			keymap("n", "<leader>fd", builtin.diagnostics, { desc = "Diagnostics" })
			keymap("n", "<leader>fg", builtin.grep_string, { desc = "Grep Word Under Cursor" })
		end,
	},
}
