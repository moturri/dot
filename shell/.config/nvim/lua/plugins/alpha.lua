return {
	"goolord/alpha-nvim",
	event = "VimEnter",
	config = function()
		local ok, alpha = pcall(require, "alpha")
		if not ok then
			vim.notify("alpha-nvim failed to load", vim.log.levels.ERROR)
			return
		end

		local dashboard = require("alpha.themes.startify")

		dashboard.section.header.val = {
			[[                                                                    ]],
			[[       ████ ██████           █████      ██                   ]],
			[[      ███████████             █████                         ]],
			[[      █████████ ███████████████████ ███   ███████████  ]],
			[[     █████████  ███    █████████████ █████ ██████████████   ]],
			[[    █████████ ██████████ █████████ █████ █████ ████ █████   ]],
			[[  ███████████ ███    ███ █████████ █████ █████ ████ █████  ]],
			[[ ██████  █████████████████████ ████ █████ █████ ████ ██████ ]],
		}

		alpha.setup(dashboard.config)
	end,
}
