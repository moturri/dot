return {
	{
		"nvim-lualine/lualine.nvim",
		lazy = false,
		dependencies = {
			"kyazdani42/nvim-web-devicons",
			"j-hui/fidget.nvim",
		},
		config = function()
			require("lualine").setup({
				options = {
					icons_enabled = true,
					theme = "auto",
					component_separators = { left = "", right = "" },
					section_separators = { left = "", right = "" },
					disabled_filetypes = {
						statusline = { "NvimTree", "lazy", "TelescopePrompt" },
						winbar = {},
					},
					always_divide_middle = true,
					globalstatus = true,
				},

				sections = {
					lualine_a = {
						{ "mode", icon = "" },
					},
					lualine_b = {
						{ "branch", icon = "" },
						{
							"diff",
							symbols = {
								added = " ",
								modified = " ",
								removed = " ",
								renamed = "󰁕 ",
								untracked = " ",
								ignored = " ",
								unstaged = "󰄱 ",
								staged = " ",
								conflict = " ",
							},
							colored = true,
						},
						{
							"diagnostics",
							sources = { "nvim_lsp" },
							symbols = {
								error = " ",
								warn = " ",
								info = " ",
								hint = " ",
							},
						},
					},
					lualine_c = {
						{
							"filename",
							file_status = true,
							path = 1,
							symbols = {
								modified = " [+]",
								readonly = " ",
								unnamed = "[No Name]",
							},
						},
					},
					lualine_x = {
						{ "filetype", colored = true, icon_only = false },
						{
							"encoding",
							cond = function()
								return vim.bo.fileencoding ~= "utf-8"
							end,
						},
						"fileformat",
						{
							"python_env",
							cond = function()
								return vim.bo.filetype == "python"
							end,
						},
						{
							"node_version",
							cond = function()
								return vim.fn.executable("node") == 1
									and vim.tbl_contains({
										"javascript",
										"typescript",
										"javascriptreact",
										"typescriptreact",
									}, vim.bo.filetype)
							end,
						},
					},
					lualine_y = { "progress" },
					lualine_z = { "location" },
				},

				inactive_sections = {
					lualine_c = { "filename" },
					lualine_x = { "location" },
				},

				tabline = {
					lualine_a = {
						{
							"buffers",
							max_length = function()
								return vim.o.columns * 0.7
							end,
							filetype_names = {
								NvimTree = "File Explorer",
								fugitive = "Git",
								toggleterm = "Terminal",
							},
						},
					},
					lualine_b = { "branch" },
					lualine_c = {},
					lualine_x = {},
					lualine_y = {},
					lualine_z = {
						{
							"tabs",
							cond = function()
								return #vim.api.nvim_list_tabpages() > 1
							end,
						},
					},
				},

				extensions = {
					"nvim-tree",
					"quickfix",
					"lazy",
				},
			})
		end,
	},
}
