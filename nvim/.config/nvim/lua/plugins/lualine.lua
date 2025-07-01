return {
	{
		"nvim-lualine/lualine.nvim",
		lazy = true,
		event = "BufReadPost",
		dependencies = {
			"j-hui/fidget.nvim",
		},
		opts = function()
			local progress_util
			local has_fidget, fidget = pcall(require, "fidget")
			if has_fidget then
				fidget.setup({})
				local ok, progress = pcall(require, "fidget.progress")
				if ok then
					progress_util = progress
				end
			end

			local has_node = vim.fn.executable("node") == 1
			local cached_node_version = nil

			local function fidget_status()
				if progress_util then
					local msg = progress_util.get_progress_message()
					return msg and msg.title or ""
				end
				return ""
			end

			local function python_env()
				if vim.bo.filetype == "python" and vim.env.VIRTUAL_ENV then
					return "🐍 " .. vim.env.VIRTUAL_ENV:match("^.+/(.+)$")
				end
				return ""
			end

			local function node_version()
				local ft = vim.bo.filetype
				if has_node and ft:match("javascript") or ft:match("typescript") or ft:match("react$") then
					if not cached_node_version then
						local handle = io.popen("node -v 2>/dev/null")
						if handle then
							local version = handle:read("*a")
							handle:close()
							cached_node_version = version and version:gsub("\n", "") or ""
						end
					end
					return cached_node_version
				end
				return ""
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
							path = 1,
							symbols = {
								modified = " 󰐗",
								readonly = " ",
								unnamed = "[No Name]",
							},
						},
						fidget_status,
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
