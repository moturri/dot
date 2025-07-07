local function python_env()
	local venv = vim.env.VIRTUAL_ENV
	return venv and venv ~= "" and "🐍 " .. vim.fn.fnamemodify(venv, ":t") or ""
end

-- Cached Node.js version display for JS/TS files
local cached_node_version
local function node_version()
	if vim.fn.executable("node") ~= 1 then
		return ""
	end

	local ft = vim.bo.filetype
	if not ft:match("javascript") and not ft:match("typescript") and not ft:match("react$") then
		return ""
	end

	cached_node_version = cached_node_version or vim.fn.system("node -v"):gsub("\n", "")
	return cached_node_version
end

return {
	"nvim-lualine/lualine.nvim",
	enabled = true,
	event = "VeryLazy",

	opts = function()
		return {
			options = {
				icons_enabled = true,
				theme = "sequoia",
				component_separators = { left = "", right = "" },
				section_separators = { left = "", right = "" },
				disabled_filetypes = {
					statusline = { "lazy", "Outline" },
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
