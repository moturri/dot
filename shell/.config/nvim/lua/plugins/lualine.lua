return {
	"nvim-lualine/lualine.nvim",
	enabled = true,
	event = "BufEnter",

	opts = function()
		return {
			options = {
				icons_enabled = true,
				theme = "sequoia",
				component_separators = { left = "", right = "" },
				section_separators = { left = "", right = "" },
				disabled_filetypes = {
					statusline = { "lazy", "Outline", "mason" },
				},
				always_divide_middle = true,
				globalstatus = true,
			},

			sections = {
				lualine_a = { { "mode", icon = "" } },
				lualine_b = {
					{ "branch", icon = "" },
					{
						"diff",
						symbols = {
							added = "󰐗 ",
							modified = "󰛿 ",
							removed = "󰍶 ",
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
							modified = " 󰐗",
							readonly = " ",
							unnamed = "[No Name]",
						},
					},
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
					python_env,
					node_version,
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
							return math.floor(vim.o.columns * 0.7)
						end,
						filetype_names = {
							NvimTree = "File Explorer",
							fugitive = "Git",
							toggleterm = "Terminal",
						},
						show_filename_only = true,
						symbols = {
							modified = " 󰐗",
							readonly = " ",
						},
					},
				},
				lualine_b = { "branch" },
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
				"quickfix",
				"lazy",
			},
		}
	end,

	config = function(_, opts)
		require("lualine").setup(opts)
	end,
}
