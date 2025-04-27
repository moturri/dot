return {
	{
		"nvim-lualine/lualine.nvim",
		lazy = false, -- or true if you want it to load on event like "VeryLazy"
		dependencies = {
			"kyazdani42/nvim-web-devicons",
			"SmiteshP/nvim-navic",
			"j-hui/fidget.nvim",
		},
		config = function()
			local ok_navic, navic = pcall(require, "nvim-navic")

			require("lualine").setup({
				options = {
					icons_enabled = true,
					theme = "auto",
					component_separators = { left = "", right = "" },
					section_separators = { left = "", right = "" },
					disabled_filetypes = {
						statusline = { "NvimTree", "packer", "TelescopePrompt" },
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
						ok_navic and {
							function()
								return navic.is_available() and navic.get_location() or ""
							end,
							cond = function()
								return navic.is_available()
							end,
							color = { fg = "#61afef" },
						} or nil,
					},
					lualine_x = {
						"filetype",
						{
							"encoding",
							cond = function()
								return vim.bo.fileencoding ~= "utf-8"
							end,
						},
						"fileformat",
						{
							"python_env",
							color = { fg = "#ff8700", gui = "bold" },
							cond = function()
								return vim.bo.filetype == "python"
							end,
						},
						{
							"node_version",
							cond = function()
								return vim.fn.executable("node") == 1
							end,
							color = { fg = "#7ebf7f", gui = "italic" },
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
					lualine_a = { "buffers" },
					lualine_b = { "branch" },
					lualine_z = { "tabs" },
				},

				extensions = {
					"nvim-tree",
					"quickfix",
					"fugitive",
					"toggleterm",
				},
			})
		end,
	},
}
