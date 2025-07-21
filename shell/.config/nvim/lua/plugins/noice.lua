return({
	{
		"folke/noice.nvim",
		event = "VeryLazy",
		opts = function()
			local ok_util, noice_util = pcall(require, "noice.util")
			local open = ok_util and noice_util.open or function() end

			return {
				cmdline = {
					enabled = true,
					view = "cmdline_popup",
					format = {
						cmdline = { pattern = "^:", icon = "", lang = "vim" },
						search_down = { pattern = "^/", icon = " ", lang = "regex" },
						search_up = { pattern = "^%?", icon = " ", lang = "regex" },
						filter = { pattern = "^:%s*!", icon = "$", lang = "bash" },
						lua = {
							pattern = { "^:%s*lua%s+", "^:%s*lua%s*=%s*", "^:%s*=%s*" },
							icon = "",
							lang = "lua",
						},
						help = { pattern = "^:%s*he?l?p?%s+", icon = "󰋗" },
						input = { view = "cmdline_input", icon = "󰥻 " },
					},
				},

				messages = {
					enabled = true,
					view = "notify",
					view_error = "notify",
					view_warn = "notify",
					view_history = "messages",
					view_search = "virtualtext",
				},

				popupmenu = {
					enabled = true,
					backend = "nui",
					kind_icons = false,
				},

				redirect = {
					view = "popup",
					filter = { event = "msg_show" },
				},

				commands = {
					history = {
						view = "split",
						opts = { enter = true, format = "details" },
						filter = {
							any = {
								{ event = "notify" },
								{ error = true },
								{ warning = true },
								{ event = "msg_show", kind = { "" } },
								{ event = "lsp", kind = "message" },
							},
						},
					},
					last = {
						view = "popup",
						opts = { enter = true, format = "details" },
						filter = {
							any = {
								{ event = "notify" },
								{ error = true },
								{ warning = true },
								{ event = "msg_show", kind = { "" } },
								{ event = "lsp", kind = "message" },
							},
						},
						filter_opts = { count = 1 },
					},
					errors = {
						view = "popup",
						opts = { enter = true, format = "details" },
						filter = { error = true },
						filter_opts = { reverse = true },
					},
					all = {
						view = "split",
						opts = { enter = true, format = "details" },
						filter = {},
					},
				},

				notify = {
					enabled = true,
					background = "#0000000",
					view = "notify",
				},

				lsp = {
					progress = {
						enabled = true,
						format = "lsp_progress",
						format_done = "lsp_progress_done",
						throttle = 33,
						view = "mini",
					},
					override = {
						["vim.lsp.util.convert_input_to_markdown_lines"] = false,
						["vim.lsp.util.stylize_markdown"] = false,
						["cmp.entry.get_documentation"] = false,
					},
					hover = {
						enabled = true,
						view = nil,
						opts = {},
					},
					signature = {
						enabled = true,
						auto_open = {
							enabled = true,
							trigger = true,
							luasnip = true,
							throttle = 50,
						},
						view = nil,
						opts = {},
					},
					message = {
						enabled = true,
						view = "notify",
						opts = {},
					},
					documentation = {
						view = "hover",
						opts = {
							lang = "markdown",
							replace = true,
							render = "plain",
							format = { "{message}" },
							win_options = { concealcursor = "n", conceallevel = 3 },
						},
					},
				},

				markdown = {
					hover = {
						["|(%S-)|"] = vim.cmd.help,
						["%[.-%]%((%S-)%)"] = open,
					},
					highlights = {
						["|%S-|"] = "@text.reference",
						["@%S+"] = "@parameter",
						["^%s*(Parameters:)"] = "@text.title",
						["^%s*(Return:)"] = "@text.title",
						["^%s*(See also:)"] = "@text.title",
						["{%S-}"] = "@parameter",
					},
				},

				health = {
					checker = false, -- turn off health check if unnecessary
				},

				presets = {
					bottom_search = false,
					command_palette = false,
					long_message_to_split = false,
					inc_rename = false,
					lsp_doc_border = false,
				},

				throttle = 33, -- same as 1000 / 30

				views = {}, -- can be used to override individual view configs
				routes = {}, -- custom routing of messages
				status = {}, -- optional statusline integrations
				format = {}, -- formatting options
			}
		end,
		dependencies = {
			"MunifTanjim/nui.nvim",
			"rcarriga/nvim-notify",
		},
	},
})
