---@diagnostic disable: undefined-global

return {
	"folke/snacks.nvim",
	priority = 1000,
	lazy = false,
	dependencies = {
		"folke/which-key.nvim",
		"echasnovski/mini.icons",
		"nvim-tree/nvim-web-devicons",
	},

	opts = {
		bigfile = {
			enabled = true,
			notify = true,
			size = 1.5 * 1024 * 1024,
			line_length = 1000,
			setup = function(ctx)
				if vim.fn.exists(":NoMatchParen") ~= 0 then
					vim.cmd([[NoMatchParen]])
				end
				Snacks.util.wo(0, { foldmethod = "manual", statuscolumn = "", conceallevel = 0 })
				vim.b.minianimate_disable = true
				vim.schedule(function()
					if vim.api.nvim_buf_is_valid(ctx.buf) then
						vim.bo[ctx.buf].syntax = ctx.ft
					end
				end)
			end,
		},
		dashboard = {
			enabled = true,
			preset = {
				header = [[
         	                                             
         	      ████ ██████           █████      ██
         	     ███████████             █████ 
         	     █████████ ███████████████████ ███   ███████████
         	    █████████  ███    █████████████ █████ ██████████████
         	   █████████ ██████████ █████████ █████ █████ ████ █████
         	 ███████████ ███    ███ █████████ █████ █████ ████ █████
         	██████  █████████████████████ ████ █████ █████ ████ ██████
      	]],
			},
			sections = {
				-- { section = "header" },
				{ section = "terminal", cmd = "fortune -s | lolcat", hl = "header", padding = 2, indent = 2 },
				{ section = "keys", padding = 1, indent = 2 },
				{
					pane = 2,
					icon = " ",
					title = "Recent Files",
					section = "recent_files",
					padding = 1,
					indent = 2,
				},
				{ pane = 2, icon = " ", title = "Projects", section = "projects", padding = 1, indent = 2 },
				{
					pane = 2,
					icon = " ",
					title = "Git Status",
					section = "terminal",
					enabled = function()
						return Snacks.git.get_root() ~= nil
					end,
					cmd = "git status --short --branch --renames",
					height = 5,
					padding = 1,
					indent = 2,
					ttl = 5 * 60,
				},
				{ section = "startup" },
			},
		},
		explorer = {
			enabled = true,
			finder = "explorer",
			sort = { fields = { "sort" } },
			tree = true,
			supports_live = true,
			follow_file = true,
			focus = "list",
			auto_close = false,
			jump = { close = false },
			layout = { preset = "sidebar", preview = false },
			formatters = { files = { filename_only = true } },
			matcher = { sort_empty = true },
			config = function(opts)
				return require("snacks.picker.source.explorer").setup(opts)
			end,
		},
		indent = {
			enabled = true,
		},
		input = { enabled = true },
		statuscolumn = {
			enabled = true,
			left = { "mark", "sign" },
			right = { "fold", "git" },
			folds = {
				open = false,
				git_hl = false,
			},
			git = {
				patterns = { "GitSign", "MiniDiffSign" },
			},
			refresh = 50,
		},
		notifier = {
			enabled = true,
			timeout = 5000,
		},
		picker = {
			enabled = true,
			tree = true,
			hidden = true,
			follow_file = true,
		},
		quickfile = {
			enabled = true,
		},
		scope = {
			enabled = true,
		},
		scroll = { enabled = true },
		words = { enabled = true },
		image = { enabled = true },
		styles = {
			notification = {
				wo = { wrap = true },
			},
		},
	},

	keys = (function()
		local function map(lhs, rhs, desc, extra)
			local opts = vim.tbl_extend("force", extra or {}, {
				desc = desc,
				[1] = lhs,
				[2] = rhs,
			})
			return opts
		end

		return {
			-- Pickers
			map("<leader><space>", function()
				Snacks.picker.smart()
			end, "Smart Find Files"),
			map("<leader>bb", function()
				Snacks.picker.buffers()
			end, "Buffers"),
			map("<leader>/", function()
				Snacks.picker.grep()
			end, "Grep"),
			map("<leader>:", function()
				Snacks.picker.command_history()
			end, "Command History"),
			map("<leader>e", function()
				Snacks.explorer()
			end, "File Explorer"),

			-- Find
			map("<leader>ff", function()
				Snacks.picker.files()
			end, "Find Files"),
			map("<leader>s/", function()
				Snacks.picker.search_history()
			end, "Search History"),
			map("<leader>sa", function()
				Snacks.picker.autocmds()
			end, "Autocmds"),
			map("<leader>fc", function()
				Snacks.picker.files({ cwd = vim.fn.stdpath("config") })
			end, "Find Config File"),
			map("<leader>fg", function()
				Snacks.picker.git_files()
			end, "Find Git Files"),
			map("<leader>fp", function()
				Snacks.picker.projects()
			end, "Projects"),
			map("<leader>fr", function()
				Snacks.picker.recent()
			end, "Recent Files"),
			map("<leader>fo", function()
				local vault = vim.fn.expand("/mnt/dm-2/Library/Obsidian")
				Snacks.picker.files({
					cwd = vault,
				})
			end, "Open Obsidian vault"),

			-- Git
			map("<leader>gs", function()
				Snacks.picker.git_status()
			end, "Git Status"),
			map("<leader>gl", function()
				Snacks.picker.git_log()
			end, "Git Log"),
			map("<leader>gg", function()
				Snacks.lazygit()
			end, "Lazygit"),
			map("<leader>gb", function()
				Snacks.picker.git_branches()
			end, "Git Branches"),
			map("<leader>gL", function()
				Snacks.picker.git_log_line()
			end, "Git Log Line"),
			map("<leader>gS", function()
				Snacks.picker.git_stash()
			end, "Git Stash"),
			map("<leader>gd", function()
				Snacks.picker.git_diff()
			end, "Git Diff (Hunks)"),
			map("<leader>gf", function()
				Snacks.picker.git_log_file()
			end, "Git Log File"),
			map("<leader>gB", function()
				Snacks.gitbrowse()
			end, "Git Browse", { mode = { "n", "v" } }),

			-- Diagnostics
			map("<leader>sd", function()
				Snacks.picker.diagnostics()
			end, "Workspace Diagnostics"),
			map("<leader>bD", function()
				Snacks.picker.diagnostics_buffer()
			end, "Buffer Diagnostics"),

			-- LSP
			map("ld", function()
				Snacks.picker.lsp_definitions()
			end, "Goto Definition"),
			map("lD", function()
				Snacks.picker.lsp_declarations()
			end, "Goto Declaration"),
			map("lr", function()
				Snacks.picker.lsp_references()
			end, "LSP References", { nowait = true }),
			map("ly", function()
				Snacks.picker.lsp_type_definitions()
			end, "Type Definition"),
			map("lI", function()
				Snacks.picker.lsp_implementations()
			end, "Goto Implementation"),

			-- Grep/Search
			map("<leader>bl", function()
				Snacks.picker.lines()
			end, "Buffer Lines"),
			map("<leader>bB", function()
				Snacks.picker.grep_buffers()
			end, "Grep Open Buffers"),
			map("<leader>sw", function()
				Snacks.picker.grep_word()
			end, "Word Under Cursor or Visual", { mode = { "n", "x" } }),
			map("<leader>sC", function()
				Snacks.picker.commands()
			end, "All Commands"),
			map("<leader>sH", function()
				Snacks.picker.highlights()
			end, "Highlight Groups"),
			map("<leader>si", function()
				Snacks.picker.icons()
			end, "Icons"),
			map("<leader>sj", function()
				Snacks.picker.jumps()
			end, "Jumps"),
			map("<leader>sk", function()
				Snacks.picker.keymaps()
			end, "Keymaps"),
			map("<leader>sl", function()
				Snacks.picker.loclist()
			end, "Location List"),
			map("<leader>sm", function()
				Snacks.picker.marks()
			end, "Marks"),
			map("<leader>sM", function()
				Snacks.picker.man()
			end, "Man Pages"),
			map("<leader>sp", function()
				Snacks.picker.lazy()
			end, "Plugin Specs"),
			map("<leader>sq", function()
				Snacks.picker.qflist()
			end, "Quickfix List"),
			map("<leader>sR", function()
				Snacks.picker.resume()
			end, "Resume Last Picker"),
			map("<leader>su", function()
				Snacks.picker.undo()
			end, "Undo History"),
			map("<leader>sh", function()
				Snacks.picker.help()
			end, "Help Pages"),
			map("<leader>sS", function()
				Snacks.picker.lsp_workspace_symbols()
			end, "Workspace Symbols"),
			map("<leader>ss", function()
				Snacks.picker.lsp_symbols()
			end, "Document Symbols"),
			map("<leader>uC", function()
				Snacks.picker.colorschemes()
			end, "Colorschemes"),

			-- Toggle Zen, Scratch, Terminal
			map("<leader>bz", function()
				Snacks.zen()
			end, "Toggle Zen Mode"),
			map("<leader>bZ", function()
				Snacks.zen.zoom()
			end, "Toggle Zoom"),
			map("<leader>b.", function()
				Snacks.scratch()
			end, "Scratch Buffer"),
			map("<C-t>", function()
				Snacks.terminal()
			end, "Toggle Terminal"),

			map("<leader>bd", function()
				Snacks.bufdelete()
			end, "Delete Buffer"),
			map("<leader>bR", function()
				Snacks.rename.rename_file()
			end, "Rename File"),

			map("<leader>n", function()
				Snacks.picker.notifications()
			end, "Notification History"),

			map("<leader>un", function()
				Snacks.notifier.hide()
			end, "Dismiss Notifications"),
			map("<leader>bS", function()
				Snacks.scratch.select()
			end, "Select Scratch Buffer"),
			map("<leader>N", function()
				Snacks.win({
					file = vim.api.nvim_get_runtime_file("doc/news.txt", false)[1],
					width = 0.6,
					height = 0.6,
					wo = {
						spell = false,
						wrap = false,
						signcolumn = "yes",
						statuscolumn = " ",
						conceallevel = 3,
					},
				})
			end, "Neovim News"),
			map("]]", function()
				Snacks.words.jump(vim.v.count1)
			end, "Next Reference", { mode = { "n", "t" } }),
			map("[[", function()
				Snacks.words.jump(-vim.v.count1)
			end, "Previous Reference", { mode = { "n", "t" } }),
		}
	end)(),

	init = function()
		require("snacks")
		vim.api.nvim_create_autocmd("User", {
			pattern = "VeryLazy",
			callback = function()
				-- Snacks debug globals
				_G.dd = function(...)
					Snacks.debug.inspect(...)
				end
				_G.bt = function()
					Snacks.debug.backtrace()
				end
				vim.print = _G.dd

				-- Toggles
				Snacks.toggle.option("spell", { name = "Spelling" }):map("<leader>us")
				Snacks.toggle.option("wrap", { name = "Wrap" }):map("<leader>uw")
				Snacks.toggle.option("relativenumber", { name = "Relative Number" }):map("<leader>uL")
				Snacks.toggle.diagnostics():map("<leader>ud")
				Snacks.toggle.line_number():map("<leader>ul")
				Snacks.toggle
					.option("conceallevel", { off = 0, on = vim.o.conceallevel > 0 and vim.o.conceallevel or 2 })
					:map("<leader>uc")
				Snacks.toggle.treesitter():map("<leader>uT")
				Snacks.toggle
					.option("background", { off = "light", on = "dark", name = "Dark Background" })
					:map("<leader>ub")
				Snacks.toggle.inlay_hints():map("<leader>uh")
				Snacks.toggle.indent():map("<leader>ug")
				Snacks.toggle.dim():map("<leader>uD")
			end,
		})
	end,
}
