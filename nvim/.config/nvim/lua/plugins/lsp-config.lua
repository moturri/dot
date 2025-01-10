return {
	{
		"williamboman/mason.nvim",
		lazy = false,
		config = function()
			require("mason").setup()
		end,
	},

	{
		"williamboman/mason-lspconfig.nvim",
		lazy = false,
		opts = {
			automatic_installation = true,
		},
	},

	{
		"neovim/nvim-lspconfig",
		lazy = false,
		config = function()
			local mason_lspconfig = require("mason-lspconfig")
			local lspconfig = require("lspconfig")
			local capabilities = require("cmp_nvim_lsp").default_capabilities()

			local default_config = {
				capabilities = capabilities,
				on_attach = function(_, bufnr)
					local keymap = vim.keymap.set
					local opts = { noremap = true, silent = true, buffer = bufnr }
					keymap("n", "K", vim.lsp.buf.hover, opts)
					keymap("n", "<leader>gd", vim.lsp.buf.definition, opts)
					keymap("n", "<leader>gr", vim.lsp.buf.references, opts)
					keymap("n", "<leader>ca", vim.lsp.buf.code_action, opts)
					keymap("n", "<leader>rn", vim.lsp.buf.rename, opts)
					keymap("n", "[d", vim.diagnostic.goto_prev, opts)
					keymap("n", "]d", vim.diagnostic.goto_next, opts)
					keymap("n", "<leader>f", function()
						vim.lsp.buf.format({ async = true })
					end, opts)
				end,
			}

			mason_lspconfig.setup_handlers({
				function(server_name)
					lspconfig[server_name].setup(default_config)
				end,
				["lua_ls"] = function()
					lspconfig.lua_ls.setup(vim.tbl_deep_extend("force", default_config, {
						settings = {
							Lua = {
								runtime = {
									version = "LuaJIT",
									path = vim.split(package.path, ";"),
								},
								diagnostics = {
									globals = { "vim" },
								},
								workspace = {
									library = vim.api.nvim_get_runtime_file("", true),
									checkThirdParty = false,
								},
								telemetry = { enable = false },
							},
						},
					}))
				end,
			})
		end,
	},
}
