---@diagnostic disable: undefined-global

return {

	-- Mason (Core)
	{
		"williamboman/mason.nvim",
		cmd = { "Mason", "MasonInstall", "MasonUpdate", "MasonUninstall", "MasonLog" },
		opts = {
			ui = {
				border = "rounded",
				icons = {
					package_installed = "",
					package_pending = "",
					package_uninstalled = "",
				},
			},
		},
	},

	-- Bridge Mason ↔ LSPConfig
	{
		"williamboman/mason-lspconfig.nvim",
		event = { "BufReadPre", "BufNewFile" },
		dependencies = { "williamboman/mason.nvim" },
		opts = {
			automatic_installation = true,
		},
	},

	-- Mason Tool Installer (LSPs, formatters, linters, DAPs)
	{
		"WhoIsSethDaniel/mason-tool-installer.nvim",
		cmd = { "MasonToolsInstall", "MasonToolsUpdate", "MasonToolsUninstall" },
		dependencies = { "williamboman/mason.nvim" },
		config = function()
			require("mason-tool-installer").setup({
				ensure_installed = {
					-- LSPs
					"clangd",
					"bashls",
					"pyright",
					"lua_ls",
					"ts_ls",
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

					-- Linters
					"eslint_d",
					"shellcheck",
					"jsonlint",
					"codespell",

					-- Debuggers
					-- "debugpy",
					-- "codelldb",
					-- "delve",
				},
				auto_update = true,
				run_on_start = true,
				start_delay = 2000,
				debounce_hours = 3,
				integrations = {
					["mason-lspconfig"] = true,
					["mason-nvim-dap"] = true,
				},
			})
		end,
	},

	-- LSP Configuration
	{
		"neovim/nvim-lspconfig",
		event = { "BufReadPre", "BufNewFile" },
		dependencies = { "williamboman/mason-lspconfig.nvim" },
		config = function()
			local lspconfig = require("lspconfig")

			-- Capabilities for autocompletion
			local capabilities = vim.lsp.protocol.make_client_capabilities()
			local ok_cmp, cmp_lsp = pcall(require, "cmp_nvim_lsp")
			if ok_cmp then
				capabilities = cmp_lsp.default_capabilities(capabilities)
			end

			-- Modern diagnostic UI
			vim.diagnostic.config({
				virtual_text = { spacing = 4, prefix = "●" },
				underline = true,
				severity_sort = true,
				update_in_insert = false,
				float = { border = "rounded", source = "always" },
				signs = true,
			})

			-- Disable legacy providers to improve startup
			for _, provider in ipairs({ "node", "perl", "python", "ruby" }) do
				vim.g["loaded_" .. provider .. "_provider"] = 0
			end

			-- Attach behaviour
			local function on_attach(client, bufnr)
				local ok_navic, navic = pcall(require, "nvim-navic")
				if ok_navic and client.server_capabilities.documentSymbolProvider then
					navic.attach(client, bufnr)
				end

				-- Disable inbuilt formatting to delegate to null-ls/formatters
				client.server_capabilities.documentFormattingProvider = false
				client.server_capabilities.documentRangeFormattingProvider = false

				vim.notify("LSP Attached: " .. client.name, vim.log.levels.INFO, { title = "LSP" })
			end

			-- Load Mason LSPs dynamically
			require("mason-lspconfig").setup({
				handlers = {
					function(server)
						lspconfig[server].setup({
							on_attach = on_attach,
							capabilities = capabilities,
							flags = { debounce_text_changes = 150 },
						})
					end,

					-- Custom configs for specific servers
					["lua_ls"] = function()
						lspconfig.lua_ls.setup({
							on_attach = on_attach,
							capabilities = capabilities,
							settings = {
								Lua = {
									runtime = { version = "LuaJIT" },
									diagnostics = { globals = { "vim" } },
									workspace = { checkThirdParty = false },
									telemetry = { enable = false },
								},
							},
						})
					end,
				},
			})

			vim.lsp.set_log_level("off")
		end,
	},
}
