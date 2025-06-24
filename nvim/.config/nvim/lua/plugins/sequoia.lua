return {
	{
		"forest-nvim/sequoia.nvim",
		priority = 1000,
		lazy = false, -- Load immediately for correct highlight ordering
		config = function()
			local colorscheme = "sequoia-insomnia" -- or "sequoia-night"

			local ok = pcall(vim.cmd.colorscheme, colorscheme)
			if not ok then
				vim.notify("Sequoia colorscheme not found: " .. colorscheme, vim.log.levels.ERROR)
				return
			end

			-- Transparent background for relevant groups
			local transparent_groups = {
				"Normal",
				"NormalNC",
				"NormalFloat",
				"FloatBorder",
				"SignColumn",
				"VertSplit",
				"StatusLine",
				"StatusLineNC",
				"WinBar",
				"WinBarNC",
				"Pmenu",
				"PmenuSel",
				"TelescopeNormal",
				"TelescopeBorder",
			}

			for _, group in ipairs(transparent_groups) do
				vim.api.nvim_set_hl(0, group, { bg = "none", ctermbg = "none" })
			end

			-- Reset any plugin-set blending (e.g. cmp/telescope)
			vim.api.nvim_set_hl(0, "Pmenu", { blend = 0 })
			vim.api.nvim_set_hl(0, "PmenuSel", { blend = 0 })
		end,
	},
}
