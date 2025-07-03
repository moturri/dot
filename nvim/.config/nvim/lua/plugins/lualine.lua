return {
	{
		"nvim-lualine/lualine.nvim",
		opts = function()
			-- Memoize node version for performance
			local cached_node_version

			local function python_env()
				local venv = vim.env.VIRTUAL_ENV
				if venv and venv ~= "" then
					return "🐍 " .. vim.fn.fnamemodify(venv, ":t")
				end
				return ""
			end

			local function node_version()
				if not vim.fn.executable("node") == 1 then
					return ""
				end
				local ft = vim.bo.filetype
				if not (ft:match("javascript") or ft:match("typescript") or ft:match("react$")) then
					return ""
				end

				if not cached_node_version then
					cached_node_version = vim.fn.system("node -v"):gsub("\n", "")
				end
				return cached_node_version
			end

			return {
				options = {
					icons_enabled = true,
					theme = "sequoia",
					component_separators = { left = "", right = "" },
					section_separators = { left = "", right = "" },
					disabled_filetypes = {
						statusline = { "NvimTree", "lazy", "TelescopePrompt", "alpha", "Outline" },
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
							symbols = { added = "󰐗 ", modified = "󰛿 ", removed = "󰍶 " },
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
							path = 1, -- relative path
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
					"nvim-tree",
					"quickfix",
					"lazy",
				},
			}
		end,
		config = function(_, opts)
			require("lualine").setup(opts)
		end,
	},
}

