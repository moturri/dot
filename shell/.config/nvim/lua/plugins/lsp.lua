---@diagnostic disable: undefined-global

return {
	-- Mason (Core)
	{
		"williamboman/mason.nvim",
		cmd = { "Mason", "MasonInstall", "MasonUpdate", "MasonUninstall", "MasonLog" },
		opts = {
			ui = { border = "rounded" },
		},
	},

	-- Mason ↔ LSP bridge
	{
		"williamboman/mason-lspconfig.nvim",
		event = { "BufReadPre", "BufNewFile" },
		dependencies = { "williamboman/mason.nvim" },
		opts = {
			automatic_installation = true,
		},
	},

	-- Auto install LSPs, formatters, linters, debuggers
	{
		"WhoIsSethDaniel/mason-tool-installer.nvim",
		cmd = { "MasonToolsInstall", "MasonToolsUpdate", "MasonToolsUninstall" },
		dependencies = { "williamboman/mason.nvim" },
		config = function()
			require("mason-tool-installer").setup({
				ensure_installed = {
					-- LSPs
					"clangd",
					"tsserver",
					"bashls",
					"pyright",
					"lua_ls",
					"jsonls",
					"marksman",
					"taplo",
					"yamlls",

					-- Formatters
					"stylua",
					"black",
					"isort",
					"clang-format",
					"shfmt",
					"prettier",
					"cbfmt",

					-- Linters
					"eslint_d",
					"shellcheck",
					"jsonlint",
					"codespell",
				},
				automatic_installation = true,
				auto_update = true,
				run_on_start = true,
				start_delay = 3000,
				debounce_hours = 12,
				integrations = {
					["mason-lspconfig"] = true,
				},
			})
		end,
	},

	-- LSP setup
	{
		"neovim/nvim-lspconfig",
		event = { "BufReadPre", "BufNewFile" },
		config = function()
			local lspconfig = require("lspconfig")
			local capabilities = vim.lsp.protocol.make_client_capabilities()

			local ok_cmp, cmp_lsp = pcall(require, "cmp_nvim_lsp")
			if ok_cmp then
				capabilities = cmp_lsp.default_capabilities(capabilities)
			end

			vim.diagnostic.config({
				virtual_text = true,
				underline = true,
				severity_sort = true,
				update_in_insert = false,
				float = { border = "rounded" },
				signs = {
					text = {
						[vim.diagnostic.severity.ERROR] = "",
						[vim.diagnostic.severity.WARN] = "",
						[vim.diagnostic.severity.HINT] = "",
						[vim.diagnostic.severity.INFO] = "",
					},
				},
			})

			vim.lsp.set_log_level("off")

			local function on_attach(client, bufnr)
				local ok_navic, navic = pcall(require, "nvim-navic")
				if ok_navic and client.server_capabilities.documentSymbolProvider then
					navic.attach(client, bufnr)
				end

				client.server_capabilities.documentFormattingProvider = false
				client.server_capabilities.documentRangeFormattingProvider = false

				vim.notify("LSP attached: " .. client.name, vim.log.levels.INFO, { title = "LSP" })
			end

			for _, provider in ipairs({ "node", "perl", "python", "python3", "ruby" }) do
				vim.g["loaded_" .. provider .. "_provider"] = 0
			end

			local mason_lspconfig = require("mason-lspconfig")
			for _, server in ipairs(mason_lspconfig.get_installed_servers() or {}) do
				local ok, server_module = pcall(function()
					return lspconfig[server]
				end)
				if ok and server_module then
					server_module.setup({
						capabilities = capabilities,
						on_attach = on_attach,
					})
				end
			end
		end,
	},
}
