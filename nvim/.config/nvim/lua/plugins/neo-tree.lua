return {
	{
		"nvim-neo-tree/neo-tree.nvim",
		dependencies = {
			"nvim-lua/plenary.nvim",
			"nvim-tree/nvim-web-devicons",
			"MunifTanjim/nui.nvim",
		},
		cmd = { "Neotree" },
		keys = {
			{ "<C-n>", "<cmd>Neotree reveal toggle<CR>", desc = "Toggle NeoTree" },
			{ "<leader>bf", "<cmd>Neotree buffers reveal float<CR>", desc = "NeoTree Buffers (Float)" },
			{ "<leader>fs", "<cmd>Neotree float<CR>", desc = "NeoTree Files (Float)" },
		},
		opts = {
			close_if_last_window = true,
			enable_git_status = true,
			enable_diagnostics = true,
			popup_border_style = "rounded",

			default_component_configs = {
				name = {
					trailing_slash = true,
					use_git_status_colors = true,
				},
				git_status = {
					symbols = {
						added = " ",
						modified = " ",
						deleted = " ",
						renamed = "󰁕 ",
						untracked = " ",
						ignored = " ",
					},
				},
			},

			window = {
				position = "left",
				width = 40,
				mappings = {
					["<space>"] = "none", -- prevent accidental expansion
				},
			},

			filesystem = {
				follow_current_file = {
					enabled = true,
					leave_dirs_open = false,
				},
				filtered_items = {
					visible = true,
					hide_dotfiles = false,
					hide_gitignored = false,
				},
				hijack_netrw_behavior = "open_default",
				use_libuv_file_watcher = true,
			},

			buffers = {
				follow_current_file = {
					enabled = true,
				},
				group_empty_dirs = true,
			},

			git_status = {
				window = {
					position = "float",
				},
			},
		},
	},
}
